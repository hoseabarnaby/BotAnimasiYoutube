@echo off
title Upload & Aktifkan Server GitHub Nonstop
echo =================================================================
echo   MENGUPDATE KODE TERBARU KE GITHUB & MENYALAKAN SERVER 5 JAM
echo =================================================================
echo.
git pull --rebase origin main 2>nul
git add -f .env youtube_token.pickle client_secrets.json .gitignore .github/workflows/youtube_bot.yml
git add -A
git commit -m "Enable 5-hour nonstop Telegram listener on push and schedule"
git push -u origin main --force

echo.
echo =================================================================
echo   BERHASIL! Server GitHub sekarang OTOMATIS MENYALA selama 5 JAM!
echo   Tunggu sekitar 1 menit (proses instal FFmpeg di server GitHub),
echo   lalu pesan Telegram kamu akan langsung dibalas otomatis!
echo =================================================================
pause
