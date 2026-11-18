"""
Mesin Ilustrasi Sketsa Tinta & Pensil Kelas Atas (Persis gaya 'Asal Mula Bitcoin' - PESAN ABADI / WASIT TERPUSAT / TAHUN 2140):
1. Kepala Stickman punya bayangan sabit 3D abu-abu lembut (3D cel-shading), garis tinta rangkap (double sketchy ink),
   mata ekspresif, tangan berjari 4 yang hidup, dan ukuran besar (Medium / Close-Up Shot).
2. Adegan Interaktif & Naratif (Bukan 3 ikon emoji melayang!):
   - Mode 'monument_stone': Prasasti batu besar / monumen berarsir cross-hatching dengan ukiran teks/angka/tanggal dari narasi + kaca pembesar / siluet berjubah.
   - Mode 'central_referee': Karakter besar memakai baju garis-garis wasit meniup peluit oranye & memegang buku besar "$ CHECK", barisan stickman kecil mengantre di kiri, dan gedung megah bertuliskan label di kanan!
   - Mode 'crisis_ruins': Gedung bank/institusi retak berarsir tinta dengan grafik patah menembus tanah & puing-puing batu.
   - Mode 'mechanism_board': Meja kerja / papan arsitektur / brankas besi raksasa berantai dengan gembok emas & kode biner 0101.
   - Mode 'discovery_closeup': Stickman membungkuk takjub di depan objek utama yang bersinar di atas bukit batu berarsir.
"""
import math
import random
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from stick_core import G, W, H, GROUND_Y
from stick_props import get_prop, normalize_prop, set_sketch_mode
from stick_engine import prepare_scene

SS = 2
OUT_W, OUT_H = 1920, 1080
INK = "#161616"
SHADE_DARK = "#7a766e"
SHADE_MID = "#b5b0a6"
SHADE_LIGHT = "#d8d3c8"
ACCENT_ORANGE = "#f48c06"
ACCENT_GOLD = "#ffba08"

