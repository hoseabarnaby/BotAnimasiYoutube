import os
import math
import subprocess
from PIL import Image
from stick_core import W, H
from stick_engine import prepare_scene, compose_frame
from cartoon_renderer import draw_word_subtitle


def _ease(p):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, p)))


def apply_camera(frame, effect, progress, width, height):
    """Gerakan kamera halus & kecil (supaya properti tidak terpotong)."""
    p = _ease(progress)
    if effect == "zoom_out":
        z = 1.05 - 0.05 * p
        shift = 0
    elif effect == "pan_left":
        z, shift = 1.05, (0.5 - p) * 0.8
    elif effect == "pan_right":
        z, shift = 1.05, (p - 0.5) * 0.8
    else:
        z, shift = 1.0 + 0.05 * p, 0
    cw, ch = int(W / z), int(H / z)
    x1 = int((W - cw) / 2 + shift * (W - cw) / 2)
    y1 = int((H - ch) / 2)
    out = frame.crop((x1, y1, x1 + cw, y1 + ch))
    if (cw, ch) != (width, height):
        out = out.resize((width, height), Image.Resampling.BILINEAR)
    return out


def render_scene_clip(scene, tts_data, work_dir, width=720, height=1280, fps=24):
    scene_id = scene.get("scene_id", 1)
    camera_effect = scene.get("camera_effect", "zoom_in")
    narration = scene.get("narration", "")

    duration = tts_data["duration"]
    audio_path = tts_data["audio_path"]
    word_timings = tts_data["word_timings"]
    envelope = tts_data.get("mouth_envelope", [])

    vis = prepare_scene(scene, scene_id)

    output_clip = os.path.join(work_dir, f"clip_scene_{scene_id}.mp4")
    total_frames = max(1, int(duration * fps))

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{width}x{height}", "-pix_fmt", "rgb24", "-r", str(fps), "-i", "-",
        "-i", audio_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-shortest", output_clip,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    for f_idx in range(total_frames):
        t = f_idx / float(fps)
        progress = f_idx / float(max(1, total_frames - 1))
        amp = envelope[f_idx] if f_idx < len(envelope) else 0.0
        speaking = amp > 0.12

        active_word = ""
        for wt in word_timings:
            if wt["start"] <= t <= wt["end"]:
                active_word = wt["word"]
                break

        frame = compose_frame(vis, t, amp, speaking)
        frame = apply_camera(frame, camera_effect, progress, width, height)

        if f_idx < 3:
            frame = Image.blend(Image.new("RGB", frame.size, (0, 0, 0)), frame, (f_idx + 1) / 4.0)

        draw_word_subtitle(frame, active_word, narration, t, word_timings)
        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait()
    return output_clip


def concatenate_scene_clips(clip_paths, output_final_mp4, work_dir, cleanup_temp=True):
    concat_list_path = os.path.join(work_dir, "concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for cp in clip_paths:
            f.write("file '" + os.path.abspath(cp).replace("\\", "/") + "'\n")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_path, "-c", "copy", output_final_mp4]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if cleanup_temp:
        for p in [concat_list_path] + list(clip_paths):
            try:
                os.remove(p)
            except Exception:
                pass
    return output_final_mp4
