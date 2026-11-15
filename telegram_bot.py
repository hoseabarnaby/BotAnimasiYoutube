import os
import json
import time
import argparse
import subprocess
import requests
from dotenv import load_dotenv

from main import create_cartoon_short

load_dotenv()

OFFSET_FILE = "telegram_last_update.txt"
_last_net_warning = 0.0


def tg_api(token, method, data=None, files=None, retries=3, timeout=(20, 300)):
    """Panggil Telegram API dengan retry otomatis. Mengembalikan dict JSON ({} jika gagal)."""
    global _last_net_warning
    url = f"https://api.telegram.org/bot{token}/{method}"
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            if files:
                for f in files.values():
                    f.seek(0)
            resp = requests.post(url, data=data, files=files, timeout=timeout)
            return resp.json()
        except Exception as e:
            last_err = e
            time.sleep(2 * attempt)
    # jangan spam log: tampilkan peringatan jaringan maksimal 1x per 60 detik
    if time.time() - _last_net_warning > 60:
        _last_net_warning = time.time()
        print(f"[!] Koneksi ke Telegram gagal ({method}): {last_err}")
        print("    Kemungkinan koneksi/ISP ke api.telegram.org tidak stabil. Coba: ganti DNS (1.1.1.1), "
              "pakai VPN, atau cek dengan: curl https://api.telegram.org")
    return {}


def send_text(token, chat_id, text):
    return tg_api(token, "sendMessage", data={"chat_id": chat_id, "text": text}, retries=4)


def _compress_for_telegram(video_path):
    """Buat versi video lebih kecil (540p) agar upload ke Telegram lebih stabil."""
    small = video_path.replace(".mp4", "_small.mp4")
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", video_path, "-vf", "scale=540:-2", "-c:v", "libx264", "-preset", "veryfast",
             "-crf", "30", "-c:a", "aac", "-b:a", "96k", small],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return small
    except Exception:
        return None


def _send_file(token, chat_id, method, field, path, caption):
    with open(path, "rb") as fh:
        res = tg_api(token, method, data={"chat_id": chat_id, "caption": caption[:1000]}, files={field: fh})
    return bool(res.get("ok"))


def send_video_and_assets(token, chat_id, work_dir):
    """Kirim video, thumbnail, dan metadata ke Telegram. Otomatis coba versi kecil jika gagal."""
    video_path = os.path.join(work_dir, "final_youtube_short.mp4")
    thumb_path = os.path.join(work_dir, "thumbnail.jpg")
    meta_path = os.path.join(work_dir, "YOUTUBE_METADATA.txt")
    storyboard_path = os.path.join(work_dir, "storyboard.json")

    title, tags_str = "Video YouTube Shorts", ""
    if os.path.exists(storyboard_path):
        with open(storyboard_path, "r", encoding="utf-8") as f:
            sb = json.load(f)
            title = sb.get("title", title)
            tags_str = ", ".join(sb.get("tags", []))
    caption = f"VIDEO SHORTS SELESAI!\n\nJudul: {title}\nTags: {tags_str[:150]}"

    if os.path.exists(video_path):
        ok = _send_file(token, chat_id, "sendVideo", "video", video_path, caption)
        if not ok:
            small = _compress_for_telegram(video_path)
            if small and os.path.exists(small):
                ok = _send_file(token, chat_id, "sendVideo", "video", small, caption + "\n(versi ringan)")
        if not ok:
            send_text(token, chat_id, f"Video sudah jadi tapi gagal terkirim ke Telegram (koneksi). "
                                      f"Ambil manual di: {video_path}")
    if os.path.exists(thumb_path):
        _send_file(token, chat_id, "sendPhoto", "photo", thumb_path, "Thumbnail YouTube Shorts")
    if os.path.exists(meta_path):
        _send_file(token, chat_id, "sendDocument", "document", meta_path, "Judul, Deskripsi & Tags lengkap")


def process_topic_from_telegram(token, chat_id, topic, auto_upload=True):
    send_text(token, chat_id,
              f"Pesanan diterima!\n\nTopik: \"{topic}\"\nSedang menulis skrip, mengisi suara, dan merender animasi. "
              f"Tunggu beberapa menit ya.")
    try:
        final_video = create_cartoon_short(topic=topic, language="Indonesia", auto_upload=auto_upload)
        send_video_and_assets(token, chat_id, os.path.dirname(final_video))
    except Exception as e:
        send_text(token, chat_id, f"Terjadi error saat membuat video: {e}")


def get_last_offset():
    if os.path.exists(OFFSET_FILE):
        try:
            with open(OFFSET_FILE, "r") as f:
                return int(f.read().strip())
        except Exception:
            pass
    return 0


def save_last_offset(offset):
    with open(OFFSET_FILE, "w") as f:
        f.write(str(offset))


def run_telegram_bot(check_once=False, auto_upload=True):
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token or token.startswith("123456"):
        print("[!] TELEGRAM_BOT_TOKEN belum diisi di file .env atau GitHub Secrets!")
        return

    print("Bot Telegram AI Cartoon Shorts aktif! Kirim topik cerita ke bot kamu.")
    offset = get_last_offset()

    while True:
        res = tg_api(token, "getUpdates", data={"offset": offset + 1, "timeout": 20 if not check_once else 1},
                     retries=1, timeout=(20, 60))
        if not res.get("ok"):
            if check_once:
                break
            time.sleep(8)  # jaringan bermasalah: tunggu, jangan spam
            continue

        updates = res.get("result", [])
        if check_once and not updates:
            print("[*] Tidak ada pesan topik baru di Telegram saat ini.")
            break

        for upd in updates:
            offset = upd["update_id"]
            save_last_offset(offset)
            msg = upd.get("message", {})
            chat_id = msg.get("chat", {}).get("id")
            text = (msg.get("text") or "").strip()
            if not chat_id or not text:
                continue

            if text.startswith("/start") or text.startswith("/help"):
                send_text(token, chat_id,
                          "Halo! Aku bot pembuat video animasi stickman YouTube Shorts.\n\n"
                          "Ketik topik cerita apa saja, contoh:\n"
                          "- Kenapa gurita punya 3 jantung?\n"
                          "- Perang paling singkat di dunia\n"
                          "- Kenapa pesawat bisa terbang?\n\n"
                          "Aku akan membuatkan video, thumbnail, judul, deskripsi, dan tags.")
            else:
                process_topic_from_telegram(token, chat_id, text, auto_upload=auto_upload)

        if check_once:
            break
        time.sleep(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telegram Bot Controller untuk AI Cartoon Shorts")
    parser.add_argument("--check-once", action="store_true", help="Cek pesan 1 kali lalu keluar (GitHub Actions)")
    parser.add_argument("--no-upload", action="store_true", help="Jangan auto-upload ke YouTube")
    args = parser.parse_args()
    run_telegram_bot(check_once=args.check_once, auto_upload=not args.no_upload)