HAND_FONTS = [
    "C:/Windows/Fonts/comicbd.ttf", "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/trebucbd.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/humor-sans/Humor-Sans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
SKETCH_TEXT_FONTS = [
    "C:/Windows/Fonts/segoeprb.ttf", "C:/Windows/Fonts/comic.ttf", "C:/Windows/Fonts/inkfree.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/humor-sans/Humor-Sans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


@lru_cache(maxsize=64)
def load_font(kind, size):
    paths = HAND_FONTS if kind == "title" else SKETCH_TEXT_FONTS
    for p in paths:
        try:
            return ImageFont.truetype(p, max(10, int(size)))
        except Exception:
            continue
    return ImageFont.load_default()


_PAPER = {}


def make_paper(w=OUT_W, h=OUT_H):
    """Kertas krem dengan vignette dramatis di keempat sudut seperti di screenshot PESAN ABADI / TAHUN 2140."""
    key = (w, h)
    if key not in _PAPER:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        nx = (xx - w / 2) / (w / 2)
        ny = (yy - h / 2) / (h / 2)
        r = np.sqrt((nx * 0.95) ** 2 + (ny * 0.95) ** 2)
        vign = np.clip((r - 0.42) / 0.88, 0, 1) ** 1.85
        center_col = np.array([248, 245, 238], np.float32)
        edge_col = np.array([158, 153, 143], np.float32)
        arr = center_col[None, None, :] * (1 - vign[..., None]) + edge_col[None, None, :] * vign[..., None]
        grain = np.random.default_rng(11).normal(0, 2.2, (h, w, 1)).astype(np.float32)
        _PAPER[key] = Image.fromarray(np.clip(arr + grain, 0, 255).astype(np.uint8), "RGB")
    return _PAPER[key].copy()


def _hatch_rect(g, x1, y1, x2, y2, spacing=12, angle_deg=45, col=INK, w=2):
    """Menggambar arsiran garis pena (cross-hatching) di dalam area kotak untuk efek sketsa tangan asli."""
    step = max(6, int(spacing))
    if angle_deg == 45:
        for offset in range(int(x1 - (y2 - y1)), int(x2), step):
            sx1 = max(x1, offset)
            sy1 = y1 + (sx1 - offset)
            sx2 = min(x2, offset + (y2 - y1))
            sy2 = y1 + (sx2 - offset)
            if sx2 > sx1 and sy2 > sy1:
                g.line([(sx1, sy1), (sx2, sy2)], fill=col, w=w, caps=False)
    else:
        for y in range(int(y1), int(y2), step):
            g.line([(x1, y), (x2, y + 4)], fill=col, w=w, caps=False)


def _sketch_line(g, pts, col=INK, w=5, seed=1):
    """Garis tinta dengan goresan ganda tipis (double-stroke ink) agar terlihat seperti goresan pena ilustrator."""
    g.line(pts, fill=col, w=w)
    rng = random.Random(seed)
    pts2 = [(x + rng.uniform(-2.2, 2.2), y + rng.uniform(-2.2, 2.2)) for x, y in pts]
    g.line(pts2, fill=col, w=max(2, w * 0.45))


def _draw_hand_fingers(g, hx, hy, angle_deg=0, scale=1.0, face=1):
    """Menggambar telapak tangan stickman dengan 4 jari terbuka ekspresif seperti di screenshot TAHUN 2140."""
    base_r = 9 * scale
    g.ellipse(hx - base_r, hy - base_r, hx + base_r, hy + base_r, fill="#ffffff", outline=INK, w=4)
    for i, a_off in enumerate((-38, -12, 14, 40)):
        rad = math.radians(angle_deg + a_off * face)
        flen = (17 if i in (1, 2) else 14) * scale
        fx = hx + math.cos(rad) * (base_r + flen)
        fy = hy + math.sin(rad) * (base_r + flen)
        bx = hx + math.cos(rad) * (base_r * 0.7)
        by = hy + math.sin(rad) * (base_r * 0.7)
        g.line([(bx, by), (fx, fy)], fill=INK, w=4)


def draw_detailed_stickman(
    g, cx, ground_y, scale=1.0, pose="talk", emotion="shocked",
    costume="normal", hand_prop="none", face=1, seated=False
):
    """
    Menggambar Karakter Stickman Detail Tinggi persis referensi:
    - Kepala bulat putih dengan bayangan sabit 3D abu-abu di sisi belakang (cel-shaded crescent shadow)
    - Garis sketsa tinta rangkap (sketchy double ink outline)
    - Mata oval ekspresif + alis tebal + mulut ekspresif
    - Bisa memakai baju garis-garis wasit + peluit oranye, duduk di kursi memegang kaca pembesar,
      atau membungkuk kaget dengan jari tangan terbuka!
    """
    HR = 68 * scale
    lean_x = face * (24 * scale if pose in ("inspect", "lean", "point") else 0)
    head_cx = cx + lean_x
    hip_x = cx - face * 10 * scale
    hip_y = ground_y - (110 if seated else 145) * scale
    sh_x = cx + lean_x * 0.6
    sh_y = hip_y - 135 * scale
    head_cy = sh_y - HR + 4 * scale

    # 1. KURSI KAYU (Jika seated=True seperti di PESAN ABADI)
    if seated:
        ch_x = cx - face * 18 * scale
        seat_y = hip_y + 12 * scale
        # Sandaran & kaki kursi
        _sketch_line(g, [(ch_x - face * 38 * scale, seat_y - 115 * scale), (ch_x - face * 28 * scale, ground_y)], w=6, seed=11)
        _sketch_line(g, [(ch_x + face * 35 * scale, seat_y), (ch_x + face * 40 * scale, ground_y)], w=6, seed=12)
        g.poly([
            (ch_x - 45 * scale, seat_y - 8 * scale),
            (ch_x + 45 * scale, seat_y - 8 * scale),
            (ch_x + 38 * scale, seat_y + 12 * scale),
            (ch_x - 38 * scale, seat_y + 12 * scale)
        ], fill=SHADE_MID, outline=INK, w=5)

    # 2. KAKI STICKMAN
    for sgn in (-1, 1):
        if seated:
            knee_x = hip_x + face * (48 + sgn * 12) * scale
            knee_y = hip_y + 10 * scale
            foot_x = knee_x + sgn * 8 * scale
            foot_y = ground_y
        else:
            knee_x = hip_x + sgn * 26 * scale + face * 8 * scale
            knee_y = (hip_y + ground_y) / 2
            foot_x = hip_x + sgn * 38 * scale
            foot_y = ground_y
        _sketch_line(g, [(hip_x, hip_y), (knee_x, knee_y), (foot_x, foot_y)], w=9 * scale, seed=20 + sgn)
        _sketch_line(g, [(foot_x, foot_y), (foot_x + face * 24 * scale, foot_y)], w=8 * scale, seed=30 + sgn)

    # 3. BADAN (Garis stickman tebal ATAU Baju Garis-Garis Wasit seperti di WASIT TERPUSAT)
    if costume == "referee":
        tw = 52 * scale
        body_pts = [
            (sh_x - tw, sh_y + 8 * scale),
            (sh_x + tw, sh_y + 8 * scale),
            (hip_x + tw * 0.88, hip_y + 6 * scale),
            (hip_x - tw * 0.88, hip_y + 6 * scale)
        ]
        g.poly(body_pts, fill="#e8e4da", outline=INK, w=6)
        # Garis-garis vertikal baju wasit + arsiran
        for sx in np.linspace(-tw * 0.72, tw * 0.72, 6):
            g.line([(sh_x + sx, sh_y + 10 * scale), (hip_x + sx * 0.85, hip_y + 5 * scale)], fill=INK, w=5)
        # Kerah baju wasit
        g.poly([(sh_x - 22 * scale, sh_y + 8 * scale), (sh_x, sh_y + 38 * scale), (sh_x - 34 * scale, sh_y + 30 * scale)],
               fill="#ffffff", outline=INK, w=4)
        g.poly([(sh_x + 22 * scale, sh_y + 8 * scale), (sh_x, sh_y + 38 * scale), (sh_x + 34 * scale, sh_y + 30 * scale)],
               fill="#ffffff", outline=INK, w=4)
    else:
        _sketch_line(g, [(sh_x, sh_y), (hip_x, hip_y)], w=10 * scale, seed=40)

    # 4. LENGAN & TANGAN INTERAKTIF (Memegang Kaca Pembesar / Peluit / Buku / Jari Terbuka)
    if costume == "referee":
        # Tangan depan meniup peluit oranye di mulut
        whistle_x = head_cx + face * 26 * scale
        whistle_y = head_cy + 34 * scale
        elbow_f = (sh_x + face * 65 * scale, sh_y + 52 * scale)
        _sketch_line(g, [(sh_x + face * 42 * scale, sh_y + 18 * scale), elbow_f, (whistle_x, whistle_y + 8 * scale)], w=8 * scale, seed=51)
        # Peluit oranye menyala + hembusan angin
        g.rrect(whistle_x - 16 * scale, whistle_y - 12 * scale, whistle_x + 16 * scale, whistle_y + 10 * scale,
                r=6 * scale, fill=ACCENT_ORANGE, outline=INK, w=4)
        for p_i in range(3):
            ang = math.radians((-25 + p_i * 25) if face == 1 else (155 + p_i * 25))
            px1 = whistle_x + face * 24 * scale + math.cos(ang) * 10 * scale
            py1 = whistle_y - 4 * scale + math.sin(ang) * 10 * scale
            px2 = px1 + face * 22 * scale
            g.line([(px1, py1), (px2, py1 + (p_i - 1) * 8 * scale)], fill=INK, w=3)
    elif hand_prop == "magnifier":
        # Tangan depan mengangkat Kaca Pembesar (persis PESAN ABADI!)
        elbow_f = (sh_x + face * 48 * scale, sh_y + 56 * scale)
        hand_f = (sh_x + face * 105 * scale, sh_y + 15 * scale)
        _sketch_line(g, [(sh_x, sh_y + 15 * scale), elbow_f, hand_f], w=8 * scale, seed=52)
        g.ellipse(hand_f[0] - 10 * scale, hand_f[1] - 10 * scale, hand_f[0] + 10 * scale, hand_f[1] + 10 * scale,
                  fill="#ffffff", outline=INK, w=4)
        # Gagang & Lensa Kaca Pembesar
        lens_cx = hand_f[0] + face * 14 * scale
        lens_cy = hand_f[1] - 58 * scale
        g.line([(hand_f[0], hand_f[1] + 14 * scale), (lens_cx, lens_cy + 36 * scale)], fill=INK, w=9 * scale)
        g.ellipse(lens_cx - 22 * scale, lens_cy - 44 * scale, lens_cx + 22 * scale, lens_cy + 44 * scale,
                  fill="#e3dfd5", outline=INK, w=6)
        g.ellipse(lens_cx - 15 * scale, lens_cy - 35 * scale, lens_cx + 15 * scale, lens_cy + 35 * scale,
                  fill="#f7f4ec", outline=INK, w=3)
        # Tangan belakang bertumpu di pinggang/kursi
        elbow_b = (sh_x - face * 46 * scale, sh_y + 55 * scale)
        hand_b = (sh_x - face * 15 * scale, hip_y - 10 * scale)
        _sketch_line(g, [(sh_x, sh_y + 15 * scale), elbow_b, hand_b], w=8 * scale, seed=53)
    else:
        # Pose tangan ekspresif dengan 4 jari terbuka (persis TAHUN 2140!)
        elbow_f = (sh_x + face * 52 * scale, sh_y + 62 * scale)
        hand_f = (sh_x + face * 115 * scale, sh_y - 8 * scale if pose != "panic" else sh_y - 55 * scale)
        _sketch_line(g, [(sh_x, sh_y + 12 * scale), elbow_f, hand_f], w=8 * scale, seed=54)
        _draw_hand_fingers(g, hand_f[0], hand_f[1], angle_deg=-35 * face, scale=scale, face=face)

        elbow_b = (sh_x - face * 54 * scale, sh_y + 48 * scale)
        hand_b = (sh_x - face * 95 * scale, sh_y + 92 * scale)
        _sketch_line(g, [(sh_x, sh_y + 12 * scale), elbow_b, hand_b], w=8 * scale, seed=55)
        _draw_hand_fingers(g, hand_b[0], hand_b[1], angle_deg=120 * face, scale=scale * 0.9, face=-face)

    # 5. KEPALA BULAT PUTIH DENGAN BAYANGAN SABIT 3D (3D Crescent Shading)
    g.ellipse(head_cx - HR, head_cy - HR, head_cx + HR, head_cy + HR, fill="#dcd7cc", outline=None, w=0)
    # Timpa lingkaran putih yang sedikit digeser ke arah wajah sehingga terbentuk bayangan sabit 3D di belakang kepala!
    shift_s = face * 14 * scale
    g.ellipse(head_cx - HR + shift_s, head_cy - HR - 4 * scale,
              head_cx + HR + shift_s * 0.4, head_cy + HR - 2 * scale,
              fill="#fbf9f5", outline=None, w=0)
    # Garis tepi kepala tinta rangkap (double sketchy ink circle)
    g.ellipse(head_cx - HR, head_cy - HR, head_cx + HR, head_cy + HR, fill=None, outline=INK, w=7)
    g.ellipse(head_cx - HR - 2, head_cy - HR + 2, head_cx + HR + 2, head_cy + HR - 2, fill=None, outline=INK, w=3)

    # 6. MATA OVAL EKSPRESIF & ALIS
    ex_base = head_cx + face * 18 * scale
    ey = head_cy - 6 * scale
    for sgn in (-1, 1):
        ex = ex_base + sgn * 16 * scale
        ew, eh = 6.5 * scale, 10.5 * scale
        g.ellipse(ex - ew, ey - eh, ex + ew, ey + eh, fill=INK, outline=None, w=0)
        # Alis ekspresif
        if emotion == "angry" or costume == "referee":
            y1 = ey - (26 if sgn == -face else 16) * scale
            y2 = ey - (16 if sgn == -face else 26) * scale
            _sketch_line(g, [(ex - 12 * scale, y1), (ex + 12 * scale, y2)], w=5 * scale, seed=60 + sgn)
        else:
            g.arc(ex - 13 * scale, ey - 32 * scale, ex + 13 * scale, ey - 14 * scale, 195, 345, fill=INK, w=4 * scale)

    # 7. MULUT EKSPRESIF (Terbuka kaget dengan lidah/gigi sketsa)
    mx = head_cx + face * 18 * scale
    my = head_cy + 28 * scale
    if costume != "referee":
        if emotion in ("shocked", "neutral", "thinking"):
            mw, mh = 13 * scale, 16 * scale
            g.ellipse(mx - mw, my - mh * 0.5, mx + mw, my + mh, fill=INK, outline=INK, w=4)
            g.ellipse(mx - mw * 0.6, my + mh * 0.2, mx + mw * 0.6, my + mh * 0.85, fill="#d8d2c5", outline=None, w=0)
        elif emotion == "happy":
            g.arc(mx - 18 * scale, my - 12 * scale, mx + 18 * scale, my + 14 * scale, 10, 170, fill=INK, w=5)
        else:
            g.arc(mx - 16 * scale, my, mx + 16 * scale, my + 18 * scale, 195, 345, fill=INK, w=5)

    # Tanda seru "!" atau "?" besar tulisan spidol di samping atas kepala (tidak menabrak judul atas!)
    f_exc = load_font("title", int(54 * scale * g.s))
    mark_char = "!" if emotion in ("shocked", "angry") else ("?" if emotion == "thinking" else "!")
    g.d.text(g.P(head_cx - face * (HR + 28 * scale), head_cy - HR * 0.65), mark_char, font=f_exc, fill=INK, anchor="mm")


def _extract_scene_keywords(scene):
    """Mengekstrak tahun/angka penting dan kata-kata kunci dari narasi & judul bab untuk diukir di ilustrasi."""
    import re
    title = str(scene.get("title", "FAKTA UTAMA")).upper().strip()
    narration = str(scene.get("narration", ""))
    # Cari angka tahun atau angka besar di narasi
    nums = re.findall(r"\b\d{3,4}\b", narration)
    words = [w.upper() for w in re.findall(r"[A-Za-z]{4,}", narration)
             if w.lower() not in ("yang", "untuk", "dalam", "dengan", "karena", "adalah", "tidak", "mereka",
                                  "akan", "bisa", "pada", "dari", "atau", "saat", "ketika", "seperti", "hingga",
                                  "sudah", "lebih", "sangat", "hanya", "banyak", "semua", "menjadi", "sebuah")]
    year_str = nums[0] if nums else ""
    if not year_str:
        t_nums = re.findall(r"\b\d+\b", title)
        year_str = t_nums[0] if t_nums else ""
    key_lines = words[:4] if words else title.split()
    return title, year_str, key_lines


# =============================================================================
# 5 TEMPLATE KOMPOSISI ILUSTRASI SKETSA SINEMATIK (PERSIS SCREENSHOT REFERENSI!)
# =============================================================================
def _scene_template_monument_tablet(g, scene, idx, rng):
    """
    Template 1 (Persis Screenshot 'PESAN ABADI'):
    - Kiri: Monumen batu besar 3D terbuka dengan arsiran cross-hatching, ukiran teks dari narasi,
      highlight stabilo oranye pada baris pertama, siluet misterius berjubah menulis di samping batu,
      koran & brankas kecil di bawah batu, serta simbol rantai & kode 0101 di udara!
    - Kanan: Stickman duduk di kursi memegang Kaca Pembesar meneliti batu tersebut dengan tanda '!' di atas kepala.
    """
    title, year_str, key_lines = _extract_scene_keywords(scene)

    # 1. Monumen Batu Besar 3D di Sisi Kiri (x=130..530, y=185..660)
    st_pts = [(135, 675), (150, 250), (260, 235), (505, 265), (545, 675)]
    side_pts = [(135, 675), (150, 250), (235, 275), (215, 675)]
    g.poly(st_pts, fill="#d9d4c7", outline=INK, w=6)
    g.poly(side_pts, fill="#9e998e", outline=INK, w=5)
    _hatch_rect(g, 145, 270, 225, 650, spacing=11, angle_deg=45, col=INK, w=2)

    # Tutup batu yang terangkat di atasnya
    lid_pts = [(130, 255), (220, 155), (465, 195), (445, 240), (235, 210), (150, 275)]
    g.poly(lid_pts, fill="#b5b0a4", outline=INK, w=6)
    _hatch_rect(g, 160, 175, 420, 230, spacing=14, angle_deg=45, col=INK, w=2)

    # Highlight Stabilo Oranye pada baris pertama ukiran batu (persis "THE TIMES" di PESAN ABADI!)
    g.rrect(255, 292, 475, 338, r=12, fill="#f7a034", outline=None, w=0)

    # Ukiran Teks Tulisan Tangan di atas permukaan batu
    line1 = title[:14]
    line2 = year_str if year_str else (key_lines[0][:12] if key_lines else "FAKTA")
    line3 = key_lines[1][:12] if len(key_lines) > 1 else "RAHASIA"
    line4 = key_lines[2][:12] if len(key_lines) > 2 else "SISTEM"
    line5 = key_lines[3][:12] if len(key_lines) > 3 else "DUNIA"

    for i_ln, txt in enumerate((line1, line2, line3, line4, line5)):
        f_st = load_font("sketch", int((34 if i_ln == 0 else 30) * g.s))
        g.d.text(g.P(370, 315 + i_ln * 56), txt, font=f_st, fill=INK, anchor="mm",
                 stroke_width=int(1.2 * g.s), stroke_fill=INK)

    # Bintang kilau oranye kecil & ledakan garis di sudut batu
    for sx, sy in ((245, 285), (495, 610)):
        g.poly([(sx, sy - 18), (sx + 5, sy - 5), (sx + 18, sy), (sx + 5, sy + 5),
                (sx, sy + 18), (sx - 5, sy + 5), (sx - 18, sy), (sx - 5, sy - 5)],
               fill=ACCENT_GOLD, outline=INK, w=3)

    # Siluet berjubah misterius memegang pena di sebelah kanan batu (x=590, y=420)
    hx, hy = 600, 415
    g.poly([(hx - 35, hy + 120), (hx - 45, hy - 15), (hx - 15, hy - 85),
            (hx + 30, hy - 65), (hx + 55, hy + 20), (hx + 45, hy + 125)],
           fill="#7d7970", outline=None, w=0)
    # Tudung kepala gelap berarsir
    g.poly([(hx - 35, hy - 25), (hx - 10, hy - 80), (hx + 22, hy - 55), (hx + 5, hy - 5)],
           fill="#2b2a27", outline=INK, w=5)
    _hatch_rect(g, hx - 30, hy - 70, hx + 15, hy - 10, spacing=7, angle_deg=45, col="#ffffff", w=1.5)
    # Tangan siluet menulis dengan pena ke batu
    g.line([(hx - 20, hy + 15), (535, hy + 35), (510, hy + 25)], fill=INK, w=5)
    g.poly([(535, hy + 5), (498, hy + 42), (505, hy + 48), (542, hy + 11)], fill="#ffffff", outline=INK, w=3)

    # Simbol biner "0101" dan mata rantai sketsa di sekitar batu
    f_bin = load_font("sketch", int(26 * g.s))
    g.d.text(g.P(475, 180), "0101", font=f_bin, fill="#4a4843", anchor="mm")
    g.d.text(g.P(80, 395), "0101", font=f_bin, fill="#4a4843", anchor="mm")
    for cy_ch in (285, 495):
        g.rrect(68, cy_ch, 102, cy_ch + 20, r=8, fill=None, outline=INK, w=4)
        g.rrect(88, cy_ch - 14, 122, cy_ch + 6, r=8, fill=None, outline=INK, w=4)

    # Koran & Brankas kecil di kaki batu
    g.poly([(145, 675), (165, 585), (240, 600), (225, 675)], fill="#e6e1d6", outline=INK, w=4)
    g.rrect(565, 580, 645, 670, r=6, fill="#c4bfb4", outline=INK, w=5)
    g.ellipse(590, 605, 622, 637, fill="#e6e1d6", outline=INK, w=4)

    # 2. Karakter Stickman Duduk di Kursi Kanan Memegang Kaca Pembesar (x=925)
    draw_detailed_stickman(g, cx=930, ground_y=665, scale=1.18, pose="inspect", emotion="shocked",
                           costume="normal", hand_prop="magnifier", face=-1, seated=True)


def _scene_template_central_referee(g, scene, idx, rng):
    """
    Template 2 (Persis Screenshot 'WASIT TERPUSAT'):
    - Kiri Bawah: Barisan 5 stickman kecil mengantre sambil membawa koin, kertas tagihan, dan papan jalan.
    - Tengah: Stickman Utama Besar memakai baju garis-garis Wasit, meniup peluit oranye, dan memeluk buku spiral raksasa.
    - Kanan: Gedung klasik bertuliskan judul/institusi dengan pilar-pilar berarsir tinta & bayangan dalam.
    """
    title, year_str, key_lines = _extract_scene_keywords(scene)

    # 1. Gedung Megah Berpilar di Sisi Kanan (x=800..1220, y=65..670)
    bx1, bx2 = 815, 1215
    # Atap segitiga pediment
    g.poly([(bx1 - 25, 225), ((bx1 + bx2) / 2, 55), (bx2 + 25, 225)], fill="#e6e1d6", outline=INK, w=7)
    g.poly([(bx1 + 10, 212), ((bx1 + bx2) / 2, 82), (bx2 - 10, 212)], fill="#d4cfc3", outline=INK, w=4)
    # Lambang lingkaran di puncak atap
    cx_b = (bx1 + bx2) / 2
    g.ellipse(cx_b - 32, 115, cx_b + 32, 179, fill="#ffffff", outline=INK, w=5)
    f_emb = load_font("title", int(38 * g.s))
    g.d.text(g.P(cx_b, 147), "$", font=f_emb, fill=INK, anchor="mm")

    # Papan nama gedung ("BANK SENTRAL" / Kata Kunci)
    g.poly([(bx1 - 10, 225), (bx2 + 10, 195), (bx2 + 10, 265), (bx1 - 10, 295)], fill="#f5f2eb", outline=INK, w=6)
    f_bank = load_font("title", int(32 * g.s))
    b_label = key_lines[0][:14] if key_lines else "SISTEM PUSAT"
    g.d.text(g.P(cx_b, 245), b_label, font=f_bank, fill=INK, anchor="mm")

    # Badan gedung & 3 pilar besar berarsir vertikal
    g.rect(bx1 + 15, 275, bx2 - 15, 640, fill="#cfc9bc", outline=INK, w=5)
    # Pintu kayu ganda di tengah gedung
    g.rect(cx_b - 48, 460, cx_b + 48, 635, fill="#9e8c70", outline=INK, w=6)
    g.line([(cx_b, 460), (cx_b, 635)], fill=INK, w=5)
    for px in (bx1 + 38, cx_b - 95, bx2 - 55):
        g.rect(px - 22, 285, px + 22, 635, fill="#f0ece3", outline=INK, w=5)
        for lx in (-10, 0, 10):
            g.line([(px + lx, 295), (px + lx, 625)], fill="#7a766e", w=2, caps=False)
        g.rrect(px - 30, 272, px + 30, 292, r=6, fill="#e6e1d6", outline=INK, w=4)
        g.rrect(px - 28, 625, px + 28, 642, r=4, fill="#e6e1d6", outline=INK, w=4)
    # Tangga gedung
    g.rect(bx1 - 15, 640, bx2 + 15, 660, fill="#e6e1d6", outline=INK, w=5)
    g.rect(bx1 - 35, 660, bx2 + 35, 678, fill="#d4cfc3", outline=INK, w=5)

    # 2. Barisan 5 Stickman Kecil Mengantre di Kiri Bawah (x=75..410)
    for q_i in range(5):
        qx = 80 + q_i * 78
        q_sc = 0.34 + q_i * 0.045
        qy = 675
        q_hr = 52 * q_sc
        q_sh = qy - 140 * q_sc
        q_hc = q_sh - q_hr
        # Badan berarsir abu-abu
        g.poly([(qx - 22 * q_sc, q_sh), (qx + 22 * q_sc, q_sh), (qx + 28 * q_sc, qy), (qx - 28 * q_sc, qy)],
               fill="#b5aea0", outline=INK, w=4)
        g.ellipse(qx - q_hr, q_hc - q_hr, qx + q_hr, q_hc + q_hr, fill="#fbf9f5", outline=INK, w=5)
        g.ellipse(qx + 8 * q_sc, q_hc - 6 * q_sc, qx + 15 * q_sc, q_hc + 6 * q_sc, fill=INK, outline=None, w=0)
        g.ellipse(qx + 22 * q_sc, q_hc - 6 * q_sc, qx + 29 * q_sc, q_hc + 6 * q_sc, fill=INK, outline=None, w=0)
        if q_i == 4:
            # Stickman terdepan menyodorkan koin
            g.line([(qx + 18 * q_sc, q_sh + 20 * q_sc), (qx + 85 * q_sc, q_sh - 10 * q_sc)], fill=INK, w=5)
            g.ellipse(qx + 75 * q_sc, q_sh - 35 * q_sc, qx + 125 * q_sc, q_sh + 15 * q_sc,
                      fill="#d9d2c5", outline=INK, w=4)

    # 3. Karakter Stickman Utama Besar Berbaju Wasit di Tengah (x=600)
    draw_detailed_stickman(g, cx=595, ground_y=675, scale=1.25, pose="talk", emotion="angry",
                           costume="referee", hand_prop="none", face=-1, seated=False)

    # 4. Buku Catatan Spiral Raksasa di Tangan Kanan Wasit (x=660..845, y=360..660)
    bk_pts = [(720, 365), (860, 415), (785, 665), (650, 610)]
    g.poly(bk_pts, fill="#dfd9cc", outline=INK, w=7)
    # Ring kawat spiral di pinggir kiri buku
    for r_i in range(9):
        fr = (r_i + 0.5) / 9.0
        rx = 720 * (1 - fr) + 650 * fr
        ry = 365 * (1 - fr) + 610 * fr
        g.ellipse(rx - 12, ry - 7, rx + 8, ry + 7, fill=None, outline=INK, w=4)
    # Tulisan & stempel merah-oranye di sampul buku
    f_bk = load_font("sketch", int(34 * g.s))
    g.d.text(g.P(755, 505), "$ Check", font=f_bk, fill=INK, anchor="mm")
    g.ellipse(745, 575, 780, 610, fill="#e04f16", outline=INK, w=3)


def _scene_template_milestone_stone(g, scene, idx, rng):
    """
    Template 3 (Persis Screenshot 'TAHUN 2140'):
    - Ruang kertas krem yang luas & bersih (minimalis dramatis!)
    - Tengah: Karakter Stickman besar membungkuk kaget dengan jari tangan terbuka ekspresif.
    - Kanan: Batu prasasti kokoh berarsir tinta gelap dengan plakat angka/kata kunci & kilau emas kecil.
    """
    title, year_str, key_lines = _extract_scene_keywords(scene)
    placa_txt = year_str if year_str else (key_lines[0][:8] if key_lines else title[:8])

    # 1. Batu Prasasti Berarsir Gelap di Kanan (x=800..1130, y=380..680)
    st_pts = [(805, 685), (885, 420), (935, 385), (1055, 385), (1125, 435), (1085, 685)]
    g.poly(st_pts, fill="#8c7f6a", outline=INK, w=8)
    # Sisi dalam batu yang lebih terang
    in_pts = [(825, 685), (898, 432), (940, 402), (1035, 402), (1075, 440), (1030, 685)]
    g.poly(in_pts, fill="#a89b84", outline=INK, w=4)
    _hatch_rect(g, 1020, 430, 1110, 675, spacing=10, angle_deg=45, col=INK, w=2.5)

    # Plakat Ukiran di Dada Batu
    pl_pts = [(888, 535), (908, 455), (1065, 470), (1045, 555)]
    g.poly(pl_pts, fill="#cfc7b6", outline=INK, w=6)
    f_pl = load_font("title", int(58 * g.s))
    g.d.text(g.P(975, 505), placa_txt, font=f_pl, fill=INK, anchor="mm")

    # Kilau bintang emas kecil di dekat plakat
    for sx, sy in ((878, 422), (1005, 472)):
        g.poly([(sx, sy - 12), (sx + 4, sy - 4), (sx + 12, sy), (sx + 4, sy + 4),
                (sx, sy + 12), (sx - 4, sy + 4), (sx - 12, sy), (sx - 4, sy - 4)],
               fill=ACCENT_GOLD, outline=INK, w=2)

    # Bongkahan batu tebing putih berarsir di pojok kanan bawah
    rock_pts = [(1075, 685), (1185, 555), (1275, 540), (1275, 685)]
    g.poly(rock_pts, fill="#efece4", outline=INK, w=5)
    _hatch_rect(g, 1140, 570, 1260, 675, spacing=12, angle_deg=45, col=INK, w=2)

    # 2. Karakter Stickman Besar Membungkuk Kaget di Tengah-Kiri (x=680)
    draw_detailed_stickman(g, cx=670, ground_y=685, scale=1.35, pose="lean", emotion="shocked",
                           costume="normal", hand_prop="none", face=1, seated=False)


def _scene_template_vault_wall(g, scene, idx, rng):
    """
    Template 4 (Gaya 'TEMBOK MATEMATIKA' / 'KEBAL BOBOL' / 'BATAS MUTLAK' dari video referensi):
    - Tembok bata 3D perspektif ATAU Pintu Brankas Besi Bulat Raksasa yang diikat rantai & gembok emas
    - Stickman berusaha mendorong/menyandar sambil menunjuk objek utama.
    """
    title, year_str, key_lines = _extract_scene_keywords(scene)
    vis = prepare_scene(scene, idx)

    if idx % 2 == 0:
        # Pintu Brankas Besi Bulat Raksasa Berantai (KEBAL BOBOL)
        vx, vy, vr = 890, 485, 165
        g.ellipse(vx - vr, vy - vr, vx + vr, vy + vr, fill="#8a8170", outline=INK, w=8)
        g.ellipse(vx - vr * 0.82, vy - vr * 0.82, vx + vr * 0.82, vy + vr * 0.82, fill="#a39987", outline=INK, w=5)
        _hatch_rect(g, vx - vr * 0.7, vy - vr * 0.7, vx + vr * 0.7, vy + vr * 0.7, spacing=14, angle_deg=45, col=INK, w=2)
        # Palang besi & rantai menyilang
        g.line([(vx - vr, vy), (vx + vr, vy)], fill=INK, w=12)
        g.line([(vx, vy - vr), (vx, vy + vr)], fill=INK, w=12)
        # Gembok Emas Menyala di Tengah Brankas
        g.arc(vx - 26, vy - 48, vx + 26, vy + 4, 180, 360, fill=INK, w=8)
        g.rrect(vx - 38, vy - 12, vx + 38, vy + 52, r=10, fill=ACCENT_GOLD, outline=INK, w=6)
        f_lk = load_font("title", int(34 * g.s))
        g.d.text(g.P(vx, vy + 20), "$", font=f_lk, fill=INK, anchor="mm")
        draw_detailed_stickman(g, cx=580, ground_y=665, scale=1.22, pose="point", emotion="happy",
                               costume="normal", hand_prop="none", face=1, seated=False)
    else:
        # Tembok Bata 3D Perspektif Raksasa (TEMBOK MATEMATIKA)
        w_pts = [(760, 650), (760, 260), (1080, 175), (1080, 590)]
        side_pts = [(1080, 175), (1145, 195), (1145, 610), (1080, 590)]
        g.poly(w_pts, fill="#b0a798", outline=INK, w=7)
        g.poly(side_pts, fill="#7d7567", outline=INK, w=6)
        _hatch_rect(g, 780, 240, 1070, 620, spacing=16, angle_deg=45, col=INK, w=2)
        for row_y in range(250, 610, 48):
            g.line([(765, row_y), (1075, row_y - 60)], fill=INK, w=3, caps=False)
        # Tanda silang merah/oranye di tembok
        g.line([(890, 380), (945, 435)], fill="#d9381e", w=9)
        g.line([(945, 380), (890, 435)], fill="#d9381e", w=9)
        draw_detailed_stickman(g, cx=540, ground_y=665, scale=1.22, pose="panic", emotion="angry",
                               costume="normal", hand_prop="none", face=1, seated=False)


def _scene_template_action_spotlight(g, g_acc, scene, idx, rng):
    """
    Template 5 (Komposisi Storyboard Dinamis dengan Objek Spesifik Topik):
    - Menggambar objek utama dari `props` ukuran besar dengan efek arsiran sketsa & stabilo emas,
      disertai label teks tulisan tangan & karakter Stickman 3D besar yang berinteraksi langsung.
    """
    title, year_str, key_lines = _extract_scene_keywords(scene)
    vis = prepare_scene(scene, idx)
    mirror = (idx % 2 == 0)

    # Gambar batu pijakan & rumput sketsa di lantai
    for rx in (180, 640, 1060):
        g.poly([(rx - 55, 665), (rx - 20, 630), (rx + 40, 640), (rx + 65, 665)],
               fill="#d8d2c5", outline=INK, w=4)
    g.line([(60, 665), (1220, 665)], fill=INK, w=5)

    # Gambar properti adegan dengan ukuran besar & detail sketsa
    try:
        for i, (name, (x, y, size)) in enumerate(vis["placed"][:3]):
            gx = (W - x if mirror else x)
            func, kind = get_prop(name)
            if i == 0:
                set_sketch_mode(True, True)
                py = 655 if kind == "ground" else 420
                func(g_acc, gx, py, size * 1.35, 1.9)
                # Lingkaran garis sinar sketsa di sekeliling objek utama
                cy_c = py - (110 if kind == "ground" else 0)
                for r_i in range(10):
                    ang = math.radians(r_i * 36 + 15)
                    g.line([
                        (gx + 135 * math.cos(ang), cy_c + 135 * math.sin(ang)),
                        (gx + 168 * math.cos(ang), cy_c + 168 * math.sin(ang))
                    ], fill="#7a7468", w=3)
            else:
                set_sketch_mode(True, False)
                func(g, gx, y + 40, size * 0.95, 1.9)
    finally:
        set_sketch_mode(False)

    # Tambahkan teks catatan kecil tulisan tangan + panah melengkung menunjuk ke objek utama
    note_x = 980 if mirror else 280
    f_nt = load_font("sketch", int(28 * g.s))
    note_txt = (year_str + " " + (key_lines[0][:10] if key_lines else "")).strip() or title
    g.d.text(g.P(note_x, 255), note_txt, font=f_nt, fill=INK, anchor="mm")

    char_x = 920 if mirror else 360
    draw_detailed_stickman(
        g, cx=char_x, ground_y=665, scale=1.22,
        pose=vis["pose"], emotion=vis["emotion"],
        costume="normal", hand_prop="none", face=-1 if mirror else 1, seated=False
    )


def _scene_template_crumbling_crisis(g, g_acc, scene, idx, rng):
    """
    Template 6 (Gaya 'BANKRUT TOTAL' / Krisis):
    - Gedung raksasa retak & miring di kanan dengan panah grafik patah menembus tanah ("CRASH!")
    - Kotak kardus di kiri bawah + Stickman memegangi kepala panik dengan tanda '!!!'
    """
    title, year_str, key_lines = _extract_scene_keywords(scene)

    # Gedung retak di kanan
    bx1, bx2 = 720, 1140
    g.poly([(bx1 - 15, 290), ((bx1 + bx2) / 2, 175), (bx2 + 15, 290)], fill="#d8d2c5", outline=INK, w=6)
    g.rect(bx1, 290, bx2, 650, fill="#c4beb2", outline=INK, w=6)
    _hatch_rect(g, bx1 + 10, 300, bx2 - 10, 640, spacing=16, angle_deg=45, col=INK, w=2)
    # Retakan gedung tajam
    g.line([(920, 290), (895, 380), (935, 440), (885, 550)], fill=INK, w=6)
    # Panah Grafik Runtuh Menembus Tanah ("CRASH!")
    crash_pts = [(700, 380), (810, 440), (850, 415), (1020, 610)]
    g.line(crash_pts, fill="#d9381e", w=14)
    g.poly([(1045, 635), (985, 620), (1030, 575)], fill="#d9381e", outline=INK, w=5)
    f_cr = load_font("title", int(32 * g.s))
    g.d.text(g.P(845, 575), "CRASH!", font=f_cr, fill=INK, anchor="mm")

    # Kotak kardus di kiri bawah
    g.poly([(220, 665), (220, 595), (305, 595), (305, 665)], fill="#c9b99b", outline=INK, w=5)
    g.line([(220, 595), (195, 570)], fill=INK, w=4)
    g.line([(305, 595), (330, 570)], fill=INK, w=4)

    draw_detailed_stickman(g, cx=450, ground_y=665, scale=1.18, pose="panic", emotion="shocked",
                           costume="normal", hand_prop="none", face=1, seated=False)


def render_sketch_image(scene, idx=1, with_title=True):
    """
    Merender 1 Gambar Ilustrasi Sketsa Komik Dokumenter (1920x1080) dengan 6 template komposisi
    yang bergilir secara bervariasi (tidak mengulang template yang sama di adegan berurutan!).
    """
    rng = random.Random(2000 + idx)
    base = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    acc = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    gb = G(base, SS, 0, 0, lw=0.65)
    ga = G(acc, SS, 0, 0, lw=0.70)

    t_low = str(scene.get("title", "")).lower()
    slot = idx % 6
    if "wasit" in t_low or "pusat" in t_low or slot == 3:
        _scene_template_central_referee(gb, scene, idx, rng)
    elif "bankrut" in t_low or "runtuh" in t_low or "krisis" in t_low or slot == 2:
        _scene_template_crumbling_crisis(gb, ga, scene, idx, rng)
    elif "pesan" in t_low or "buku" in t_low or slot == 5:
        _scene_template_monument_tablet(gb, scene, idx, rng)
    elif "tahun" in t_low or "batas" in t_low or slot == 4:
        _scene_template_milestone_stone(gb, scene, idx, rng)
    elif "tembok" in t_low or "kebal" in t_low or slot == 0:
        _scene_template_vault_wall(gb, scene, idx, rng)
    else:
        _scene_template_action_spotlight(gb, ga, scene, idx, rng)

    layer = Image.alpha_composite(base, acc)

    # JUDUL BAB BESAR TULISAN SPIDOL TEBAL DI BAGIAN ATAS TENGAH (Persis PESAN ABADI / WASIT TERPUSAT / TAHUN 2140)
    title = str(scene.get("title", "")).strip().upper() if with_title else ""
    if title:
        d = ImageDraw.Draw(layer)
        t_size = 86 * SS
        while t_size > 40 * SS:
            if load_font("title", t_size).getlength(title) <= (W - 140) * SS:
                break
            t_size -= 4 * SS
        f_title = load_font("title", t_size)
        d.text((W * SS / 2, 82 * SS), title, font=f_title, fill="#0f0f0f",
               anchor="mm", stroke_width=int(2.2 * SS), stroke_fill="#0f0f0f")

    ink = layer.resize((OUT_W, OUT_H), Image.Resampling.LANCZOS)
    paper = make_paper().convert("RGBA")
    final_rgb = Image.alpha_composite(paper, ink).convert("RGB")
    return ImageEnhance.Contrast(final_rgb).enhance(1.06)


# Kompatibilitas import untuk modul lain
def wobble(img, amp=2.0, cell=30, seed=0):
    return img


def _ground_doodle(g, rng):
    g.line([(60, GROUND_Y + 85), (W - 60, GROUND_Y + 85)], fill=INK, w=5)


def _wash(layer):
    return layer


def _glow_layer(cx, cy, radius):
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(255, 200, 60, 145))
    return glow.filter(ImageFilter.GaussianBlur(radius * 0.35))


def draw_sketch_character(g, cx, ground, t, pose="talk", emotion="shocked", hat="none", face=1):
    draw_detailed_stickman(g, cx, ground + 45, scale=1.15, pose=pose, emotion=emotion, face=face)
