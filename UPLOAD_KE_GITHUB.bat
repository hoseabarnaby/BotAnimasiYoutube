@echo off
title Upload Bot ke GitHub Actions
echo =================================================================
echo   PERSIAPAN UPLOAD KE GITHUB ACTIONS (AMAN TANPA BOCOR API KEY)
echo =================================================================
echo.
echo [1/3] Mengekspor Token Login YouTube untuk GitHub Secrets...
python export_youtube_token.py

echo.
echo [2/3] Menyiapkan Git Repository lokal...
git init
git branch -M main
git add .
git commit -m "Initial commit: AI Cartoon Shorts Bot V3 (Stickman Explainer + Telegram)"

echo.
echo =================================================================
echo [3/3] Masukkan Link Repository GitHub Baru Kamu
echo       (Contoh: https://github.com/usernamekamu/youtube-shorts-bot.git)
echo =================================================================
set /p REPO_URL="Paste Link Repository GitHub di sini: "
if "%REPO_URL%"=="" (
    echo [!] Link belum diisi. Jalankan ulang file ini setelah membuat repository di GitHub.
    pause
    exit /b
)

git remote remove origin 2>nul
git remote add origin %REPO_URL%
echo.
echo [*] Mengunggah kode ke GitHub...
git push -u origin main

echo.
echo =================================================================
echo   BERHASIL DI-UPLOAD KE GITHUB!
echo   Sekarang tinggal masukkan 3 Secrets di GitHub:
echo   1. DEEPSEEK_API_KEY
echo   2. TELEGRAM_BOT_TOKEN
echo   3. YOUTUBE_TOKEN_BASE64 (Copy isi dari file GITHUB_SECRET_YOUTUBE_TOKEN.txt)
echo =================================================================
pause
