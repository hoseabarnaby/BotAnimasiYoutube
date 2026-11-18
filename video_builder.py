import os
import math
import subprocess
from PIL import Image
from image_gen import get_scene_image
from cartoon_renderer import draw_word_subtitle


def _ease(p):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, p)))


def apply_camera_to_still(master_img, effect, progress, width, height):
    """
    Mengambil potongan 16:9 dari master ilustrasi (1920x1080) dengan gerakan kamera halus (Ken Burns)
    sehingga karakter di dalam gambar tidak bergerak-gerak sendiri (murni ilustrasi statis per adegan
    persis gaya 'Asal Mula Bitcoin'!).
    """
    mw, mh = master_img.size
    p = _ease(progress)

    if effect == "zoom_out":
        z = 1.07 - 0.06 * p
        shift_x = 0.0
    elif effect == "pan_left":
        z = 1.05
        shift_x = (0.5 - p) * 0.75
    elif effect == "pan_right":
        z = 1.05
        shift_x = (p - 0.5) * 0.75
    else:  # zoom_in
        z = 1.0 + 0.07 * p
        shift_x = 0.0

    cw, ch = int(mw / z), int(mh / z)
    max_dx = max(0, (mw - cw) // 2)
    x1 = int((mw - cw) // 2 + shift_x * max_dx)
    y1 = int((mh - ch) // 2)
    x1 = max(0, min(mw - cw, x1))
    y1 = max(0, min(mh - ch, y1))

    cropped = master_img.crop((x1, y1, x1 + cw, y1 + ch))
    return cropped.resize((width, height), Image.Resampling.BILINEAR)


def render_scene_clip(scene, tts_data, work_dir, width=1280, height=720, fps=24):
    """
    Merender 1 adegan bergaya 'Asal Mula Bitcoin' (Whiteboard Sketch Explainer):
    - 1 Gambar Ilustrasi Sketsa Tinta & Kertas Krem per adegan (karakter diam tidak goyang-goyang!)
    - Judul Bab Kapital di bagian atas gambar
    - Efek kamera halus + transisi crossfade antar adegan
    - Sangat cepat karena gambar adegan cukup di-render 1 kali di awal adegan!
    """
    scene_id = scene.get("scene_id", 1)
    camera_effect = scene.get("camera_effect", "zoom_in")
    narration = scene.get("narration", "")

    duration = tts_data["duration"]
    audio_path = tts_data["audio_path"]
    word_timings = tts_data["word_timings"]

    # 1. Buat 1 gambar ilustrasi sketsa utuh untuk adegan ini (1920x1080)
    master_img, src_name = get_scene_image(scene, scene_id, work_dir)

    output_clip = os.path.join(work_dir, f"clip_scene_{scene_id}.mp4")
    total_frames = max(1, int(duration * fps))

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{width}x{height}", "-pix_fmt", "rgb24", "-r", str(fps), "-i", "-",
        "-i", audio_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-shortest", output_clip,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    paper_fade_bg = Image.new("RGB", (width, height), (245, 241, 232))

    for f_idx in range(total_frames):
        t = f_idx / float(fps)
        progress = f_idx / float(max(1, total_frames - 1))

        frame = apply_camera_to_still(master_img, camera_effect, progress, width, height)

        # Transisi halus di awal adegan (4 frame pertama) seperti lembaran gambar berganti
        if f_idx < 4:
            frame = Image.blend(paper_fade_bg, frame, (f_idx + 1) / 5.0)

        active_word = ""
        for wt in word_timings:
            if wt["start"] <= t <= wt["end"]:
                active_word = wt["word"]
                break

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
        # Bersihkan file gambar scene sementara agar folder output hanya menyisakan video utuh & thumbnail
        for fn in os.listdir(work_dir):
            if fn.startswith("scene_") and fn.endswith(".jpg"):
                try:
                    os.remove(os.path.join(work_dir, fn))
                except Exception:
                    pass
    return output_final_mp4
