import os
from PIL import Image, ImageDraw
from stick_core import get_font, W, H
from stick_engine import prepare_scene, compose_frame


def draw_word_subtitle(canvas, active_word, full_narration, current_time, word_timings):
    """Subtitle karaoke per 3 kata (kata aktif berwarna kuning) di bagian bawah layar 9:16."""
    if not word_timings:
        return
    draw = ImageDraw.Draw(canvas)
    w, h = canvas.size

    active_idx = 0
    for i, wt in enumerate(word_timings):
        if wt["start"] <= current_time <= wt["end"] + 0.12:
            active_idx = i
            break
        if current_time > wt["end"]:
            active_idx = i

    chunk_size = 3
    chunk_start = (active_idx // chunk_size) * chunk_size
    chunk_words = word_timings[chunk_start:chunk_start + chunk_size]
    if not chunk_words:
        return

    font_size = 44
    font_sub = get_font(font_size)
    full_line = " ".join(cw["word"] for cw in chunk_words)
    bbox = draw.textbbox((0, 0), full_line, font=font_sub)
    total_w = bbox[2] - bbox[0]
    while total_w > (w - 80) and font_size > 26:
        font_size -= 3
        font_sub = get_font(font_size)
        bbox = draw.textbbox((0, 0), full_line, font=font_sub)
        total_w = bbox[2] - bbox[0]

    y_pos = int(h * 0.815)
    pad_x, pad_y = 24, 15
    box = [max(16, (w - total_w) // 2 - pad_x), y_pos - pad_y,
           min(w - 16, (w + total_w) // 2 + pad_x), y_pos + (bbox[3] - bbox[1]) + pad_y + 8]
    draw.rounded_rectangle(box, radius=18, fill=(18, 18, 24))
    draw.rounded_rectangle(box, radius=18, outline="#ffffff", width=3)

    cur_x = (w - total_w) // 2
    for i, cw in enumerate(chunk_words):
        word_text = cw["word"]
        fill_color = "#ffd166" if (chunk_start + i) == active_idx else "#ffffff"
        for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4)]:
            draw.text((cur_x + ox, y_pos + oy), word_text, font=font_sub, fill="#000000")
        draw.text((cur_x, y_pos), word_text, font=font_sub, fill=fill_color)
        wb = draw.textbbox((0, 0), word_text + " ", font=font_sub)
        cur_x += (wb[2] - wb[0])


def generate_thumbnail_image(storyboard, work_dir, width=720, height=1280):
    """Thumbnail 9:16: adegan pertama + banner judul besar."""
    scenes = storyboard.get("scenes", [])
    first_scene = scenes[0] if scenes else {}
    thumb_text = storyboard.get("thumbnail_text", storyboard.get("title", "FAKTA MENGEJUTKAN!"))
    thumb_text = thumb_text.replace("#Shorts", "").strip().upper()

    vis = prepare_scene(first_scene, 1)
    img = compose_frame(vis, 1.4, 0.7, True).convert("RGB")
    draw = ImageDraw.Draw(img)

    bx1, by1, bx2, by2 = 36, 60, W - 36, 270
    draw.rounded_rectangle([bx1 + 8, by1 + 8, bx2 + 8, by2 + 8], radius=22, fill="#111111")
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=22, fill="#ffd166", outline="#111111", width=6)

    words = thumb_text.split()
    lines = [" ".join(words[:len(words) // 2]), " ".join(words[len(words) // 2:])] if len(words) >= 3 else [thumb_text]
    font_thumb = get_font(54)
    cur_y = by1 + 30
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_thumb)
        lw, lh = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = (W - lw) // 2
        for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3)]:
            draw.text((tx + ox, cur_y + oy), line, font=font_thumb, fill="#000000")
        draw.text((tx, cur_y), line, font=font_thumb, fill="#ffffff")
        cur_y += lh + 22

    thumb_path = os.path.join(work_dir, "thumbnail.jpg")
    img.save(thumb_path, quality=95)
    return thumb_path
