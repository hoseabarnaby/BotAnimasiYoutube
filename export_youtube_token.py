import os
import base64
from youtube_uploader import get_authenticated_service

if __name__ == "__main__":
    print("=" * 65)
    print("🔑 SETUP LOGIN YOUTUBE & EXPORT TOKEN UNTUK GITHUB ACTIONS")
    print("=" * 65)
    service = get_authenticated_service("client_secrets.json")
    if service and os.path.exists("youtube_token.pickle"):
        with open("youtube_token.pickle", "rb") as f:
            b64_str = base64.b64encode(f.read()).decode("utf-8")
        with open("GITHUB_SECRET_YOUTUBE_TOKEN.txt", "w", encoding="utf-8") as out:
            out.write(b64_str)
        print("\n[+] LOGIN BERHASIL!")
        print("[+] Kode untuk GitHub Secret 'YOUTUBE_TOKEN_BASE64' sudah disimpan ke file:")
        print("    -> GITHUB_SECRET_YOUTUBE_TOKEN.txt")
        print("    Kamu tinggal copy isi file itu ke GitHub Settings -> Secrets -> Actions!")
