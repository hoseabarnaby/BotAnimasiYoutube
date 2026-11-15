@echo off
title Upload Semua Langsung ke Private GitHub
echo =================================================================
echo   MENGUNGGAH SEMUA FILE + .ENV + TOKEN YOUTUBE KE PRIVATE GITHUB
echo =================================================================
echo.
git add -f .env youtube_token.pickle client_secrets.json .gitignore .github/workflows/youtube_bot.yml
git add .
git commit -m "Include .env and YouTube token directly for Private Repo"
git push -u origin main

echo.
echo =================================================================
echo   SELESAI 100%! TIDAK PERLU ISI SECRETS LAGI!
echo   Langsung buka tab "Actions" di GitHub kamu lalu klik "Run workflow"!
echo =================================================================
pause
