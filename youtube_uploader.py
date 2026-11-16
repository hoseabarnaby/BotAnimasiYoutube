import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_authenticated_service(client_secrets_file: str = "client_secrets.json"):
    """
    Login OAuth2 Google untuk mendapatkan akses resmi upload ke channel YouTube kamu.
    Mendukung:
    1. File lokal 'youtube_token.pickle' (untuk penggunaan di Laptop).
    2. Environment variable 'YOUTUBE_TOKEN_BASE64' (untuk penggunaan di Cloud / GitHub Actions tanpa browser!).
    """
    creds = None
    token_pickle = "youtube_token.pickle"

    # Cek apakah dijalankan di GitHub Actions menggunakan secret YOUTUBE_TOKEN_BASE64
    token_b64 = os.getenv("YOUTUBE_TOKEN_BASE64", "").strip()
    if token_b64 and not os.path.exists(token_pickle):
        try:
            with open(token_pickle, "wb") as f:
                f.write(base64.b64decode(token_b64))
        except Exception as e:
            print(f"[!] Gagal membaca YOUTUBE_TOKEN_BASE64: {e}")

    if os.path.exists(token_pickle):
        with open(token_pickle, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_pickle, "wb") as token:
                pickle.dump(creds, token)
        else:
            if not os.path.exists(client_secrets_file):
                print("\n" + "!" * 65)
                print("[!] PERHATIAN: File 'client_secrets.json' belum ada di folder ini.")
                print("    Video, Thumbnail, Judul, Deskripsi & Tag SUDAH JADI di folder output.")
                print("!" * 65 + "\n")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)

            with open(token_pickle, "wb") as token:
                pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)


def upload_to_youtube_shorts(
    video_path: str,
    thumbnail_path: str,
    title: str,
    description: str,
    tags: list,
    privacy_status: str = "public"
):
    """Mengunggah file MP4 beserta Thumbnail 16:9, Judul, Deskripsi, dan Tag ke YouTube."""
    youtube = get_authenticated_service()
    if youtube is None:
        return None

    title = title.replace("#Shorts", "").replace("#shorts", "").strip()

    print(f"\n[*] Mengunggah Long Video 16:9 ke YouTube...")
    print(f"    Judul : {title}")
    print(f"    Tags  : {', '.join(tags[:8])}")

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"    -> Progres Upload Video: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    print(f"[+] Video berhasil di-upload! Link: https://youtu.be/{video_id}")

    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            print("[*] Mengunggah Thumbnail custom ke YouTube...")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            ).execute()
            print("[+] Thumbnail berhasil dipasang!")
        except Exception as e:
            print(f"[!] Catatan Thumbnail: ({e})")

    return video_id
