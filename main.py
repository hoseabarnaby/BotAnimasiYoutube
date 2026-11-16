import os
import json
import time
import argparse
from dotenv import load_dotenv

from script_generator import generate_script
from tts_engine import synthesize_scene_audio
from video_builder import render_scene_clip, concatenate_scene_clips
from cartoon_renderer import generate_thumbnail_image
from youtube_uploader import upload_to_youtube_shorts


def save_youtube_metadata_txt(work_dir: str, title: str, thumb_text: str, description: str, tags: list) -> str:
    """Menyimpan Judul, Deskripsi, dan Tag ke file .txt yang rapi agar mudah di-copy atau dicek."""
    meta_path = os.path.join(work_dir, "YOUTUBE_METADATA.txt")
    clean_tags = [t for t in tags if t.lower() not in ("shorts", "short", "#shorts")]
    tags_comma = ", ".join(clean_tags)
    tags_hash = " ".join([f"#{t.replace(' ', '')}" for t in clean_tags])

    content = (
        "========================================================\n"
        "📌 JUDUL YOUTUBE LONG VIDEO 16:9 (TITLE)\n"
        "========================================================\n"
        f"{title}\n\n"
        "========================================================\n"
        "🖼️ TEKS THUMBNAIL 16:9\n"
        "========================================================\n"
        f"{thumb_text}\n\n"
        "========================================================\n"
        "📝 DESKRIPSI YOUTUBE (DESCRIPTION)\n"
        "========================================================\n"
        f"{description}\n\n"
        f"{tags_hash}\n\n"
        "========================================================\n"
        "🏷️ TAGS YOUTUBE (COPY-PASTE KE KOLOM TAGS)\n"
        "========================================================\n"
        f"{tags_comma}\n"
    )
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(content)
    return meta_path


