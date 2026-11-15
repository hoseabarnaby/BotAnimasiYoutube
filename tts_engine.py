import os
import asyncio
import subprocess
import numpy as np
import edge_tts


async def _generate_scene_tts(text: str, voice: str, rate: str, audio_path: str):
    """Generate MP3 audio and extract word-level timing boundaries using edge-tts."""
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    word_timings = []

    with open(audio_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start_sec = chunk["offset"] / 10_000_000.0
                dur_sec = chunk["duration"] / 10_000_000.0
                word_timings.append({
                    "word": chunk["text"],
                    "start": start_sec,
                    "end": start_sec + dur_sec
                })

    return word_timings


def get_audio_duration(audio_path: str) -> float:
    """Dapatkan durasi file audio menggunakan ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception:
        return 5.0


def extract_mouth_envelope(audio_path: str, fps: int, duration: float) -> list:
    """
    Mengekstrak amplitudo (keras-lembutnya) suara asli dari file MP3 pada setiap frame video.
    Dengan ini, mulut karakter membuka dan menutup 100% PAS mengikuti suku kata & jeda napas suara TTS!
    """
    total_frames = max(1, int(duration * fps) + 5)
    sample_rate = 8000
    try:
        cmd = [
            "ffmpeg", "-v", "error",
            "-i", audio_path,
            "-f", "s16le",
            "-acodec", "pcm_s16le",
            "-ac", "1",
            "-ar", str(sample_rate),
            "-"
        ]
        res = subprocess.run(cmd, capture_output=True, check=True)
        samples = np.frombuffer(res.stdout, dtype=np.int16).astype(np.float32)
        if len(samples) == 0:
            return [0.0] * total_frames

        samples_per_frame = max(1, int(sample_rate / fps))
        raw_env = []
        for f in range(total_frames):
            start_i = f * samples_per_frame
            end_i = start_i + samples_per_frame
            chunk = samples[start_i:end_i]
            if len(chunk) == 0:
                raw_env.append(0.0)
            else:
                rms = float(np.sqrt(np.mean(chunk ** 2)))
                raw_env.append(rms)

        max_rms = max(raw_env) if raw_env else 1.0
        if max_rms < 10.0:
            max_rms = 1.0

        # Normalisasi 0.0 - 1.0 dengan noise gate (jeda napas = mulut tertutup rapat)
        norm_env = []
        for val in raw_env:
            v = val / (max_rms * 0.80)
            if v < 0.16:
                v = 0.0
            norm_env.append(min(1.0, v))

        # Smoothing antar frame agar gerakan mulut mulus dan tidak berkedip terlalu cepat
        smoothed = []
        for i in range(len(norm_env)):
            prev_v = norm_env[max(0, i - 1)]
            curr_v = norm_env[i]
            next_v = norm_env[min(len(norm_env) - 1, i + 1)]
            smoothed.append(prev_v * 0.25 + curr_v * 0.50 + next_v * 0.25)

        return smoothed
    except Exception:
        return [0.0] * total_frames


def build_natural_word_timings(text: str, total_duration: float, mouth_envelope: list, fps: int) -> list:
    """
    Membagi timing subtitle per kata secara proporsional mengikuti panjang huruf & jeda tanda baca,
    serta disinkronkan dengan detik pertama dan terakhir suara aktif.
    """
    words = text.split()
    if not words:
        return []

    # Cari kapan suara benar-benar mulai dan berhenti dari envelope audio
    start_offset = 0.08
    end_time = max(0.5, total_duration - 0.15)
    for idx, amp in enumerate(mouth_envelope):
        if amp > 0.1:
            start_offset = idx / float(fps)
            break
    for idx in range(len(mouth_envelope) - 1, -1, -1):
        if mouth_envelope[idx] > 0.1:
            end_time = min(total_duration, (idx + 2) / float(fps))
            break

    usable_dur = max(0.5, end_time - start_offset)

    # Bobot durasi per kata berdasarkan jumlah karakter + jeda koma/titik
    weights = []
    for w in words:
        base_w = max(2, len(w))
        if w.endswith((",", ";", ":")):
            base_w += 3.5
        elif w.endswith((".", "!", "?", "...")):
            base_w += 5.0
        weights.append(float(base_w))

    total_weight = sum(weights)
    timings = []
    cur_t = start_offset
    for w, weight in zip(words, weights):
        w_dur = (weight / total_weight) * usable_dur
        timings.append({
            "word": w,
            "start": cur_t,
            "end": cur_t + w_dur
        })
        cur_t += w_dur

    return timings


def synthesize_scene_audio(
    text: str,
    output_mp3: str,
    voice: str = "id-ID-ArdiNeural",
    rate: str = "+5%",
    fps: int = 24
) -> dict:
    """
    Membuat file MP3 untuk 1 scene, mengekstrak envelope amplitudo suara asli untuk auto lip-sync mulut,
    serta timing per kata untuk subtitle.
    """
    os.makedirs(os.path.dirname(output_mp3), exist_ok=True)
    word_timings = asyncio.run(_generate_scene_tts(text, voice, rate, output_mp3))
    duration = get_audio_duration(output_mp3)

    # Ekstrak gelombang amplitudo suara asli (agar mulut gerak pas mengikuti suku kata)
    mouth_envelope = extract_mouth_envelope(output_mp3, fps=fps, duration=duration)

    if not word_timings:
        word_timings = build_natural_word_timings(text, duration, mouth_envelope, fps)
    else:
        last_end = word_timings[-1]["end"] + 0.25
        if last_end > duration:
            duration = last_end

    return {
        "audio_path": output_mp3,
        "duration": duration,
        "word_timings": word_timings,
        "mouth_envelope": mouth_envelope
    }
