import os
import math
from PIL import Image, ImageDraw
from stick_core import get_font, W, H, S, G, K, RED, YEL, BLUE, draw_character, make_background
from stick_props import get_prop, normalize_prop
from stick_engine import prepare_scene, compose_frame


def draw_word_subtitle(canvas, active_word, full_narration, current_time, word_timings):
    """
    Subtitle Widescreen 16:9 Sinematik (5 kata per baris di bagian bawah tengah layar 1280x720)
    dengan highlight kuning emas pada kata yang sedang diucapkan.
    """
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

    chunk_size = 5
    chunk_start = (active_idx // chunk_size) * chunk_size
    chunk_words = word_timings[chunk_start:chunk_start + chunk_size]
    if not chunk_words:
        return

    font_size = 42
    font_sub = get_font(font_size)
    full_line = " ".join(cw["word"] for cw in chunk_words)
    bbox = draw.textbbox((0, 0), full_line, font=font_sub)
    total_w = bbox[2] - bbox[0]
    while total_w > (w - 140) and font_size > 26:
        font_size -= 3
        font_sub = get_font(font_size)
        bbox = draw.textbbox((0, 0), full_line, font=font_sub)
        total_w = bbox[2] - bbox[0]

    y_pos = int(h * 0.855)
    pad_x, pad_y = 28, 14
    box = [max(24, (w - total_w) // 2 - pad_x), y_pos - pad_y,
           min(w - 24, (w + total_w) // 2 + pad_x), y_pos + (bbox[3] - bbox[1]) + pad_y + 8]
    draw.rounded_rectangle(box, radius=18, fill=(15, 18, 28))
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


def generate_thumbnail_image(storyboard, work_dir, width=1280, height=720):
    """
    Membuat Thumbnail YouTube 16:9 (1280x720) Kelas Atas dengan CTR Tinggi (gaya The Paint Explainer / Kurzgesagt / MrBeast):
    - Latar belakang kontras tinggi dengan radial sunburst beams di belakang objek utama
    - Panel Kiri: Teks HOOK Raksasa (2-3 baris) dengan kotak badge merah/kuning miring + outline 3D tebal
    - Tengah: Karakter Stickman Close-Up Besar dengan ekspresi Shocked/Excited
    - Kanan: Objek Utama / Ikon Topik Raksasa + Panah Merah Clickbait yang menunjuk ke objek!
    """
    scenes = storyboard.get("scenes", [])
    first_scene = scenes[0] if scenes else {}
    thumb_text = storyboard.get("thumbnail_text", storyboard.get("title", "FAKTA MENGEJUTKAN!"))
    thumb_text = thumb_text.replace("#Shorts", "").strip().upper()

    # 1. Buat kanvas High-Res (2x supersampling) untuk Thumbnail 1280x720
    tw, th = 1280, 720
    bg_base = make_background(first_scene.get("setting", "city")).resize((tw, th), Image.Resampling.LANCZOS)

    # Gelapkan sedikit sisi kiri agar teks judul 100% menonjol dan mudah dibaca
    overlay = Image.new("RGBA", (tw * S, th * S), (0, 0, 0, 0))
    g = G(overlay, S, 0, 0)

    # Radial Sunburst Kuning/Putih di sisi kanan (pusat perhatian objek & karakter)
    burst_cx, burst_cy = 960, 360
    for i in range(16):
        ang1 = math.radians(i * 22.5)
        ang2 = math.radians(i * 22.5 + 10)
        r_len = 650
        pts = [
            (burst_cx, burst_cy),
            (burst_cx + r_len * math.cos(ang1), burst_cy + r_len * math.sin(ang1)),
            (burst_cx + r_len * math.cos(ang2), burst_cy + r_len * math.sin(ang2)),
        ]
        g.poly(pts, fill=(255, 240, 150, 55), outline=None, w=0)

    # Lingkaran Glow Kuning Terang di belakang Objek Utama (Kanan)
    g.ellipse(830, 140, 1210, 520, fill="#ffd166", outline=K, w=8)
    g.ellipse(855, 165, 1185, 495, fill="#fff3b0", outline=None, w=0)

    # 2. Gambar Objek Utama Ukuran Raksasa di Lingkaran Kanan
    raw_props = first_scene.get("props", [])
    if isinstance(raw_props, str):
        raw_props = [p for p in raw_props.split(",")]
    prop_names = []
    for p in raw_props:
        n = normalize_prop(p)
        if n and n not in prop_names:
            prop_names.append(n)
    if not prop_names:
        prop_names = ["question_marks"]

    main_prop = prop_names[0]
    p_func, p_kind = get_prop(main_prop)
    if p_kind == "ground":
        p_func(g, 1020, 470, 1.35, 1.8)
    elif p_kind == "high":
        p_func(g, 1020, 330, 1.65, 1.8)

    # Jika ada prop ke-2, taruh sebagai aksen di pojok kanan atas
    if len(prop_names) >= 2:
        p2_func, p2_kind = get_prop(prop_names[1])
        if p2_kind == "high":
            p2_func(g, 790, 145, 0.95, 1.5)

    # 3. Gambar Karakter Stickman Close-Up Besar (Ekspresi Shocked/Heboh) di Tengah
    char_layer = Image.new("RGBA", (500 * S, 600 * S), (0, 0, 0, 0))
    cg = G(char_layer, S, 0, 0)
    draw_character(
        cg, cx=250, ground=560, t=1.2, amp=0.85, speaking=True,
        pose="panic", emotion="shocked",
        hat=first_scene.get("hat", "none"), outfit=first_scene.get("outfit", "tshirt"), face=1
    )
    # Perbesar karakter 1.45x agar tampak close-up dramatis di thumbnail
    char_big = char_layer.resize((int(500 * S * 1.42), int(600 * S * 1.42)), Image.Resampling.LANCZOS)
    overlay.alpha_composite(char_big, (int(390 * S), int(40 * S)))

    # 4. Panel Teks HOOK Raksasa di Sisi Kiri (Gaya Thumbnail Viral)
    words = thumb_text.split()
    if len(words) >= 4:
        lines = [" ".join(words[:2]), " ".join(words[2:4]), " ".join(words[4:])]
        lines = [ln for ln in lines if ln.strip()]
    elif len(words) == 3:
        lines = [words[0], " ".join(words[1:])]
    elif len(words) == 2:
        lines = [words[0], words[1]]
    else:
        lines = [thumb_text]

    badge_colors = [("#e63946", "#ffffff"), ("#ffd166", "#111111"), ("#ffffff", "#111111")]
    base_y = 145 if len(lines) == 3 else 195
    for idx, line in enumerate(lines[:3]):
        bg_col, txt_col = badge_colors[idx % len(badge_colors)]
        f_sz = 68 if len(line) <= 10 else (56 if len(line) <= 14 else 46)
        box_w = min(560, max(280, int(len(line) * f_sz * 0.68) + 60))
        box_h = f_sz + 38
        bx1 = 48
        by1 = base_y + idx * (box_h + 22)
        bx2 = bx1 + box_w
        by2 = by1 + box_h

        # Bayangan 3D hitam keras di belakang kotak teks
        g.rrect(bx1 + 10, by1 + 10, bx2 + 10, by2 + 10, r=18, fill="#000000", outline=None, w=0)
        g.rrect(bx1, by1, bx2, by2, r=18, fill=bg_col, outline=K, w=7)
        g.text((bx1 + bx2) / 2, (by1 + by2) / 2, line, f_sz, fill=txt_col,
               stroke=4 if txt_col == "#ffffff" else 0, stroke_fill="#000000")

    # 5. Panah Merah Clickbait Melengkung dari Teks Menunjuk ke Lingkaran Objek!
    arrow_pts = [
        (260, 560), (420, 620), (740, 560), (810, 485),
        (775, 465), (875, 440), (855, 535), (828, 512),
        (745, 600), (410, 660), (245, 595)
    ]
    g.poly(arrow_pts, fill="#e63946", outline=K, w=6)

    # Bingkai tepi kuning-hitam tegas di sekeliling thumbnail agar mencolok di beranda YouTube
    g.rect(6, 6, tw - 6, th - 6, fill=None, outline="#ffd166", w=12)
    g.rect(14, 14, tw - 14, th - 14, fill=None, outline=K, w=5)

    small_overlay = overlay.reduce(S)
    final_thumb = bg_base.convert("RGBA")
    final_thumb.alpha_composite(small_overlay, (0, 0))
    final_rgb = final_thumb.convert("RGB")

    if (width, height) != (tw, th):
        final_rgb = final_rgb.resize((width, height), Image.Resampling.LANCZOS)

    thumb_path = os.path.join(work_dir, "thumbnail.jpg")
    final_rgb.save(thumb_path, quality=96)
    return thumb_path
