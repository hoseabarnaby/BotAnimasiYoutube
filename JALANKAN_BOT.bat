@echo off
title AI Cartoon Shorts Bot V2
echo ========================================================
echo   AI CARTOON SHORTS BOT V2 (LIP-SYNC + THUMBNAIL + SEO)
echo ========================================================
echo.
set /p TOPIC="Masukkan topik cerita (atau tekan Enter untuk topik default): "
if "%TOPIC%"=="" set TOPIC=Kenapa bajak laut memakai penutup mata? Ternyata bukan karena buta!

echo.
echo [*] Memproses cerita: "%TOPIC%"
python main.py --topic "%TOPIC%" --upload

echo.
echo ========================================================
echo   SELESAI! Cek folder "output" untuk:
echo   1. final_youtube_short.mp4 (Video Utuh)
echo   2. thumbnail.jpg (Gambar Thumbnail)
echo   3. YOUTUBE_METADATA.txt (Judul, Deskripsi, dan Tags)
echo ========================================================
pause
