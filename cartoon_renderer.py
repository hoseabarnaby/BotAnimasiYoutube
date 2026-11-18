import os
import math
from PIL import Image, ImageDraw, ImageEnhance
from stick_core import get_font, W, H, S, G, K
from sketch_style import render_sketch_image, load_font, make_paper, wobble, _ground_doodle, _wash, _glow_layer, draw_sketch_character, SS, OUT_W, OUT_H, INK
from stick_props import get_prop, normalize_prop, set_sketch_mode
from stick_engine import prepare_scene
import random


def draw_word_subtitle(canvas, active_word, full_narration, current_time, word_timings):
    """
    Dalam gaya dokumenter "Asal Mula Bitcoin" (Whiteboard Sketch Explainer),
    layar bersih dari kotak subtitle bawah karena sudah ada JUDUL BAB besar di atas gambar.
    Jika user ingin mengaktifkan subtitle bawah, bisa set SHOW_SUBTITLES=true di .env.
    """
    if os.getenv("SHOW_SUBTITLES", "false").strip().lower() not in ("true", "1", "yes"):
        return
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

    font_size = 38
    font_sub = get_font(font_size)
    full_line = " ".join(cw["word"] for cw in chunk_words)
    bbox = draw.textbbox((0, 0), full_line, font=font_sub)
    total_w = bbox[2] - bbox[0]
    while total_w > (w - 140) and font_size > 24:
        font_size -= 3
        font_sub = get_font(font_size)
        bbox = draw.textbbox((0, 0), full_line, font=font_sub)
        total_w = bbox[2] - bbox[0]

    y_pos = int(h * 0.88)
    pad_x, pad_y = 24, 12
    box = [max(24, (w - total_w) // 2 - pad_x), y_pos - pad_y,
           min(w - 24, (w + total_w) // 2 + pad_x), y_pos + (bbox[3] - bbox[1]) + pad_y + 6]
    draw.rounded_rectangle(box, radius=14, fill=(24, 24, 24))
    draw.rounded_rectangle(box, radius=14, outline="#ffffff", width=2)

    cur_x = (w - total_w) // 2
    for i, cw in enumerate(chunk_words):
        word_text = cw["word"]
        fill_color = "#ffd166" if (chunk_start + i) == active_idx else "#ffffff"
        draw.text((cur_x, y_pos), word_text, font=font_sub, fill=fill_color)
        wb = draw.textbbox((0, 0), word_text + " ", font=font_sub)
        cur_x += (wb[2] - wb[0])


def generate_thumbnail_image(storyboard, work_dir, width=1280, height=720):
    """
    Membuat Thumbnail 16:9 (1280x720) PERSIS GAYA CONTOH 'ASAL MULA BITCOIN':
    - Kertas sketsa krem dengan vignette gelap dramatis di tepi luar
    - Judul tulisan tangan tebal kapital di bagian atas tengah ("ASAL MULA BITCOIN")
    - Karakter Stickman terkejut (mata melotot, mulut terbuka, tanda '?') menunjuk lurus ke arah objek utama
    - Di tengah-kanan: Objek Utama (misal Koin Emas / simbol topik) bersinar kuning keemasan dengan garis-garis sinar tangan
    - Di kanan belakang: Latar bangunan/elemen abu-abu sketsa (misal gedung BANK retak dicoret X) & siluet misterius di kiri!
    """
    scenes = storyboard.get("scenes", [])
    first_scene = dict(scenes[0]) if scenes else {}
    thumb_text = storyboard.get("thumbnail_text", storyboard.get("title", "ASAL MULA BITCOIN"))
    thumb_text = thumb_text.replace("#Shorts", "").strip().upper()

    base = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    acc = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    gb = G(base, SS, 0, 0, lw=0.55)
    ga = G(acc, SS, 0, 0, lw=0.60)
    rng = random.Random(2026)

    # 1. Garis tanah retak & bebatuan sketsa di bagian bawah
    _ground_doodle(gb, rng)
    # Tambah batu sketsa di pojok kiri bawah & kanan bawah
    gb.poly([(40, 585), (75, 515), (145, 535), (175, 595)], fill="#d8d2c5", outline=INK, w=5)
    gb.poly([(1060, 590), (1120, 520), (1210, 540), (1245, 595)], fill="#d8d2c5", outline=INK, w=5)

    # 2. Siluet berjubah misterius + tanda '?' di latar kiri belakang (persis thumbnail Asal Mula Bitcoin!)
    hood_x, hood_y = 225, 480
    gb.poly([(hood_x - 52, hood_y + 70), (hood_x - 36, hood_y - 35), (hood_x, hood_y - 78),
             (hood_x + 36, hood_y - 35), (hood_x + 52, hood_y + 70)], fill="#5c5954", outline=INK, w=5)
    gb.ellipse(hood_x - 18, hood_y - 52, hood_x + 18, hood_y - 12, fill="#1a1a1a", outline=INK, w=3)
    f_q = load_font("hand", 52 * SS)
    gb.d.text(gb.P(hood_x + 48, hood_y - 88), "?", font=f_q, fill=INK, anchor="mm")

    # 3. Gedung BANK retak di sisi kanan belakang dengan coretan X di atasnya
    set_sketch_mode(True, False)
    bank_fn, _ = get_prop("bank_building")
    bank_fn(gb, 1025, 545, 1.15, 1.5)
    # Coretan silang X tebal di bagian atap tulisan BANK + garis retakan dinding
    gb.line([(955, 345), (1095, 310)], fill=INK, w=7)
    gb.line([(955, 310), (1095, 345)], fill=INK, w=7)
    gb.line([(995, 390), (1010, 425), (998, 455), (1018, 490)], fill=INK, w=4)

    # 4. Objek Utama Bercahaya Emas di Tengah-Kanan (x=745, y=455) + Garis-Garis Pancaran Sinar
    raw_props = first_scene.get("props", ["🪙", "🍕"])
    if isinstance(raw_props, str):
        raw_props = [p for p in raw_props.split(",")]
    prop_names = []
    for p in raw_props:
        n = normalize_prop(p)
        if n and n not in prop_names:
            prop_names.append(n)
    if not prop_names:
        prop_names = ["coins"]

    focus_x, focus_y = 755, 445
    # Garis-garis sinar sketsa tangan di sekeliling objek utama
    for i in range(12):
        ang = math.radians(i * 30 + 10)
        r1, r2 = 105, 138
        gb.line([
            (focus_x + r1 * math.cos(ang), focus_y + r1 * math.sin(ang)),
            (focus_x + r2 * math.cos(ang), focus_y + r2 * math.sin(ang))
        ], fill="#8c7a5b", w=4)

    set_sketch_mode(True, True)
    main_fn, main_kind = get_prop(prop_names[0])
    if main_kind == "ground":
        main_fn(ga, focus_x, focus_y + 85, 1.15, 1.8)
    else:
        main_fn(ga, focus_x, focus_y, 1.25, 1.8)

    # Prop ke-2 kecil di bawah lantai (seperti potongan pizza di thumbnail referensi)
    if len(prop_names) >= 2:
        p2_fn, p2_kind = get_prop(prop_names[1])
        if p2_kind == "high":
            p2_fn(ga, 815, 595, 0.58, 1.8)
    set_sketch_mode(False)

    # 5. Karakter Stickman Utama Ukuran Besar di Kiri-Tengah (Menunjuk Lurus ke Objek Emas!)
    gc = G(base, SS * 1.28, 0, 0, lw=0.60)
    draw_sketch_character(gc, 435 / 1.28, 610 / 1.28, 0.9, pose="point", emotion="shocked", hat="none", face=1)

    # 6. Judul Besar Tulisan Spidol Tebal di Bagian Atas Tengah ("ASAL MULA BITCOIN")
    layer = Image.alpha_composite(_wash(base), acc)
    d = ImageDraw.Draw(layer)
    title_size = 86 * SS
    while title_size > 44 * SS:
        if load_font("hand", title_size).getlength(thumb_text) <= (W - 180) * SS:
            break
        title_size -= 4 * SS
    f_title = load_font("hand", title_size)
    d.text((W * SS / 2, 95 * SS), thumb_text, font=f_title, fill="#141414",
            anchor="mm", stroke_width=int(2.0 * SS), stroke_fill="#141414")

    ink = wobble(layer.resize((OUT_W, OUT_H), Image.Resampling.LANCZOS), amp=2.4, cell=30, seed=7)
    paper = make_paper().convert("RGBA")
    gl = _glow_layer(focus_x, focus_y, 165).resize((OUT_W, OUT_H), Image.Resampling.BILINEAR)
    paper = Image.alpha_composite(paper, gl)

    final_img = Image.alpha_composite(paper, ink).convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
    final_img = ImageEnhance.Contrast(final_img).enhance(1.08)

    thumb_path = os.path.join(work_dir, "thumbnail.jpg")
    final_img.save(thumb_path, quality=96)
    return thumb_path
