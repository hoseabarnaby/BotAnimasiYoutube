"""
Gaya 'Sketsa Explainer' (mirip video dokumenter animasi tipe The Paint Explainer / Asal Mula Bitcoin):
- kertas krem + vignette + butiran halus
- karakter stickman garis tipis (kepala bulat putih), bergaya digambar tangan (garis bergelombang)
- objek berwarna pudar (abu-abu hangat) dan HANYA objek utama yang berwarna (aksen kuning/oranye)
- judul bab tulisan tangan di bagian atas setiap gambar
Dipakai sebagai (1) generator gambar lokal gratis tanpa batas, dan (2) cadangan jika generator gambar AI gagal.
"""
import math
import random
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from stick_core import G, W, H, GROUND_Y, arm_angles, _limb, _draw_hat
from stick_props import get_prop, set_sketch_mode
from stick_engine import prepare_scene

SS = 3                      # supersampling lapisan tinta
OUT_W, OUT_H = 1920, 1080   # master gambar (ruang untuk gerakan kamera)
INK = "#262626"

HAND_FONTS = [
    "C:/Windows/Fonts/comicbd.ttf", "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/trebucbd.ttf",
    "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeprb.ttf",
    "/usr/share/fonts/truetype/humor-sans/Humor-Sans.ttf",
    "/usr/share/fonts/truetype/comic-neue/ComicNeue-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
BOLD_FONTS = [
    "C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/ariblk.ttf", "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


@lru_cache(maxsize=64)
def load_font(kind, size):
    for p in (HAND_FONTS if kind == "hand" else BOLD_FONTS):
        try:
            return ImageFont.truetype(p, int(size))
        except Exception:
            continue
    return ImageFont.load_default()


# ----------------------------------------------------------------------------- kertas & efek tangan
_PAPER = {}


def make_paper(w=OUT_W, h=OUT_H):
    key = (w, h)
    if key not in _PAPER:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        nx = (xx - w / 2) / (w / 2)
        ny = (yy - h / 2) / (h / 2)
        r = np.sqrt(nx ** 2 + (ny * 0.92) ** 2)
        vign = np.clip((r - 0.50) / 0.95, 0, 1) ** 1.7
        base = np.array([252, 249, 243], np.float32)
        edge = np.array([208, 204, 194], np.float32)
        arr = base[None, None, :] * (1 - vign[..., None]) + edge[None, None, :] * vign[..., None]
        grain = np.random.default_rng(3).normal(0, 2.4, (h, w, 1)).astype(np.float32)
        _PAPER[key] = Image.fromarray(np.clip(arr + grain, 0, 255).astype(np.uint8), "RGB")
    return _PAPER[key].copy()


def wobble(img, amp=2.6, cell=30, seed=0):
    """Menggeser garis sedikit bergelombang agar tampak digambar tangan."""
    w, h = img.size
    cols, rows = w // cell, h // cell
    rng = np.random.default_rng(seed)

    def field():
        n = rng.uniform(-amp, amp, (rows + 1, cols + 1))
        for _ in range(2):
            n = (n + np.roll(n, 1, 0) + np.roll(n, -1, 0) + np.roll(n, 1, 1) + np.roll(n, -1, 1)) / 5.0
        n[0, :] = n[-1, :] = 0
        n[:, 0] = n[:, -1] = 0
        return n

    dx, dy = field(), field()
    mesh = []
    for r in range(rows):
        for c in range(cols):
            x0, y0, x1, y1 = c * cell, r * cell, (c + 1) * cell, (r + 1) * cell
            quad = (x0 + dx[r, c], y0 + dy[r, c], x0 + dx[r + 1, c], y1 + dy[r + 1, c],
                    x1 + dx[r + 1, c + 1], y1 + dy[r + 1, c + 1], x1 + dx[r, c + 1], y0 + dy[r, c + 1])
            mesh.append(((x0, y0, x1, y1), quad))
    return img.transform(img.size, Image.MESH, mesh, Image.BICUBIC)


# ----------------------------------------------------------------------------- karakter sketsa
def draw_sketch_character(g, cx, ground, t, pose="talk", emotion="neutral", hat="none", face=1):
    HR = 50
    hip_y = ground - 105
    sh_y = hip_y - 100
    head_cy = sh_y - HR - 6

    for sgn in (-1, 1):
        knee = (cx + sgn * 14, hip_y + 52)
        foot = (cx + sgn * 26, ground)
        g.line([(cx, hip_y), knee, foot], fill=INK, w=8)
        g.line([foot, (foot[0] + face * 20, foot[1])], fill=INK, w=8)
    g.line([(cx, sh_y), (cx - face * 3, hip_y)], fill=INK, w=8)

    act, pas = arm_angles(pose, t, 0.0, False)
    angs = {1: act, -1: pas} if face == 1 else {1: pas, -1: act}
    for sgn in (-1, 1):
        sx, sy = cx, sh_y + 10
        a1, a2 = angs[sgn]
        e, h = _limb(sx, sy, sgn, a1, a2, l1=52, l2=48)
        g.line([(sx, sy), e, h], fill=INK, w=7)
        g.ellipse(h[0] - 7, h[1] - 7, h[0] + 7, h[1] + 7, fill="#ffffff", outline=INK, w=5)

    g.ellipse(cx - HR, head_cy - HR, cx + HR, head_cy + HR, fill="#ffffff", outline=INK, w=6)

    ex, ey = cx + face * 12, head_cy - 4
    for sgn in (-1, 1):
        x = ex + sgn * 17
        if emotion == "happy":
            g.arc(x - 8, ey - 6, x + 8, ey + 10, 200, 340, fill=INK, w=5)
        elif emotion == "shocked":
            g.ellipse(x - 9, ey - 10, x + 9, ey + 10, fill="#ffffff", outline=INK, w=4)
            g.ellipse(x - 2.5 + face * 2, ey - 2.5, x + 2.5 + face * 2, ey + 2.5, fill=INK, outline=None, w=0)
        else:
            g.ellipse(x - 4.5, ey - 5.5, x + 4.5, ey + 5.5, fill=INK, outline=None, w=0)
        if emotion == "sad":
            y1, y2 = (ey - 13, ey - 22) if sgn == -1 else (ey - 22, ey - 13)
            g.line([(x - 10, y1), (x + 10, y2)], fill=INK, w=4)
        elif emotion == "angry":
            y1, y2 = (ey - 24, ey - 13) if sgn == -1 else (ey - 13, ey - 24)
            g.line([(x - 10, y1), (x + 10, y2)], fill=INK, w=5)
        elif emotion == "shocked":
            g.arc(x - 11, ey - 32, x + 11, ey - 16, 200, 340, fill=INK, w=4)
        elif emotion == "thinking":
            if sgn == 1:
                g.arc(x - 11, ey - 32, x + 11, ey - 16, 200, 340, fill=INK, w=4)
            else:
                g.line([(x - 10, ey - 20), (x + 10, ey - 20)], fill=INK, w=4)
        elif emotion == "neutral":
            g.line([(x - 9, ey - 19), (x + 9, ey - 19)], fill=INK, w=3)

    mx, my = cx + face * 10, head_cy + 24
    if emotion == "happy":
        g.arc(mx - 16, my - 12, mx + 16, my + 10, 15, 165, fill=INK, w=5)
    elif emotion in ("sad", "angry"):
        g.arc(mx - 14, my + 2, mx + 14, my + 18, 200, 340, fill=INK, w=5)
    elif emotion == "shocked":
        g.ellipse(mx - 8, my - 3, mx + 8, my + 15, fill="#ffffff", outline=INK, w=4)
    elif emotion == "thinking":
        g.line([(mx - 9, my + 5), (mx + 11, my + 1)], fill=INK, w=4)
    else:
        g.line([(mx - 11, my + 4), (mx + 11, my + 4)], fill=INK, w=4)

    _draw_hat(g, hat, cx, head_cy - HR)

    # tanda seru / tanya khas gambar tangan
    mark = {"shocked": "!!!", "panic": "!!!", "thinking": "?"}.get(emotion if emotion in ("shocked", "thinking") else pose)
    if mark:
        _hand_text(g, cx + face * 78, head_cy - 74, mark, 46)
    if emotion == "happy" or pose == "celebrate":
        for k in range(3):
            a = math.radians(-40 - 50 * k)
            x0, y0 = cx - face * 70 + math.cos(a) * 20, head_cy - 30 + math.sin(a) * 20
            g.line([(x0, y0), (x0 + math.cos(a) * 16, y0 + math.sin(a) * 16)], fill=INK, w=4)


def _hand_text(g, x, y, txt, size, fill=INK, anchor="mm"):
    f = load_font("hand", size * g.s)
    g.d.text(g.P(x, y), txt, font=f, fill=fill, anchor=anchor)


def _ground_doodle(g, rng):
    y = GROUND_Y + 10
    x = 50
    while x < W - 50:
        seg, gap = rng.uniform(90, 230), rng.uniform(14, 46)
        pts = [(x + k * seg / 6, y + rng.uniform(-2.5, 2.5)) for k in range(7)]
        g.line(pts, fill="#555555", w=5)
        x += seg + gap
    for _ in range(rng.randint(6, 10)):
        px, py, r = rng.uniform(70, W - 70), GROUND_Y + rng.uniform(8, 30), rng.uniform(6, 15)
        g.ellipse(px - r, py - r * 0.6, px + r, py + r * 0.6, fill="#e8e3d8", outline="#555555", w=4)
    for _ in range(rng.randint(3, 6)):
        px, py = rng.uniform(70, W - 70), GROUND_Y + 8
        for k in range(-2, 3):
            g.line([(px, py), (px + k * 5, py - rng.uniform(12, 22))], fill="#555555", w=4)


# ----------------------------------------------------------------------------- render adegan
def _wash(layer):
    rgb = layer.convert("RGB")
    a = layer.getchannel("A")
    rgb = ImageEnhance.Color(rgb).enhance(0.25)
    rgb = Image.blend(rgb, Image.new("RGB", rgb.size, (232, 226, 214)), 0.12)
    r, g_, b = rgb.split()
    return Image.merge("RGBA", (r, g_, b, a))


def _fit_text(text, kind, max_w, start, minimum):
    size = start
    while size > minimum:
        if load_font(kind, size).getlength(text) <= max_w:
            break
        size -= 2
    return size


def _glow_layer(cx, cy, radius):
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(255, 205, 70, 170))
    return glow.filter(ImageFilter.GaussianBlur(radius * 0.35))


def render_sketch_image(scene, idx=1, with_title=True):
    """Gambar adegan bergaya sketsa (RGB 1920x1080)."""
    vis = prepare_scene(scene, idx)
    mirror = vis["mirror"]
    rng = random.Random(1000 + idx)
    T = 1.9

    base = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    acc = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    gb = G(base, SS, 0, 0, lw=0.5)
    ga = G(acc, SS, 0, 0, lw=0.5)

    _ground_doodle(gb, rng)
    glow_pos = None
    try:
        for name in vis["area"]:
            set_sketch_mode(True, False)
            get_prop(name)[0](gb, T)
        for i, (name, (x, y, size)) in enumerate(vis["placed"]):
            gx = W - x if mirror else x
            func, kind = get_prop(name)
            if i == 0:
                set_sketch_mode(True, True)
                func(ga, gx, y, size, T)
                glow_pos = (gx, y - (95 * size if kind == "ground" else 0), 150 * size)
            else:
                set_sketch_mode(True, False)
                func(gb, gx, y, size, T)
    finally:
        set_sketch_mode(False)

    char_x = 960 if mirror else 320
    draw_sketch_character(gb, char_x, GROUND_Y, 0.9, vis["pose"], vis["emotion"], vis["hat"],
                          -1 if mirror else 1)

    layer = Image.alpha_composite(_wash(base), acc)

    title = str(scene.get("title", "")).strip().upper() if with_title else ""
    if title:
        d = ImageDraw.Draw(layer)
        size = _fit_text(title, "hand", (W - 260) * SS, 64 * SS, 32 * SS)
        d.text((W * SS / 2, 72 * SS), title, font=load_font("hand", size), fill="#141414",
               anchor="mm", stroke_width=int(1.8 * SS), stroke_fill="#141414")

    ink = wobble(layer.resize((OUT_W, OUT_H), Image.Resampling.LANCZOS), amp=2.6, cell=30, seed=idx)

    paper = make_paper().convert("RGBA")
    if glow_pos:
        gl = _glow_layer(*glow_pos).resize((OUT_W, OUT_H), Image.Resampling.BILINEAR)
        paper = Image.alpha_composite(paper, gl)
    return Image.alpha_composite(paper, ink).convert("RGB")


# ----------------------------------------------------------------------------- thumbnail
def _split_lines(text, max_lines=3):
    words = text.split()
    if len(words) <= 1:
        return [text]
    n = min(max_lines, len(words), 3 if len(words) >= 3 else 2)
    per = math.ceil(len(words) / n)
    return [" ".join(words[i:i + per]) for i in range(0, len(words), per)]


def add_thumbnail_text(img, text):
    """Teks judul raksasa bergaya thumbnail viral (huruf tebal, outline hitam, kata kunci kuning)."""
    img = img.convert("RGB")
    w, h = img.size
    d = ImageDraw.Draw(img)
    lines = _split_lines(str(text).upper().strip())
    max_w = int(w * 0.46)
    size = 170
    while size > 60:
        f = load_font("bold", size)
        total_h = sum(f.getbbox(ln)[3] - f.getbbox(ln)[1] for ln in lines) + (len(lines) - 1) * size * 0.16
        if max(f.getlength(ln) for ln in lines) <= max_w and total_h <= h * 0.78:
            break
        size -= 4
    f = load_font("bold", size)
    stroke = max(5, int(size * 0.075))
    heights = [f.getbbox(ln)[3] - f.getbbox(ln)[1] for ln in lines]
    total_h = sum(heights) + (len(lines) - 1) * size * 0.16
    y = (h - total_h) / 2 - 10
    key_idx = max(range(len(lines)), key=lambda i: len(lines[i])) if len(lines) > 1 else 0
    x = int(w * 0.04)
    for i, ln in enumerate(lines):
        col = "#ffd84d" if i == key_idx else "#ffffff"
        d.text((x, y), ln, font=f, fill=col, stroke_width=stroke, stroke_fill="#111111")
        if i == key_idx:
            lw_ = f.getlength(ln)
            yy = y + heights[i] + stroke + 8
            d.line([(x, yy), (x + lw_ * 0.5, yy + 6), (x + lw_, yy - 2)], fill="#e63946", width=10, joint="curve")
        y += heights[i] + size * 0.16
    return img


def render_sketch_thumbnail(storyboard):
    """Thumbnail 1280x720 bergaya sketsa: karakter besar + objek utama bercahaya + teks raksasa."""
    scenes = storyboard.get("scenes", [])
    scene0 = dict(scenes[0]) if scenes else {}
    scene0["title"] = ""
    scene0["pose"], scene0["emotion"] = "point", "shocked"
    vis = prepare_scene(scene0, 1)

    base = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    acc = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    gb = G(base, SS, 0, 0, lw=0.5)
    ga = G(acc, SS, 0, 0, lw=0.5)
    gc = G(base, SS * 1.28, 0, 0, lw=0.5)       # karakter diperbesar 1.28x
    rng = random.Random(77)
    _ground_doodle(gb, rng)

    glow = None
    try:
        for i, (name, (x, y, size)) in enumerate(vis["placed"][:2]):
            func, kind = get_prop(name)
            if i == 0:
                set_sketch_mode(True, True)
                px, py = (1010, 640) if kind == "ground" else (1000, 350)
                func(ga, px, py, 1.9 if kind == "ground" else 1.75, 1.9)
                glow = (px, py - (150 if kind == "ground" else 0), 260)
            else:
                set_sketch_mode(True, False)
                func(gb, 1130, 130, 0.8, 1.9)
    finally:
        set_sketch_mode(False)
    # koordinat karakter dalam satuan skala 1.28x
    draw_sketch_character(gc, 640 / 1.28, 650 / 1.28, 0.9, "point", "shocked", vis["hat"], 1)

    layer = Image.alpha_composite(_wash(base), acc)
    ink = wobble(layer.resize((OUT_W, OUT_H), Image.Resampling.LANCZOS), amp=2.4, cell=30, seed=9)
    paper = make_paper().convert("RGBA")
    if glow:
        gl = _glow_layer(*glow).resize((OUT_W, OUT_H), Image.Resampling.BILINEAR)
        paper = Image.alpha_composite(paper, gl)
    img = Image.alpha_composite(paper, ink).convert("RGB").resize((1280, 720), Image.Resampling.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(1.1)
    return add_thumbnail_text(img, storyboard.get("thumbnail_text", storyboard.get("title", "")))
