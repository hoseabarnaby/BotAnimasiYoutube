"""
Perpustakaan properti animasi untuk Stickman Explainer.
Setiap properti: func(g, x, y, s, t)
  - properti 'ground' : (x, y) = titik tengah-bawah (berpijak di lantai)
  - properti 'high'   : (x, y) = titik tengah (melayang di udara)
  - t = waktu (detik) sejak properti muncul
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from stick_core import G, K, RED, YEL, BLUE, W, rot_rect, rot_pts, GROUND_Y

GREEN = "#8fd18f"
DGREEN = "#3d8b50"
WOOD = "#d4a373"
DWOOD = "#a9714b"
GREY = "#ced4da"
DGREY = "#6c757d"
ORANGE = "#f4a261"


def shadow(g, x, y, w):
    g.ellipse(x - w / 2, y - 9, x + w / 2, y + 9, fill=(0, 0, 0, 55), outline=None, w=0)


def bill(g, cx, cy, w=70, h=36, ang=0):
    g.poly(rot_rect(cx, cy, w, h, ang), fill=GREEN, outline=K, w=3)
    g.poly(rot_rect(cx, cy, w * 0.78, h * 0.62, ang), fill=None, outline=DGREEN, w=2)
    r = h * 0.2
    g.ellipse(cx - r, cy - r, cx + r, cy + r, fill=DGREEN, outline=None, w=0)


def heart(g, x, y, r, fill=RED):
    for f, o in ((K, True), (fill, False)):
        k = 1.0 if o else 0.9
        g.ellipse(x - r * 1.05, y - r * 0.85, x + r * 0.05, y + r * 0.25, fill=f, outline=None, w=0)
        g.ellipse(x - r * 0.05, y - r * 0.85, x + r * 1.05, y + r * 0.25, fill=f, outline=None, w=0)
        g.poly([(x - r * 1.0, y - r * 0.15), (x + r * 1.0, y - r * 0.15), (x, y + r * 1.0)],
               fill=f, outline=None, w=0)
        if o:
            r = r * 0.86


def star(g, x, y, R, r, n, ang, fill, outline=K, w=4):
    pts = []
    for i in range(n * 2):
        a = math.radians(ang + i * 180.0 / n)
        rad = R if i % 2 == 0 else r
        pts.append((x + rad * math.cos(a), y + rad * math.sin(a)))
    g.poly(pts, fill=fill, outline=outline, w=w)


# ------------------------------- GROUND ---------------------------------------
def money_pile(g, x, y, s, t):
    shadow(g, x, y, 190 * s)
    for i in range(5):
        yy = y - 20 * s * (i + 1)
        w = (160 - 8 * i) * s
        g.rrect(x - w / 2, yy, x + w / 2, yy + 20 * s, r=5 * s, fill=GREEN if i % 2 == 0 else "#a6e3a6", outline=K, w=3)
        g.rrect(x - 14 * s, yy, x + 14 * s, yy + 20 * s, r=2 * s, fill=YEL, outline=K, w=2)
    top = y - 100 * s
    bill(g, x + 24 * s, top - 12 * s + math.sin(t * 3) * 3, 64 * s, 34 * s, math.sin(t * 2.5) * 10 - 12)
    g.text(x, top - 72 * s + math.sin(t * 3) * 3, "$", 54 * s, fill=DGREEN, stroke=3)
    for dx in (-105, -78, 108):
        g.ellipse(x + (dx - 14) * s, y - 14 * s, x + (dx + 14) * s, y + 2 * s, fill=YEL, outline=K, w=3)


def shopping_cart(g, x, y, s, t):
    shadow(g, x, y, 190 * s)
    by = y - 34 * s
    g.ellipse(x - 62 * s, by - 126 * s, x + 6 * s, by - 80 * s, fill="#e9b872", outline=K, w=4)
    g.rrect(x + 8 * s, by - 120 * s, x + 56 * s, by - 80 * s, r=5 * s, fill="#e63946", outline=K, w=4)
    g.poly([(x - 80 * s, by - 90 * s), (x + 75 * s, by - 90 * s), (x + 55 * s, by - 20 * s), (x - 60 * s, by - 20 * s)],
           fill="#f1f3f5", outline=K, w=4)
    for i in range(1, 4):
        g.line([(x + (-80 + i * 38.75) * s, by - 90 * s), (x + (-60 + i * 28.75) * s, by - 20 * s)],
               fill=DGREY, w=2, caps=False)
    for fr in (0.33, 0.66):
        yy = by - 90 * s + fr * 70 * s
        g.line([(x + (-80 + fr * 20) * s, yy), (x + (75 - fr * 20) * s, yy)], fill=DGREY, w=2, caps=False)
    g.line([(x - 80 * s, by - 90 * s), (x - 102 * s, by - 128 * s), (x - 124 * s, by - 128 * s)], w=6)
    for wx in (-40, 42):
        g.ellipse(x + (wx - 13) * s, y - 26 * s, x + (wx + 13) * s, y, fill=DGREY, outline=K, w=4)


def bank_building(g, x, y, s, t):
    shadow(g, x, y, 320 * s)
    w = 250 * s
    g.rect(x - w / 2 - 12 * s, y - 14 * s, x + w / 2 + 12 * s, y, fill="#e9e4da")
    g.rect(x - w / 2, y - 28 * s, x + w / 2, y - 14 * s, fill="#e9e4da")
    for i in range(5):
        cx = x - w / 2 + 22 * s + i * (w - 44 * s) / 4
        g.rect(cx - 13 * s, y - 175 * s, cx + 13 * s, y - 28 * s, fill="#fbf7ee")
    g.rect(x - w / 2, y - 205 * s, x + w / 2, y - 175 * s, fill="#e9e4da")
    g.poly([(x - w / 2 - 8 * s, y - 205 * s), (x, y - 268 * s), (x + w / 2 + 8 * s, y - 205 * s)], fill="#f3ede1")
    g.ellipse(x - 17 * s, y - 252 * s, x + 17 * s, y - 218 * s, fill=YEL, outline=K, w=3)
    g.text(x, y - 235 * s, "$", 22 * s, fill="#b5830b")
    g.text(x, y - 190 * s, "BANK", 22 * s, fill=K)


def printing_machine(g, x, y, s, t):
    shadow(g, x, y, 260 * s)
    g.rrect(x - 105 * s, y - 130 * s, x + 105 * s, y - 10 * s, r=14 * s, fill="#adb5bd", outline=K, w=5)
    g.rrect(x - 85 * s, y - 160 * s, x + 85 * s, y - 130 * s, r=8 * s, fill="#868e96", outline=K, w=5)
    g.rect(x - 70 * s, y - 100 * s, x + 20 * s, y - 70 * s, fill="#343a40", outline=K, w=4)
    on = int(t * 4) % 2 == 0
    g.ellipse(x + 45 * s, y - 108 * s, x + 65 * s, y - 88 * s, fill="#e63946" if on else "#6b1a21", outline=K, w=3)
    g.ellipse(x + 45 * s, y - 78 * s, x + 65 * s, y - 58 * s, fill="#80ed99", outline=K, w=3)
    g.rect(x - 30 * s, y - 45 * s, x + 80 * s, y - 28 * s, fill="#212529", outline=K, w=4)
    for k in range(5):
        ph = (t * 1.1 + k * 0.2) % 1.0
        bx = x + (20 + ph * 105) * s
        by = y - 170 * s - math.sin(ph * math.pi) * 85 * s + ph * 60 * s
        bill(g, bx, by, 58 * s, 30 * s, ph * 160 - 20)


def laptop(g, x, y, s, t):
    shadow(g, x, y, 240 * s)
    g.rect(x - 110 * s, y - 120 * s, x + 110 * s, y - 104 * s, fill=WOOD, outline=K, w=4)
    g.rect(x - 90 * s, y - 104 * s, x - 76 * s, y, fill=DWOOD, outline=K, w=4)
    g.rect(x + 76 * s, y - 104 * s, x + 90 * s, y, fill=DWOOD, outline=K, w=4)
    g.rrect(x - 70 * s, y - 126 * s, x + 70 * s, y - 120 * s, r=2 * s, fill="#adb5bd", outline=K, w=3)
    g.poly([(x - 56 * s, y - 126 * s), (x + 56 * s, y - 126 * s), (x + 62 * s, y - 214 * s), (x - 62 * s, y - 214 * s)],
           fill="#343a40", outline=K, w=4)
    g.rect(x - 50 * s, y - 206 * s, x + 50 * s, y - 132 * s, fill="#7bdff2", outline=None, w=0)
    for i in range(4):
        wdt = (60 + 18 * math.sin(t * 2 + i)) * s
        g.rect(x - 42 * s, y - 196 * s + i * 17 * s, x - 42 * s + wdt, y - 188 * s + i * 17 * s, fill="#ffffff", outline=None, w=0)


def house(g, x, y, s, t):
    shadow(g, x, y, 240 * s)
    g.rect(x + 40 * s, y - 220 * s, x + 74 * s, y - 130 * s, fill="#b56576", outline=K, w=4)
    g.rect(x - 85 * s, y - 120 * s, x + 85 * s, y, fill="#ffe8cc", outline=K, w=5)
    g.poly([(x - 108 * s, y - 118 * s), (x, y - 200 * s), (x + 108 * s, y - 118 * s)], fill="#e76f51", outline=K, w=5)
    g.rect(x - 22 * s, y - 80 * s, x + 22 * s, y, fill=DWOOD, outline=K, w=4)
    g.ellipse(x + 10 * s, y - 42 * s, x + 17 * s, y - 35 * s, fill=YEL, outline=None, w=0)
    g.rect(x + 40 * s, y - 95 * s, x + 74 * s, y - 55 * s, fill="#bde0fe", outline=K, w=4)
    g.rect(x - 74 * s, y - 95 * s, x - 40 * s, y - 55 * s, fill="#bde0fe", outline=K, w=4)
    for i in range(3):
        ph = (t * 0.5 + i * 0.33) % 1.0
        r = (10 + ph * 18) * s
        g.ellipse(x + 57 * s - r + ph * 25 * s, y - 230 * s - ph * 80 * s - r,
                  x + 57 * s + r + ph * 25 * s, y - 230 * s - ph * 80 * s + r, fill="#f1f3f5", outline=K, w=3)


def fire(g, x, y, s, t):
    shadow(g, x, y, 170 * s)
    g.poly(rot_rect(x - 8 * s, y - 14 * s, 130 * s, 22 * s, 12), fill=DWOOD, outline=K, w=4)
    g.poly(rot_rect(x + 8 * s, y - 14 * s, 130 * s, 22 * s, -12), fill="#8d5524", outline=K, w=4)
    f1, f2, f3 = math.sin(t * 11), math.sin(t * 13 + 1), math.sin(t * 9 + 2)

    def flame(scale, col, outline):
        pts = [(x - 48 * scale * s, y - 20 * s), (x - 32 * scale * s, y - (62 + 10 * f1) * scale * s),
               (x - 12 * scale * s, y - 42 * scale * s), (x + 2 * scale * s, y - (118 + 14 * f2) * scale * s),
               (x + 18 * scale * s, y - 52 * scale * s), (x + 36 * scale * s, y - (80 + 10 * f3) * scale * s),
               (x + 50 * scale * s, y - 20 * s)]
        g.poly(pts, fill=col, outline=K if outline else None, w=4)

    flame(1.0, "#f77f00", True)
    flame(0.66, YEL, False)
    for k in range(3):
        ph = (t * 0.9 + k * 0.33) % 1.0
        sx = x + math.sin(t * 3 + k * 2) * 35 * s
        sy = y - (80 + ph * 110) * s
        g.ellipse(sx - 3 * s, sy - 3 * s, sx + 3 * s, sy + 3 * s, fill=YEL, outline=None, w=0)


def trophy(g, x, y, s, t):
    shadow(g, x, y, 180 * s)
    g.rrect(x - 55 * s, y - 28 * s, x + 55 * s, y, r=4 * s, fill="#6c4f2f", outline=K, w=4)
    g.rect(x - 14 * s, y - 70 * s, x + 14 * s, y - 28 * s, fill=YEL, outline=K, w=4)
    for sgn in (-1, 1):
        g.arc(x + (sgn * 78 - 30) * s, y - 190 * s, x + (sgn * 78 + 30) * s, y - 120 * s, 90 if sgn == 1 else 270,
              270 if sgn == 1 else 90, fill=K, w=7)
    g.poly([(x - 66 * s, y - 200 * s), (x + 66 * s, y - 200 * s), (x + 46 * s, y - 120 * s),
            (x + 14 * s, y - 70 * s), (x - 14 * s, y - 70 * s), (x - 46 * s, y - 120 * s)], fill=YEL, outline=K, w=5)
    star(g, x, y - 150 * s, (24 + 3 * math.sin(t * 5)) * s, 11 * s, 5, -90 + t * 20, "#fff3b0", w=3)


# -------------------------------- HIGH ----------------------------------------
def _chart(g, x, y, s, t, down):
    g.rrect(x - 150 * s, y - 110 * s, x + 150 * s, y + 110 * s, r=16 * s, fill="#fffdf7", outline=K, w=5)
    for i in range(-1, 2):
        g.line([(x - 125 * s, y + i * 40 * s), (x + 125 * s, y + i * 40 * s)], fill="#e3dccb", w=2, caps=False)
    g.line([(x - 125 * s, y - 88 * s), (x - 125 * s, y + 85 * s), (x + 130 * s, y + 85 * s)], w=4)
    if down:
        data = [(-120, -62), (-85, -36), (-60, -56), (-25, -6), (0, -22), (35, 34), (65, 18), (115, 74)]
        col = RED
    else:
        data = [(-120, 70), (-85, 46), (-60, 56), (-25, 16), (0, 26), (35, -20), (65, -8), (115, -68)]
        col = DGREEN
    pts = [(x + a * s, y + b * s) for a, b in data]
    p = min(1.0, t / 1.3) * (len(pts) - 1)
    k = int(p)
    cur = pts[: k + 1]
    if k < len(pts) - 1:
        fr = p - k
        a, b = pts[k], pts[k + 1]
        cur.append((a[0] + (b[0] - a[0]) * fr, a[1] + (b[1] - a[1]) * fr))
    if len(cur) >= 2:
        g.line(cur, fill=col, w=8)
        (x1, y1), (x2, y2) = cur[-2], cur[-1]
        ang = math.atan2(y2 - y1, x2 - x1)
        hd = 20 * s
        g.poly([(x2 + math.cos(ang) * hd * 0.7, y2 + math.sin(ang) * hd * 0.7),
                (x2 + math.cos(ang + 2.5) * hd, y2 + math.sin(ang + 2.5) * hd),
                (x2 + math.cos(ang - 2.5) * hd, y2 + math.sin(ang - 2.5) * hd)], fill=col, outline=K, w=3)


def chart_down(g, x, y, s, t):
    _chart(g, x, y, s, t, True)


def chart_up(g, x, y, s, t):
    _chart(g, x, y, s, t, False)


def wallet_empty(g, x, y, s, t):
    g.rrect(x - 85 * s, y - 45 * s, x + 85 * s, y + 55 * s, r=14 * s, fill=DWOOD, outline=K, w=5)
    g.rrect(x - 74 * s, y - 62 * s, x + 74 * s, y + 20 * s, r=10 * s, fill="#f5ead6", outline=K, w=4)
    g.text(x, y - 24 * s, "$0", 34 * s, fill=RED)
    g.rrect(x - 85 * s, y - 8 * s, x + 85 * s, y + 55 * s, r=14 * s, fill="#c08552", outline=K, w=5)
    g.ellipse(x + 58 * s, y + 8 * s, x + 80 * s, y + 30 * s, fill=YEL, outline=K, w=3)
    for i in range(3):
        a = t * 3 + i * 2.1
        fx = x + (60 + i * 8) * s * math.cos(a)
        fy = y - 100 * s + 26 * s * math.sin(a * 1.3)
        g.ellipse(fx - 8 * s, fy - 11 * s, fx, fy - 2 * s, fill="#ffffff", outline=K, w=1.5)
        g.ellipse(fx - 4 * s, fy - 4 * s, fx + 4 * s, fy + 4 * s, fill=K, outline=None, w=0)


def bread(g, x, y, s, t):
    g.ellipse(x - 72 * s, y - 38 * s, x + 72 * s, y + 38 * s, fill="#e9b872", outline=K, w=5)
    for i in range(3):
        g.line([(x + (-34 + i * 32) * s, y - 22 * s), (x + (-20 + i * 32) * s, y + 2 * s)], fill="#b9772a", w=6)
    star(g, x + 60 * s, y - 40 * s, (16 + 4 * math.sin(t * 6)) * s, 5 * s, 4, 0, "#fff3b0", w=2)


def price_tag(g, x, y, s, t):
    ang = math.sin(t * 2.2) * 10
    base = [(x - 62 * s, y - 34 * s), (x + 30 * s, y - 34 * s), (x + 68 * s, y), (x + 30 * s, y + 34 * s), (x - 62 * s, y + 34 * s)]
    pts = rot_pts(base, x, y, ang)
    g.poly(pts, fill=YEL, outline=K, w=5)
    hx, hy = rot_pts([(x - 48 * s, y)], x, y, ang)[0]
    g.ellipse(hx - 7 * s, hy - 7 * s, hx + 7 * s, hy + 7 * s, fill="#ffffff", outline=K, w=3)
    g.text(x + 2 * s, y + 1 * s, "$$$", 30 * s, fill=RED)
    g.poly([(x + 48 * s, y - 70 * s), (x + 70 * s, y - 44 * s), (x + 58 * s, y - 44 * s),
            (x + 58 * s, y - 20 * s), (x + 38 * s, y - 20 * s), (x + 38 * s, y - 44 * s), (x + 26 * s, y - 44 * s)],
           fill=RED, outline=K, w=3)


def coins(g, x, y, s, t):
    for i in range(3):
        cx = x + (i - 1) * 74 * s
        cy = y + math.sin(t * 2 + i) * 9 * s
        wd = max(5.0, abs(math.cos(t * 3 + i * 1.3)) * 30) * s
        g.ellipse(cx - wd, cy - 30 * s, cx + wd, cy + 30 * s, fill=YEL, outline=K, w=4)
        if wd > 16 * s:
            g.ellipse(cx - wd * 0.72, cy - 22 * s, cx + wd * 0.72, cy + 22 * s, fill=None, outline="#e0a800", w=2)
            g.text(cx, cy, "$", 30 * s, fill="#b5830b")


def lightbulb(g, x, y, s, t):
    ln = 16 + 10 * math.sin(t * 6)
    for i in range(9):
        a = math.radians(-180 + i * 22.5)
        g.line([(x + 64 * s * math.cos(a), y - 8 * s + 64 * s * math.sin(a)),
                (x + (64 + ln) * s * math.cos(a), y - 8 * s + (64 + ln) * s * math.sin(a))], fill=YEL, w=6)
    g.ellipse(x - 48 * s, y - 56 * s, x + 48 * s, y + 40 * s, fill="#fff3b0", outline=K, w=5)
    g.rrect(x - 20 * s, y + 34 * s, x + 20 * s, y + 66 * s, r=5 * s, fill=GREY, outline=K, w=4)
    g.line([(x - 20 * s, y + 48 * s), (x + 20 * s, y + 48 * s)], w=3, caps=False)
    g.line([(x - 12 * s, y + 20 * s), (x - 4 * s, y - 8 * s), (x + 4 * s, y + 10 * s), (x + 12 * s, y - 14 * s)], fill="#e0a800", w=4)


def question_marks(g, x, y, s, t):
    for i, (dx, dy, sz) in enumerate(((0, 0, 130), (-86, -34, 84), (84, -10, 96))):
        bob = math.sin(t * 3 + i * 1.7) * 9 * s
        g.text(x + dx * s, y + dy * s + bob, "?", sz * s, fill=YEL, stroke=4)


def clock(g, x, y, s, t):
    x = x + math.sin(t * 28) * 2.5 * s
    for sgn in (-1, 1):
        g.ellipse(x + (sgn * 46 - 24) * s, y - 92 * s, x + (sgn * 46 + 24) * s, y - 52 * s, fill=YEL, outline=K, w=4)
    g.ellipse(x - 70 * s, y - 70 * s, x + 70 * s, y + 70 * s, fill="#ffffff", outline=K, w=6)
    for i in range(12):
        a = math.radians(i * 30)
        g.line([(x + 54 * s * math.sin(a), y - 54 * s * math.cos(a)), (x + 62 * s * math.sin(a), y - 62 * s * math.cos(a))], w=4)
    for ln, spd, w in ((46, 120, 4), (32, 10, 6)):
        a = math.radians(t * spd)
        g.line([(x, y), (x + ln * s * math.sin(a), y - ln * s * math.cos(a))], w=w)
    g.ellipse(x - 6 * s, y - 6 * s, x + 6 * s, y + 6 * s, fill=RED, outline=K, w=2)


def phone(g, x, y, s, t):
    g.rrect(x - 50 * s, y - 88 * s, x + 50 * s, y + 88 * s, r=16 * s, fill="#343a40", outline=K, w=5)
    g.rrect(x - 42 * s, y - 72 * s, x + 42 * s, y + 72 * s, r=8 * s, fill="#7bdff2", outline=None, w=0)
    g.rrect(x - 16 * s, y - 84 * s, x + 16 * s, y - 76 * s, r=3 * s, fill=K, outline=None, w=0)
    for i in range(3):
        g.rrect(x - 32 * s, y - 52 * s + i * 34 * s, x + 32 * s, y - 28 * s + i * 34 * s, r=6 * s, fill="#ffffff", outline=None, w=0)
    for i in range(3):
        ph = (t * 0.7 + i * 0.33) % 1.0
        heart(g, x + (i - 1) * 46 * s, y - 96 * s - ph * 110 * s, (10 + 5 * ph) * s)


def book(g, x, y, s, t):
    g.poly([(x - 96 * s, y - 40 * s), (x, y - 56 * s), (x + 96 * s, y - 40 * s), (x + 96 * s, y + 64 * s),
            (x, y + 76 * s), (x - 96 * s, y + 64 * s)], fill="#9d4edd", outline=K, w=5)
    g.poly([(x - 86 * s, y - 34 * s), (x - 4 * s, y - 48 * s), (x - 4 * s, y + 56 * s), (x - 86 * s, y + 46 * s)],
           fill="#ffffff", outline=K, w=3)
    g.poly([(x + 86 * s, y - 34 * s), (x + 4 * s, y - 48 * s), (x + 4 * s, y + 56 * s), (x + 86 * s, y + 46 * s)],
           fill="#ffffff", outline=K, w=3)
    for i in range(5):
        yy = -22 + i * 16
        g.line([(x - 74 * s, y + yy * s), (x - 18 * s, y + (yy - 6) * s)], fill=GREY, w=3, caps=False)
        g.line([(x + 18 * s, y + (yy - 6) * s), (x + 74 * s, y + yy * s)], fill=GREY, w=3, caps=False)
    star(g, x + 80 * s, y - 62 * s, (14 + 4 * math.sin(t * 5)) * s, 4 * s, 4, 0, YEL, w=2)


def globe(g, x, y, s, t):
    g.arc(x - 94 * s, y - 30 * s, x + 94 * s, y + 30 * s, 190, 350, fill=K, w=5)
    g.ellipse(x - 70 * s, y - 70 * s, x + 70 * s, y + 70 * s, fill="#74c0fc", outline=K, w=6)
    off = math.sin(t * 1.2) * 14
    for pts in ([(-40, -30), (-10, -50), (10, -20), (-20, 10), (-46, 0)], [(20, 0), (50, -10), (56, 30), (30, 50), (14, 24)]):
        g.poly([(x + (a + off) * s, y + b * s) for a, b in pts], fill="#69db7c", outline=K, w=3)
    g.ellipse(x - 28 * s, y - 70 * s, x + 28 * s, y + 70 * s, fill=None, outline="#1c7ed6", w=2)
    g.line([(x - 70 * s, y), (x + 70 * s, y)], fill="#1c7ed6", w=2, caps=False)
    g.arc(x - 94 * s, y - 30 * s, x + 94 * s, y + 30 * s, 10, 170, fill=K, w=5)


def rocket(g, x, y, s, t):
    y = y - math.sin(t * 3) * 10 * s
    fl = 36 + 14 * math.sin(t * 20)
    g.poly([(x - 22 * s, y + 80 * s), (x + 22 * s, y + 80 * s), (x, y + (80 + fl * 2) * s)], fill="#f77f00", outline=K, w=4)
    g.poly([(x - 12 * s, y + 80 * s), (x + 12 * s, y + 80 * s), (x, y + (80 + fl * 1.2) * s)], fill=YEL, outline=None, w=0)
    g.poly([(x - 40 * s, y + 20 * s), (x - 72 * s, y + 90 * s), (x - 30 * s, y + 70 * s)], fill=RED, outline=K, w=4)
    g.poly([(x + 40 * s, y + 20 * s), (x + 72 * s, y + 90 * s), (x + 30 * s, y + 70 * s)], fill=RED, outline=K, w=4)
    g.ellipse(x - 40 * s, y - 100 * s, x + 40 * s, y + 90 * s, fill="#ffffff", outline=K, w=5)
    g.poly([(x - 36 * s, y - 50 * s), (x, y - 120 * s), (x + 36 * s, y - 50 * s)], fill=RED, outline=K, w=4)
    g.ellipse(x - 17 * s, y - 28 * s, x + 17 * s, y + 6 * s, fill="#7bdff2", outline=K, w=4)


def heart_prop(g, x, y, s, t):
    heart(g, x, y, (62 + 7 * math.sin(t * 6)) * s)


def warning(g, x, y, s, t):
    x = x + math.sin(t * 22) * 2 * s
    col = YEL if int(t * 4) % 2 == 0 else "#ffb703"
    g.poly([(x, y - 82 * s), (x + 84 * s, y + 62 * s), (x - 84 * s, y + 62 * s)], fill=col, outline=K, w=7)
    g.text(x, y + 14 * s, "!", 100 * s, fill=K)


def boom(g, x, y, s, t):
    pul = 1 + 0.08 * math.sin(t * 9)
    star(g, x, y, 100 * s * pul, 58 * s * pul, 12, t * 25, RED, w=6)
    star(g, x, y, 72 * s * pul, 40 * s * pul, 12, -t * 25, YEL, w=4)
    g.text(x, y, "BOOM", 36 * s, fill="#ffffff", stroke=4)


def _gear(g, x, y, r, teeth, ang, fill):
    pts = []
    for i in range(teeth * 4):
        a = math.radians(ang + i * 90.0 / teeth)
        rad = r * 1.22 if (i % 4) in (0, 1) else r
        pts.append((x + rad * math.cos(a), y + rad * math.sin(a)))
    g.poly(pts, fill=fill, outline=K, w=4)
    g.ellipse(x - r * 0.38, y - r * 0.38, x + r * 0.38, y + r * 0.38, fill="#f1f3f5", outline=K, w=4)


def gear(g, x, y, s, t):
    _gear(g, x, y, 56 * s, 8, t * 40, "#adb5bd")
    _gear(g, x + 92 * s, y + 62 * s, 34 * s, 6, -t * 66 + 15, YEL)


def balance_scale(g, x, y, s, t):
    tilt = math.sin(t * 1.6) * 12
    g.line([(x, y - 90 * s), (x, y + 80 * s)], w=7)
    g.rrect(x - 50 * s, y + 76 * s, x + 50 * s, y + 92 * s, r=4 * s, fill=DWOOD, outline=K, w=4)
    a = math.radians(tilt)
    lx, ly = x - 96 * math.cos(a) * s, y - 80 * s - 96 * math.sin(a) * s
    rx, ry = x + 96 * math.cos(a) * s, y - 80 * s + 96 * math.sin(a) * s
    g.line([(lx, ly), (rx, ry)], w=7)
    for px, py, item in ((lx, ly, 0), (rx, ry, 1)):
        g.line([(px, py), (px - 34 * s, py + 74 * s)], fill=DGREY, w=3, caps=False)
        g.line([(px, py), (px + 34 * s, py + 74 * s)], fill=DGREY, w=3, caps=False)
        g.poly([(px - 44 * s, py + 74 * s), (px + 44 * s, py + 74 * s), (px + 28 * s, py + 96 * s), (px - 28 * s, py + 96 * s)],
               fill=YEL, outline=K, w=4)
        if item == 0:
            g.ellipse(px - 20 * s, py + 44 * s, px + 20 * s, py + 76 * s, fill=YEL, outline=K, w=3)
            g.text(px, py + 60 * s, "$", 22 * s, fill="#b5830b")
        else:
            g.rrect(px - 22 * s, py + 40 * s, px + 22 * s, py + 76 * s, r=4 * s, fill=BLUE, outline=K, w=3)


def zzz(g, x, y, s, t):
    for i in range(3):
        ph = (t * 0.45 + i * 0.33) % 1.0
        sz = (40 + i * 22 + ph * 10) * s
        g.text(x + (i * 46 - 40 + ph * 20) * s, y + (50 - i * 40 - ph * 50) * s, "Z", sz, fill="#4361ee", stroke=3)


def battery(g, x, y, s, t):
    g.rrect(x - 78 * s, y - 42 * s, x + 66 * s, y + 42 * s, r=10 * s, fill="#ffffff", outline=K, w=6)
    g.rect(x + 66 * s, y - 14 * s, x + 84 * s, y + 14 * s, fill=K, outline=K, w=2)
    if int(t * 3) % 2 == 0:
        g.rect(x - 68 * s, y - 32 * s, x - 38 * s, y + 32 * s, fill=RED, outline=None, w=0)
    g.text(x + 12 * s, y, "5%", 34 * s, fill=RED)


def briefcase(g, x, y, s, t):
    g.arc(x - 34 * s, y - 80 * s, x + 34 * s, y - 20 * s, 180, 360, fill=K, w=8)
    g.rrect(x - 90 * s, y - 40 * s, x + 90 * s, y + 56 * s, r=12 * s, fill="#8d5524", outline=K, w=5)
    g.line([(x - 90 * s, y + 4 * s), (x + 90 * s, y + 4 * s)], w=4, caps=False)
    g.rrect(x - 14 * s, y - 6 * s, x + 14 * s, y + 18 * s, r=3 * s, fill=YEL, outline=K, w=3)


def storm_cloud(g, x, y, s, t):
    for dx, dy, rx, ry in ((0, 0, 70, 40), (-60, 16, 52, 32), (62, 18, 54, 32), (-14, -26, 44, 34)):
        g.ellipse(x + (dx - rx) * s, y + (dy - ry) * s, x + (dx + rx) * s, y + (dy + ry) * s, fill="#adb5bd", outline=K, w=5)
    for dx, dy, rx, ry in ((0, 0, 70, 40), (-60, 16, 52, 32), (62, 18, 54, 32), (-14, -26, 44, 34)):
        g.ellipse(x + (dx - rx) * s + 4, y + (dy - ry) * s + 4, x + (dx + rx) * s - 4, y + (dy + ry) * s - 4, fill="#adb5bd", outline=None, w=0)
    for i in range(6):
        ph = (t * 1.3 + i * 0.17) % 1.0
        rx_ = x + (-70 + i * 28) * s
        g.line([(rx_, y + (50 + ph * 90) * s), (rx_ - 6 * s, y + (66 + ph * 90) * s)], fill="#4cc9f0", w=4)
    if math.sin(t * 5) > 0.5:
        g.poly([(x + 6 * s, y + 40 * s), (x - 20 * s, y + 90 * s), (x + 2 * s, y + 88 * s), (x - 14 * s, y + 140 * s),
                (x + 30 * s, y + 76 * s), (x + 8 * s, y + 78 * s)], fill=YEL, outline=K, w=3)


# ------------------------------- AREA -----------------------------------------
def banknotes_rain(g, t):
    for i in range(16):
        x0 = (i * 97) % 680 + 20
        sp = 150 + (i * 37) % 90
        y = 110 + ((t * sp + i * 131) % 820)
        bill(g, x0 + math.sin(t * 1.5 + i) * 24, y, 58, 30, math.sin(t * 2 + i) * 40 + i * 12)


# ------------------------- IKON UNIVERSAL (emoji berwarna) --------------------
# Untuk hewan, kendaraan, sains, sejarah, dll. yang tidak digambar manual:
# dirender dari font emoji sistem + garis hitam tebal ala stiker, lalu dianimasikan.
EMOJI_WORDS = {
    # hewan
    "octopus": "\U0001F419", "gurita": "\U0001F419", "fish": "\U0001F41F", "ikan": "\U0001F41F",
    "shark": "\U0001F988", "hiu": "\U0001F988", "whale": "\U0001F40B", "paus": "\U0001F40B",
    "dolphin": "\U0001F42C", "lumba": "\U0001F42C", "turtle": "\U0001F422", "kura": "\U0001F422",
    "bird": "\U0001F426", "burung": "\U0001F426", "eagle": "\U0001F985", "cat": "\U0001F431",
    "kucing": "\U0001F431", "dog": "\U0001F436", "anjing": "\U0001F436", "elephant": "\U0001F418",
    "gajah": "\U0001F418", "lion": "\U0001F981", "singa": "\U0001F981", "tiger": "\U0001F42F",
    "harimau": "\U0001F42F", "monkey": "\U0001F435", "monyet": "\U0001F435", "snake": "\U0001F40D",
    "ular": "\U0001F40D", "spider": "\U0001F577", "laba": "\U0001F577", "bee": "\U0001F41D",
    "lebah": "\U0001F41D", "butterfly": "\U0001F98B", "kupu": "\U0001F98B", "ant": "\U0001F41C",
    "semut": "\U0001F41C", "dinosaur": "\U0001F996", "dinosaurus": "\U0001F996", "trex": "\U0001F996",
    "horse": "\U0001F434", "kuda": "\U0001F434", "cow": "\U0001F404", "sapi": "\U0001F404",
    "pig": "\U0001F416", "babi": "\U0001F416", "chicken": "\U0001F414", "ayam": "\U0001F414",
    "rabbit": "\U0001F430", "kelinci": "\U0001F430", "bear": "\U0001F43B", "beruang": "\U0001F43B",
    "wolf": "\U0001F43A", "serigala": "\U0001F43A", "penguin": "\U0001F427", "pinguin": "\U0001F427",
    "crab": "\U0001F980", "kepiting": "\U0001F980", "frog": "\U0001F438", "katak": "\U0001F438",
    "lizard": "\U0001F98E", "kadal": "\U0001F98E", "gecko": "\U0001F98E", "crocodile": "\U0001F40A", "buaya": "\U0001F40A",
    "mouse": "\U0001F42D", "tikus": "\U0001F42D", "giraffe": "\U0001F992", "jerapah": "\U0001F992",
    "panda": "\U0001F43C", "owl": "\U0001F989", "hantu": "\U0001F47B", "shrimp": "\U0001F990",
    "udang": "\U0001F990", "squid": "\U0001F991", "cumi": "\U0001F991", "snail": "\U0001F40C",
    "bat": "\U0001F987", "kelelawar": "\U0001F987", "camel": "\U0001F42B", "unta": "\U0001F42B",
    "zebra": "\U0001F993", "animal": "\U0001F43E", "hewan": "\U0001F43E",
    # kendaraan
    "airplane": "\u2708\ufe0f", "plane": "\u2708\ufe0f", "jet": "\u2708\ufe0f", "pesawat": "\u2708\ufe0f",
    "helicopter": "\U0001F681", "ship": "\U0001F6A2", "kapal": "\U0001F6A2", "boat": "\u26F5",
    "car": "\U0001F697", "mobil": "\U0001F697", "train": "\U0001F686", "kereta": "\U0001F686",
    "bus": "\U0001F68C", "bicycle": "\U0001F6B2", "sepeda": "\U0001F6B2", "motorcycle": "\U0001F3CD",
    "truck": "\U0001F69A", "satellite": "\U0001F6F0", "satelit": "\U0001F6F0", "ufo": "\U0001F6F8",
    # sains & alam
    "atom": "\u269B\ufe0f", "dna": "\U0001F9EC", "microscope": "\U0001F52C", "mikroskop": "\U0001F52C",
    "telescope": "\U0001F52D", "teleskop": "\U0001F52D", "flask": "\U0001F9EA", "chemistry": "\U0001F9EA",
    "magnet": "\U0001F9F2", "volcano": "\U0001F30B", "gunung_berapi": "\U0001F30B", "tornado": "\U0001F32A",
    "rainbow": "\U0001F308", "pelangi": "\U0001F308", "sun": "\u2600\ufe0f", "matahari": "\u2600\ufe0f",
    "moon": "\U0001F319", "bulan": "\U0001F319", "cloud": "\u2601\ufe0f", "clouds": "\u2601\ufe0f",
    "awan": "\u2601\ufe0f", "star": "\u2B50", "bintang": "\u2B50",
    "planet": "\U0001FA90", "saturn": "\U0001FA90", "comet": "\u2604\ufe0f", "lightning": "\u26A1",
    "petir": "\u26A1", "snowflake": "\u2744\ufe0f", "snow": "\u2744\ufe0f", "salju": "\u2744\ufe0f",
    "ice": "\U0001F9CA", "es": "\U0001F9CA", "water": "\U0001F4A7", "droplet": "\U0001F4A7",
    "air_minum": "\U0001F4A7", "wave": "\U0001F30A", "ombak": "\U0001F30A", "tree": "\U0001F333",
    "pohon": "\U0001F333", "plant": "\U0001F331", "flower": "\U0001F338", "bunga": "\U0001F338",
    "mountain": "\u26F0\ufe0f", "gunung": "\u26F0\ufe0f", "leaf": "\U0001F343", "mushroom": "\U0001F344",
    "jamur": "\U0001F344", "cactus": "\U0001F335", "kaktus": "\U0001F335",
    # sejarah & perang
    "sword": "\u2694\ufe0f", "pedang": "\u2694\ufe0f", "shield": "\U0001F6E1\ufe0f", "perisai": "\U0001F6E1\ufe0f",
    "bomb": "\U0001F4A3", "bom": "\U0001F4A3", "cannon": "\U0001F4A3", "meriam": "\U0001F4A3",
    "castle": "\U0001F3F0", "istana": "\U0001F3F0", "benteng": "\U0001F3F0", "crown": "\U0001F451",
    "mahkota": "\U0001F451", "scroll": "\U0001F4DC", "gulungan": "\U0001F4DC", "flag": "\U0001F6A9",
    "bendera": "\U0001F6A9", "medal": "\U0001F3C5", "medali": "\U0001F3C5", "map": "\U0001F5FA\ufe0f",
    "peta": "\U0001F5FA\ufe0f", "compass": "\U0001F9ED", "kompas": "\U0001F9ED", "anchor": "\u2693",
    "jangkar": "\u2693", "pyramid": "\U0001F3DC\ufe0f", "piramida": "\U0001F3DC\ufe0f", "statue": "\U0001F5FF",
    "patung": "\U0001F5FF", "bow": "\U0001F3F9", "panah": "\U0001F3F9", "king": "\U0001F934",
    "raja": "\U0001F934", "soldier": "\U0001F482", "tentara": "\U0001F482",
    # tubuh & kesehatan
    "brain": "\U0001F9E0", "otak": "\U0001F9E0", "skull": "\U0001F480", "tengkorak": "\U0001F480",
    "bone": "\U0001F9B4", "tulang": "\U0001F9B4", "tooth": "\U0001F9B7", "gigi": "\U0001F9B7",
    "eye": "\U0001F441\ufe0f", "mata": "\U0001F441\ufe0f", "ear": "\U0001F442", "telinga": "\U0001F442",
    "muscle": "\U0001F4AA", "otot": "\U0001F4AA", "virus": "\U0001F9A0", "bacteria": "\U0001F9A0",
    "pill": "\U0001F48A", "obat": "\U0001F48A", "syringe": "\U0001F489", "vaccine": "\U0001F489",
    "vaksin": "\U0001F489", "medicine": "\U0001F48A",
    # benda sehari-hari
    "apple": "\U0001F34E", "apel": "\U0001F34E", "pizza": "\U0001F355", "coffee": "\u2615", "kopi": "\u2615",
    "cake": "\U0001F382", "kue": "\U0001F382", "burger": "\U0001F354", "banana": "\U0001F34C",
    "pisang": "\U0001F34C", "egg": "\U0001F95A", "telur": "\U0001F95A", "rice": "\U0001F35A",
    "nasi": "\U0001F35A", "camera": "\U0001F4F7", "kamera": "\U0001F4F7", "tv": "\U0001F4FA",
    "television": "\U0001F4FA", "music": "\U0001F3B5", "musik": "\U0001F3B5", "guitar": "\U0001F3B8",
    "gitar": "\U0001F3B8", "game": "\U0001F3AE", "ball": "\u26BD", "soccer": "\u26BD", "bola": "\u26BD",
    "key": "\U0001F511", "kunci": "\U0001F511", "lock": "\U0001F512", "gembok": "\U0001F512",
    "gift": "\U0001F381", "hadiah": "\U0001F381", "diamond": "\U0001F48E", "berlian": "\U0001F48E",
    "email": "\U0001F4E7", "news": "\U0001F4F0", "berita": "\U0001F4F0", "hourglass": "\u23F3",
    "calendar": "\U0001F4C5", "kalender": "\U0001F4C5", "magnifier": "\U0001F50D", "search": "\U0001F50D",
    # teknologi, olahraga, cuaca, makanan & simbol populer lainnya
    "cpu": "\U0001F4BB", "code": "\U0001F4BB", "internet": "\U0001F310", "wifi": "\U0001F4F6",
    "battery_full": "\U0001F50B", "plug": "\U0001F50C", "bulb": "\U0001F4A1", "flashlight": "\U0001F526",
    "candle": "\U0001F56F\ufe0f", "lilin": "\U0001F56F\ufe0f", "broom": "\U0001F9F9", "sapu": "\U0001F9F9",
    "basket": "\U0001F9FA", "soap": "\U0001F9FC", "sabun": "\U0001F9FC", "sponge": "\U0001F9FD",
    "bed": "\U0001F6CF\ufe0f", "kasur": "\U0001F6CF\ufe0f", "chair": "\U0001FA91", "kursi": "\U0001FA91",
    "door": "\U0001F6AA", "pintu": "\U0001F6AA", "window": "\U0001FA9F", "jendela": "\U0001FA9F",
    "mirror": "\U0001FA9E", "cermin": "\U0001FA9E", "toilet": "\U0001F6BD", "shower": "\U0001F6BF",
    "bathtub": "\U0001F6C1", "toothbrush": "\U0001FAA5", "razor": "\U0001FA92",
    "hospital": "\U0001F3E5", "rumah_sakit": "\U0001F3E5", "school": "\U0001F3EB", "sekolah": "\U0001F3EB",
    "factory": "\U0001F3ED", "pabrik": "\U0001F3ED", "church": "\u26EA", "mosque": "\U0001F54C",
    "masjid": "\U0001F54C", "temple": "\U0001F6D5", "tent": "\u26FA", "tenda": "\u26FA",
    "fountain": "\u26F2", "bridge": "\U0001F309", "jembatan": "\U0001F309", "statue_liberty": "\U0001F5FD",
    "tower": "\U0001F5FC", "menara": "\U0001F5FC", "island": "\U0001F3DD\ufe0f", "pulau": "\U0001F3DD\ufe0f",
    "desert": "\U0001F3DC\ufe0f", "gurun": "\U0001F3DC\ufe0f", "beach": "\U0001F3D6\ufe0f", "pantai": "\U0001F3D6\ufe0f",
    "camping": "\U0001F3D5\ufe0f", "stadium": "\U0001F3DF\ufe0f", "stadion": "\U0001F3DF\ufe0f",
    "runner": "\U0001F3C3", "run": "\U0001F3C3", "running": "\U0001F3C3", "lari": "\U0001F3C3",
    "walk": "\U0001F6B6", "jalan": "\U0001F6B6", "swim": "\U0001F3CA", "berenang": "\U0001F3CA",
    "dive": "\U0001F93F", "menyelam": "\U0001F93F", "climb": "\U0001F9D7", "panjat": "\U0001F9D7",
    "weight": "\U0001F3CB\ufe0f", "gym": "\U0001F3CB\ufe0f", "boxing": "\U0001F94A", "tinju": "\U0001F94A",
    "basketball": "\U0001F3C0", "basket": "\U0001F3C0", "football": "\u26BD", "tennis": "\U0001F3BE",
    "badminton": "\U0001F3F8", "golf": "\u26F3", "fishing": "\U0001F3A3", "mancing": "\U0001F3A3",
    "chess": "\u265F\ufe0f", "catur": "\u265F\ufe0f", "dice": "\U0001F3B2", "dadu": "\U0001F3B2",
    "puzzle": "\U0001F9E9", "target": "\U0001F3AF", "bullseye": "\U0001F3AF", "art": "\U0001F3A8",
    "microphone": "\U0001F3A4", "mic": "\U0001F3A4", "headphone": "\U0001F3A7", "drum": "\U0001F941",
    "violin": "\U0001F3BB", "trumpet": "\U0001F3BA", "movie": "\U0001F3AC", "film": "\U0001F3AC",
    "ticket": "\U0001F3AB", "tiket": "\U0001F3AB", "Mask": "\U0001F3AD", "topeng": "\U0001F3AD",
    "foot": "\U0001F9B6", "feet": "\U0001F9B6", "kaki": "\U0001F9B6", "hand": "\u270B", "tangan": "\u270B",
    "finger": "\U0001F446", "lungs": "\U0001FAC1", "paru": "\U0001FAC1", "heart_organ": "\U0001FAC0",
    "jantung": "\U0001FAC0", "blood": "\U0001FA78", "darah": "\U0001FA78", "bandage": "\U0001FA79",
    "stethoscope": "\U0001FA7A", "dokter": "\U0001FA7A", "doctor": "\U0001FA7A", "x_ray": "\U0001FA7B",
    "glasses": "\U0001F453", "kacamata": "\U0001F453", "sunglasses": "\U0001F576\ufe0f", "ring": "\U0001F48D",
    "cincin": "\U0001F48D", "lipstick": "\U0001F484", "perfume": "\U0001F9F4", "umbrella": "\u2602\ufe0f",
    "payung": "\u2602\ufe0f", "backpack": "\U0001F392", "tas": "\U0001F392", "shoe": "\U0001F45F",
    "sepatu": "\U0001F45F", "boot": "\U0001F97E", "socks": "\U0001F9E6", "gloves": "\U0001F9E4",
    "scarf": "\U0001F9E3", "coat": "\U0001F9E5", "dress": "\U0001F457", "shirt": "\U0001F455",
    "pants": "\U0001F456", "helmet": "\u26D1\ufe0f", "helm": "\u26D1\ufe0f",
    "meat": "\U0001F356", "daging": "\U0001F356", "steak": "\U0001F969", "cheese": "\U0001F9C0",
    "keju": "\U0001F9C0", "milk": "\U0001F95B", "susu": "\U0001F95B", "honey": "\U0001F36F",
    "madu": "\U0001F36F", "salt": "\U0001F9C2", "garam": "\U0001F9C2", "chili": "\U0001F336\ufe0f",
    "cabai": "\U0001F336\ufe0f", "corn": "\U0001F33D", "jagung": "\U0001F33D", "carrot": "\U0001F955",
    "wortel": "\U0001F955", "potato": "\U0001F954", "kentang": "\U0001F954", "garlic": "\U0001F9C4",
    "onion": "\U0001F9C5", "tomato": "\U0001F345", "tomat": "\U0001F345", "coconut": "\U0001F965",
    "kelapa": "\U0001F965", "grape": "\U0001F347", "anggur": "\U0001F347", "watermelon": "\U0001F349",
    "semangka": "\U0001F349", "lemon": "\U0001F34B", "strawberry": "\U0001F353", "cherry": "\U0001F352",
    "ice_cream": "\U0001F366", "eskrim": "\U0001F366", "chocolate": "\U0001F36B", "coklat": "\U0001F36B",
    "candy": "\U0001F36C", "permen": "\U0001F36C", "donut": "\U0001F369", "cookie": "\U0001F36A",
    "tea": "\U0001F375", "teh": "\U0001F375", "juice": "\U0001F9C3", "jus": "\U0001F9C3",
    "hammer": "\U0001F528", "palu": "\U0001F528", "axe": "\U0001FA93", "kapak": "\U0001FA93",
    "wrench": "\U0001F527", "obeng": "\U0001FA9B", "saw": "\U0001FA9A", "gergaji": "\U0001FA9A",
    "ladder": "\U0001FA9C", "tangga": "\U0001FA9C", "brick": "\U0001F9F1", "bata": "\U0001F9F1",
    "chain": "\u26D3\ufe0f", "rantai": "\u26D3\ufe0f", "hook": "\U0001FA9D", "toolbox": "\U0001F9F0",
    "gun": "\U0001F52B", "pistol": "\U0001F52B", "dagger": "\U0001F5E1\ufe0f", "pisau": "\U0001F52A",
    "knife": "\U0001F52A", "dynamite": "\U0001F9E8", "petasan": "\U0001F9E8",
}

_EMOJI_FONTS = [
    ("C:/Windows/Fonts/seguiemj.ttf", 360),
    ("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109),
    ("/usr/share/fonts/noto/NotoColorEmoji.ttf", 109),
    ("/System/Library/Fonts/Apple Color Emoji.ttc", 160),
]
_EMOJI_CACHE = {}


def _emoji_base(ch):
    """Sprite emoji berwarna + garis hitam tebal (stiker). None jika font emoji tidak tersedia."""
    if ch in _EMOJI_CACHE:
        return _EMOJI_CACHE[ch]
    base = None
    for path, size in _EMOJI_FONTS:
        if not os.path.exists(path):
            continue
        try:
            font = ImageFont.truetype(path, size)
            canvas = Image.new("RGBA", (size * 4, size * 3), (0, 0, 0, 0))
            ImageDraw.Draw(canvas).text((size // 2, size // 2), ch, font=font, embedded_color=True)
            bb = canvas.getbbox()
            if not bb:
                continue
            spr = canvas.crop(bb)
            sc = 400.0 / max(spr.size)
            spr = spr.resize((max(1, int(spr.width * sc)), max(1, int(spr.height * sc))), Image.Resampling.LANCZOS)
            pad = 22
            c2 = Image.new("RGBA", (spr.width + pad * 2, spr.height + pad * 2), (0, 0, 0, 0))
            c2.alpha_composite(spr, (pad, pad))
            dil = c2.getchannel("A").filter(ImageFilter.MaxFilter(2 * 11 + 1))
            outline = Image.new("RGBA", c2.size, (26, 26, 26, 255))
            outline.putalpha(dil)
            base = Image.alpha_composite(outline, c2)
            break
        except Exception:
            continue
    _EMOJI_CACHE[ch] = base
    return base


def emoji_prop(g, x, y, s, t, ch):
    drift = math.sin(t * 1.4) * 18 * s
    bob = math.sin(t * 2.6) * 10 * s
    base = _emoji_base(ch)
    if base is None:
        g.ellipse(x - 60 * s, y - 60 * s, x + 60 * s, y + 60 * s, fill=YEL, outline=K, w=5)
        g.text(x, y, "?", 80 * s, fill=K)
        return
    target = 200 * s * g.s * (1 + 0.04 * math.sin(t * 5))
    sc = target / float(max(base.size))
    w, h = max(2, int(base.width * sc)), max(2, int(base.height * sc))
    spr = base.resize((w, h), Image.Resampling.BILINEAR).rotate(
        math.sin(t * 2.0) * 7, expand=True, resample=Image.Resampling.BICUBIC)
    cx, cy = g.P(x + drift, y + bob)
    x0, y0 = int(cx - spr.width / 2), int(cy - spr.height / 2)
    region = g.img.crop((x0, y0, x0 + spr.width, y0 + spr.height))
    g.img.paste(Image.alpha_composite(region, spr), (x0, y0))


def get_prop(name):
    """Mengembalikan (fungsi_gambar, jenis) untuk nama properti, termasuk 'emoji:X'."""
    if name.startswith("emoji:"):
        ch = name[6:]
        return (lambda g, x, y, s, t: emoji_prop(g, x, y, s, t, ch)), "high"
    return PROPS[name]


PROPS = {
    "money_pile": (money_pile, "ground"), "shopping_cart": (shopping_cart, "ground"),
    "bank_building": (bank_building, "ground"), "printing_machine": (printing_machine, "ground"),
    "laptop": (laptop, "ground"), "house": (house, "ground"), "fire": (fire, "ground"), "trophy": (trophy, "ground"),
    "chart_down": (chart_down, "high"), "chart_up": (chart_up, "high"), "wallet_empty": (wallet_empty, "high"),
    "bread": (bread, "high"), "price_tag": (price_tag, "high"), "coins": (coins, "high"),
    "lightbulb": (lightbulb, "high"), "question_marks": (question_marks, "high"), "clock": (clock, "high"),
    "phone": (phone, "high"), "book": (book, "high"), "globe": (globe, "high"), "rocket": (rocket, "high"),
    "heart": (heart_prop, "high"), "warning": (warning, "high"), "boom": (boom, "high"), "gear": (gear, "high"),
    "balance_scale": (balance_scale, "high"), "zzz": (zzz, "high"), "battery": (battery, "high"),
    "briefcase": (briefcase, "high"), "storm_cloud": (storm_cloud, "high"),
    "banknotes_rain": (banknotes_rain, "area"),
}


def normalize_prop(name):
    raw = str(name or "").strip()
    n = raw.lower().replace(" ", "_").replace("-", "_")
    if n in PROPS:
        return n
    # emoji langsung (mis. "🐙")
    if raw and any(ord(c) > 0x2000 for c in raw):
        return "emoji:" + raw
    if raw.startswith("emoji:"):
        return raw
    if "rain" in n and ("money" in n or "cash" in n or "bill" in n):
        return "banknotes_rain"
    # kata benda/hewan umum -> ikon berwarna
    import re
    for tok in re.findall(r"[a-z]+", n):
        for cand in (tok, tok[:-1] if tok.endswith("s") else tok):
            if cand in EMOJI_WORDS:
                return "emoji:" + EMOJI_WORDS[cand]
    rules = [
        (("banknote",), "banknotes_rain"),
        (("print",), "printing_machine"), (("money", "cash", "rich", "gold", "treasure"), "money_pile"),
        (("crash", "drop", "fall", "decline", "down", "recession", "crisis"), "chart_down"),
        (("chart", "graph", "stock", "grow", "rise", "profit"), "chart_up"),
        (("bank",), "bank_building"), (("wallet", "empty", "broke", "poor"), "wallet_empty"),
        (("cart", "shop", "groc", "market"), "shopping_cart"), (("bread", "food", "meal", "eat"), "bread"),
        (("tag", "price", "inflat"), "price_tag"), (("coin",), "coins"),
        (("idea", "bulb", "light", "solution", "smart"), "lightbulb"),
        (("question", "confus", "mystery", "why"), "question_marks"),
        (("clock", "time", "deadline", "alarm"), "clock"), (("laptop", "computer", "work", "code", "desk"), "laptop"),
        (("phone", "social", "scroll", "media"), "phone"), (("book", "study", "read", "learn", "school"), "book"),
        (("earth", "world", "globe", "global"), "globe"), (("house", "home", "property"), "house"),
        (("fire", "burn", "flame"), "fire"), (("rocket", "launch", "space"), "rocket"),
        (("trophy", "win", "champion", "success"), "trophy"), (("heart", "love"), "heart"),
        (("warn", "danger", "risk", "alert"), "warning"), (("boom", "explo", "bomb", "war", "blast"), "boom"),
        (("gear", "system", "process", "machine"), "gear"), (("scale", "balance", "law", "justice", "compare"), "balance_scale"),
        (("sleep", "zzz", "night", "rest"), "zzz"), (("battery", "energy", "tired", "exhaust"), "battery"),
        (("case", "job", "business", "career"), "briefcase"), (("storm", "cloud", "sad", "rainy"), "storm_cloud"),
    ]
    for keys, target in rules:
        if any(k in n for k in keys):
            return target
    return None