def create_cartoon_short(topic: str, language: str = "Indonesia", auto_upload: bool = False):
    load_dotenv()

    voice = os.getenv("TTS_VOICE", "id-ID-ArdiNeural")
    rate = os.getenv("TTS_RATE", "+5%")
    width = 1280
    height = 720
    fps = int(os.getenv("VIDEO_FPS", "24"))

    timestamp = int(time.time())
    work_dir = os.path.join("output", f"project_{timestamp}")
    os.makedirs(work_dir, exist_ok=True)

    print("=" * 65)
    print("🎬 AI STICKMAN LONG VIDEO 16:9 BOT (WIDESCREEN HD + THUMBNAIL)")
    print("=" * 65)

    # 1. Buat Skrip Cerita, Judul, Deskripsi, Tags & Storyboard via DeepSeek API
    storyboard = generate_script(topic=topic, language=language)
    storyboard_path = os.path.join(work_dir, "storyboard.json")
    with open(storyboard_path, "w", encoding="utf-8") as f:
        json.dump(storyboard, f, indent=2, ensure_ascii=False)

    title = storyboard.get("title", f"Fakta Menarik {topic}").replace("#Shorts", "").replace("#shorts", "").strip()
    thumb_text = storyboard.get("thumbnail_text", "FAKTA MENGEJUTKAN!")
    description = storyboard.get("description", "").replace("#Shorts", "").replace("#shorts", "")
    raw_tags = storyboard.get("tags", ["Animasi", "FaktaUnik", "Edukasi"])
    tags = [t for t in raw_tags if t.lower() not in ("shorts", "short", "#shorts")]
    scenes = storyboard.get("scenes", [])

    # Simpan Judul, Deskripsi, dan Tag ke file YOUTUBE_METADATA.txt
    meta_txt_path = save_youtube_metadata_txt(work_dir, title, thumb_text, description, tags)

    print(f"[+] Judul Video    : {title}")
    print(f"[+] Teks Thumbnail : {thumb_text}")
    print(f"[+] Total Adegan   : {len(scenes)} adegan")

    # 2. Loop setiap scene: Generate Suara (TTS) + Analisis Gelombang Suara + Render Animasi
    clip_paths = []
    temp_audios = []
    for idx, scene in enumerate(scenes, start=1):
        scene["scene_id"] = idx
        narration = scene.get("narration", "")
        print(f"\n--- Memproses Adegan {idx}/{len(scenes)} ---")
        print(f"    Narasi: \"{narration}\"")

        audio_mp3 = os.path.join(work_dir, f"tts_scene_{idx}.mp3")
        print("    [1/2] Membuat voiceover AI & membaca amplitudo suara untuk lip-sync...")
        tts_data = synthesize_scene_audio(
            text=narration,
            output_mp3=audio_mp3,
            voice=voice,
            rate=rate,
            fps=fps
        )
        temp_audios.append(audio_mp3)

        print(f"    [2/2] Merender animasi kartun 2D ({tts_data['duration']:.1f} detik)...")
        clip_mp4 = render_scene_clip(
            scene=scene,
            tts_data=tts_data,
            work_dir=work_dir,
            width=width,
            height=height,
            fps=fps
        )
        clip_paths.append(clip_mp4)

    # 3. Buat Gambar Thumbnail Otomatis
    print("\n[*] Membuat gambar Thumbnail YouTube otomatis (thumbnail.jpg)...")
    thumbnail_path = generate_thumbnail_image(storyboard, work_dir, width, height)

    # 4. Gabungkan semua adegan menjadi 1 video MP4 utuh & hapus potongan file sementara
    final_video_path = os.path.join(work_dir, "final_youtube_short.mp4")
    print("[*] Menggabungkan seluruh adegan menjadi 1 video utuh & merapikan file sementara...")
    concatenate_scene_clips(clip_paths, final_video_path, work_dir, cleanup_temp=True)

    # Bersihkan file mp3 dan gambar sementara agar folder output hanya berisi file penting
    for mp3_f in temp_audios:
        try:
            os.remove(mp3_f)
        except Exception:
            pass
    for idx in range(1, len(scenes) + 1):
        for prefix in ("bg_scene_", "ai_scene_"):
            bg_f = os.path.join(work_dir, f"{prefix}{idx}.jpg")
            try:
                if os.path.exists(bg_f):
                    os.remove(bg_f)
            except Exception:
                pass

    print("\n" + "=" * 65)
    print("✅ SEMUA BERHASIL DIBUAT! ISI FOLDER OUTPUT:")
    print(f"🎬 Video Utuh      : {os.path.abspath(final_video_path)}")
    print(f"🖼️ Thumbnail       : {os.path.abspath(thumbnail_path)}")
    print(f"📝 Judul/Desk/Tags : {os.path.abspath(meta_txt_path)}")
    print("=" * 65)

    # Tampilkan Judul, Deskripsi, dan Tag langsung di terminal
    print("\n📌 RINGKASAN METADATA YOUTUBE:")
    print(f"   • JUDUL     : {title}")
    print(f"   • THUMBNAIL : {thumb_text}")
    print(f"   • TAGS      : {', '.join(tags)}")

    # 5. Upload ke YouTube Shorts jika diminta
    if auto_upload:
        upload_to_youtube_shorts(
            video_path=final_video_path,
            thumbnail_path=thumbnail_path,
            title=title,
            description=description,
            tags=tags,
            privacy_status=os.getenv("YOUTUBE_PRIVACY", "public").strip() or "public"
        )

    return final_video_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bot Pembuat Animasi Kartun 2D YouTube Shorts V2")
    parser.add_argument(
        "--topic",
        type=str,
        default="Kenapa bajak laut memakai penutup mata? Ternyata bukan karena buta!",
        help="Topik atau ide cerita untuk dibuatkan video Shorts"
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="Indonesia",
        help="Bahasa skrip (Indonesia / English)"
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Otomatis upload ke YouTube Shorts setelah video selesai dibuat"
    )

    args = parser.parse_args()
    create_cartoon_short(topic=args.topic, language=args.lang, auto_upload=args.upload)
