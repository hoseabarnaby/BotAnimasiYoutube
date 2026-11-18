import os
import re
import wave
import base64
import asyncio
import subprocess
import numpy as np
import requests
import edge_tts


def _format_expressive_text(text: str) -> str:
    """
    Memperbaiki ritme bacaan TTS agar intonasinya naik-turun alami seperti narator manusia:
    - Memberi jeda napas halus setelah kata hubung dramatis
    - Memastikan tanda baca ekspresif terbaca oleh mesin neural TTS
    """
    t = text.strip()
    # Pastikan kata pembuka dramatis punya jeda koma agar ada penekanan intonasi
    for word in ("Bayangkan", "Ternyata", "Masalahnya", "Anehnya", "Sayangnya", "Hasilnya", "Namun", "Padahal"):
        t = re.sub(rf"\b{word}\s+(?!,)", f"{word}, ", t)
    return t


def apply_studio_podcast_mastering(input_mp3: str):
    """
    Memproses audio voiceover dengan FFmpeg Studio Podcast Mastering:
    1. Equalizer Warm Bass (+4.5dB di 125Hz) -> menghilangkan suara tipis/cempreng AI, memberi bobot suara dada hangat.
    2. Presence Boost (+3dB di 3600Hz) -> membuat artikulasi vokal terdengar jernih dan dekat di telinga.
    3. Dynamic Audio Compressor (acompressor) -> membuat suara terdengar padat, bertenaga, dan berwibawa seperti podcaster.
    4. Loudness Normalization -> volume stabil dan lantang di YouTube.
    """
    temp_out = input_mp3.replace(".mp3", "_mastered.mp3")
    af_chain = (
        "equalizer=f=125:t=q:w=1.1:g=4.5,"
        "equalizer=f=280:t=q:w=1.5:g=-1.5,"
        "equalizer=f=3600:t=q:w=1.2:g=3.0,"
        "acompressor=threshold=-18dB:ratio=2.8:attack=15:release=180:makeup=3.5dB,"
        "alimiter=limit=0.95"
    )
    try:
        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-i", input_mp3,
            "-af", af_chain,
            "-ar", "44100",
            "-ac", "2",
            "-b:a", "192k",
            temp_out
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(temp_out) and os.path.getsize(temp_out) > 1000:
            os.replace(temp_out, input_mp3)
    except Exception:
        if os.path.exists(temp_out):
            try:
                os.remove(temp_out)
            except Exception:
                pass


def _try_gemini_human_tts(text: str, output_mp3: str) -> bool:
    """
    Jika GEMINI_API_KEY tersedia di .env, gunakan Gemini 2.5 Flash Native Audio TTS
    (Suara manusia super ekspresif & bergairah dengan gaya pencerita dokumenter).
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return False

    voice_name = os.getenv("GEMINI_TTS_VOICE", "Puck").strip()  # Puck / Charon / Kore / Fenrir
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={api_key}"
    prompt_text = (
        "Bacakan narasi dokumenter YouTube ini dengan suara manusia yang sangat menarik, "
        "antusias, hangat, berwibawa, dan penuh ekspresi (tidak datar): " + text
    )
    body = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {"voiceName": voice_name}
                }
            }
        }
    }
    try:
        r = requests.post(url, json=body, timeout=45)
        if r.status_code != 200:
            return False
        data = r.json()
        for cand in data.get("candidates", []):
            for part in cand.get("content", {}).get("parts", []):
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    pcm_bytes = base64.b64decode(inline["data"])
                    temp_wav = output_mp3.replace(".mp3", "_gem.wav")
                    with wave.open(temp_wav, "wb") as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(24000)
                        wf.writeframes(pcm_bytes)
                    subprocess.run(
                        ["ffmpeg", "-y", "-v", "error", "-i", temp_wav, "-ar", "44100", "-ac", "2", "-b:a", "192k", output_mp3],
                        check=True
                    )
                    try:
                        os.remove(temp_wav)
                    except Exception:
                        pass
                    return True
    except Exception:
        pass
    return False


def _try_elevenlabs_tts(text: str, output_mp3: str) -> bool:
    """Jika ELEVENLABS_API_KEY tersedia di .env, gunakan ElevenLabs Multilingual v2."""
    api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        return False
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB").strip()  # Adam / Custom voice
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    body = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.42, "similarity_boost": 0.80, "style": 0.55, "use_speaker_boost": True}
    }
    try:
        r = requests.post(url, json=body, headers=headers, timeout=45)
        if r.status_code == 200 and len(r.content) > 2000:
            with open(output_mp3, "wb") as f:
                f.write(r.content)
            return True
    except Exception:
        pass
    return False


async def _generate_scene_tts(text: str, voice: str, rate: str, pitch: str, audio_path: str):
    """Generate MP3 audio and extract word-level timing boundaries using edge-tts with expressive pitch & rate."""
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
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
    """Mengekstrak amplitudo suara dari file MP3 pada setiap frame video."""
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

        norm_env = []
        for val in raw_env:
            v = val / (max_rms * 0.80)
            if v < 0.16:
                v = 0.0
            norm_env.append(min(1.0, v))

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
    words = text.split()
    if not words:
        return []

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
    rate: str = "+12%",
    fps: int = 24
) -> dict:
    """
    Membuat voiceover untuk 1 adegan dengan kualitas Studio Podcast:
    - Otomatis memformat teks agar intonasi ekspresif & tidak datar
    - Mendukung Gemini Human TTS / ElevenLabs (jika API key diisi) atau Edge-TTS Neural dengan pitch & speed energik
    - Menerapkan Studio Podcast Mastering (Warm Bass EQ + Presence + Dynamic Compression)
    """
    os.makedirs(os.path.dirname(output_mp3), exist_ok=True)
    expressive_text = _format_expressive_text(text)
    pitch = os.getenv("TTS_PITCH", "-2Hz").strip()
    # Kecepatan +12% membuat suara jauh lebih bergairah, antusias, dan tidak mengantuk seperti robot
    if rate in ("+0%", "+5%", ""):
        rate = "+12%"

    word_timings = []
    used_human_api = _try_elevenlabs_tts(expressive_text, output_mp3) or _try_gemini_human_tts(expressive_text, output_mp3)

    if not used_human_api:
        word_timings = asyncio.run(_generate_scene_tts(expressive_text, voice, rate, pitch, output_mp3))

    # Terapkan Studio Podcast Audio Mastering agar suara hangat, nge-bass, dan bertenaga!
    apply_studio_podcast_mastering(output_mp3)

    duration = get_audio_duration(output_mp3)
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
