"""
Inti engine animasi Stickman Explainer (Lanskap 16:9 Sinematik HD 1280x720):
- Kanvas gambar anti-alias (supersampling 2x -> 2560x1440 di-downsample ke 1280x720)
- 13 Latar belakang widescreen 16:9 detail (kota, kantor, bank, pasar, rumah, alam, luar angkasa, kastil, laut, langit, lab, gurun, polos)
- Karakter stickman kaos biru dengan pose, ekspresi, topi, jas & auto lip-sync
"""
import math
import random
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720          # Resolusi Widescreen Long Video 16:9 (HD)
S = 2                     # Supersampling 2x untuk garis tajam
FLOOR_Y = 535             # Garis lantai widescreen
GROUND_Y = 578            # Tempat kaki karakter & properti berpijak
DYN_TOP = 20              # Area layer dinamis
DYN_H = 600
K = "#1a1a1a"             # Warna garis outline tebal

RED = "#e63946"
YEL = "#ffd166"
BLUE = "#5aa9e6"


@lru_cache(maxsize=64)
def get_font(size):
    size = max(8, int(size))
    for fp in (
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/tahomabd.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(fp, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size)
    except Exception:
        return ImageFont.load_default()


class G:
    """Kuas gambar widescreen 1280x720 dengan supersampling."""

    def __init__(self, img, s=S, ox=0, oy=0, lw=1.0):
        self.img = img
        self.d = ImageDraw.Draw(img)
        self.s = s
        self.ox = ox
        self.oy = oy
        self.lw = lw          # pengali ketebalan garis (mode sketsa memakai garis tipis)

    def P(self, x, y):
        return ((x - self.ox) * self.s, (y - self.oy) * self.s)

    def B(self, x1, y1, x2, y2):
        ax, ay = self.P(x1, y1)
        bx, by = self.P(x2, y2)
        return [min(ax, bx), min(ay, by), max(ax, bx), max(ay, by)]

    def _w(self, w):
        return max(1, int(round(w * self.s * self.lw))) if w else 0

    def line(self, pts, fill=K, w=5, caps=True):
        P = [self.P(*q) for q in pts]
        self.d.line(P, fill=fill, width=self._w(w), joint="curve")
        if caps:
            r = self._w(w) / 2.0
            for q in (P[0], P[-1]):
                self.d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=fill)

    def ellipse(self, x1, y1, x2, y2, fill=None, outline=K, w=4):
        self.d.ellipse(self.B(x1, y1, x2, y2), fill=fill,
                       outline=outline if w else None, width=max(1, self._w(w)))

    def rect(self, x1, y1, x2, y2, fill=None, outline=K, w=4):
        self.d.rectangle(self.B(x1, y1, x2, y2), fill=fill,
                         outline=outline if w else None, width=max(1, self._w(w)))

    def rrect(self, x1, y1, x2, y2, r=8, fill=None, outline=K, w=4):
        r = max(0.5, min(r, abs(x2 - x1) / 2.0, abs(y2 - y1) / 2.0))
        self.d.rounded_rectangle(self.B(x1, y1, x2, y2), radius=r * self.s, fill=fill,
                                 outline=outline if w else None, width=max(1, self._w(w)))

    def poly(self, pts, fill=None, outline=K, w=4):
        P = [self.P(*q) for q in pts]
        if fill:
            self.d.polygon(P, fill=fill)
        if outline and w:
            self.d.line(P + [P[0]], fill=outline, width=self._w(w), joint="curve")

    def arc(self, x1, y1, x2, y2, a0, a1, fill=K, w=4):
        self.d.arc(self.B(x1, y1, x2, y2), a0, a1, fill=fill, width=max(1, self._w(w)))

    def text(self, x, y, txt, size, fill=K, stroke=0, stroke_fill=K, anchor="mm"):
        self.d.text(self.P(x, y), txt, font=get_font(size * self.s), fill=fill, anchor=anchor,
                    stroke_width=int(round(stroke * self.s)), stroke_fill=stroke_fill)


def rot_rect(cx, cy, w, h, ang):
    a = math.radians(ang)
    c, s = math.cos(a), math.sin(a)
    return [(cx + dx * c - dy * s, cy + dx * s + dy * c)
            for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]


def rot_pts(pts, cx, cy, ang):
    a = math.radians(ang)
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


# =============================================================================
# LATAR BELAKANG WIDESCREEN 16:9 (1280 x 720)
# =============================================================================
def _gradient(g, y1, y2, c1, c2, step=6):
    for y in range(int(y1), int(y2), step):
        r = (y - y1) / float(max(1, y2 - y1))
        col = tuple(int(c1[i] * (1 - r) + c2[i] * r) for i in range(3))
        g.rect(-5, y, W + 5, y + step + 1, fill=col, outline=None, w=0)


def _cloud(g, x, y, sc=1.0):
    parts = [(0, 0, 60, 34), (-44, 10, 44, 26), (46, 12, 46, 26), (-12, -18, 36, 28)]
    for dx, dy, rx, ry in parts:
        g.ellipse(x + (dx - rx) * sc, y + (dy - ry) * sc, x + (dx + rx) * sc, y + (dy + ry) * sc,
                  fill="#ffffff", outline=K, w=4)
    for dx, dy, rx, ry in parts:
        g.ellipse(x + (dx - rx) * sc + 3, y + (dy - ry) * sc + 3,
                  x + (dx + rx) * sc - 3, y + (dy + ry) * sc - 3, fill="#ffffff", outline=None, w=0)


def _floor(g, color, line, top=FLOOR_Y):
    g.rect(-10, top, W + 10, H + 10, fill=color, outline=K, w=5)
    for y in range(top + 48, H, 55):
        g.line([(0, y), (W, y)], fill=line, w=3, caps=False)


def _windows(g, x, y, w, h, cols, rows, color="#fff1b8"):
    cw = w / float(cols)
    rh = h / float(rows)
    for r in range(rows):
        for c in range(cols):
            g.rect(x + c * cw + cw * 0.22, y + r * rh + rh * 0.2,
                   x + c * cw + cw * 0.78, y + r * rh + rh * 0.65, fill=color, outline=K, w=2)


def _bg_city(g):
    _gradient(g, 0, FLOOR_Y, (120, 196, 245), (255, 238, 214))
    g.ellipse(1060, 60, 1170, 170, fill="#ffe27a", outline=K, w=5)
    _cloud(g, 200, 110, 1.0)
    _cloud(g, 640, 140, 0.85)
    _cloud(g, 920, 95, 0.75)
    buildings = [
        (-10, 140, 310, "#cdb4db"), (120, 130, 240, "#ffc8dd"), (240, 160, 360, "#bde0fe"),
        (390, 130, 270, "#a2d2ff"), (510, 160, 330, "#ffafcc"), (660, 140, 250, "#cdb4db"),
        (790, 165, 350, "#bde0fe"), (945, 140, 280, "#ffc8dd"), (1075, 150, 320, "#a2d2ff"),
        (1210, 100, 260, "#cdb4db")
    ]
    for x, w, h, col in buildings:
        g.rect(x, FLOOR_Y - h, x + w, FLOOR_Y, fill=col, outline=K, w=4)
        _windows(g, x + 8, FLOOR_Y - h + 18, w - 16, h - 40, max(2, int(w / 40)), max(3, int(h / 55)))
    _floor(g, "#d9d2c5", "#c4bcad")
    for x in range(30, W, 140):
        g.rect(x, 625, x + 75, 640, fill="#f1ede4", outline=None, w=0)


def _bg_indoor(g):
    g.rect(-5, 0, W + 5, FLOOR_Y, fill="#f3e9dc", outline=None, w=0)
    # Jendela kiri
    g.rect(70, 90, 340, 360, fill="#dff3fb", outline=K, w=6)
    g.line([(205, 90), (205, 360)], w=5, caps=False)
    g.line([(70, 225), (340, 225)], w=5, caps=False)
    g.rect(55, 360, 355, 382, fill="#d4a373", outline=K, w=5)
    # Tanaman pot
    g.poly([(165, 325), (235, 325), (225, 360), (175, 360)], fill="#e07a5f", outline=K, w=4)
    g.ellipse(170, 265, 230, 330, fill="#81b29a", outline=K, w=4)
    # Lukisan dinding tengah-kanan
    g.rect(520, 100, 780, 270, fill="#ffffff", outline=K, w=6)
    g.rect(538, 118, 762, 252, fill="#ffd6a5", outline=K, w=3)
    g.ellipse(600, 145, 700, 220, fill="#f4a261", outline=K, w=3)
    # Rak buku kanan
    g.rect(900, 140, 1190, 360, fill="#d4a373", outline=K, w=5)
    g.line([(900, 250), (1190, 250)], w=5, caps=False)
    for bx, col in ((925, "#e63946"), (960, "#2a9d8f"), (995, "#ffd166"), (1060, "#5aa9e6"), (1100, "#9b5de5")):
        g.rect(bx, 165, bx + 28, 250, fill=col, outline=K, w=3)
    _floor(g, "#c68b59", "#a9714b")


def _bg_office(g):
    g.rect(-5, 0, W + 5, FLOOR_Y, fill="#dbe4ee", outline=None, w=0)
    g.rect(120, 70, 1160, 370, fill="#bfe3f7", outline=K, w=7)
    skyline = [
        (150, 110, 160, "#8ecae6"), (270, 95, 220, "#6fb6dc"), (380, 130, 180, "#8ecae6"),
        (520, 110, 240, "#6fb6dc"), (640, 140, 170, "#8ecae6"), (790, 120, 210, "#6fb6dc"),
        (920, 110, 190, "#8ecae6"), (1040, 95, 230, "#6fb6dc")
    ]
    for x, w, h, col in skyline:
        g.rect(x, 370 - h, x + w, 370, fill=col, outline=K, w=3)
    g.line([(465, 70), (465, 370)], w=6, caps=False)
    g.line([(815, 70), (815, 370)], w=6, caps=False)
    g.line([(120, 220), (1160, 220)], w=6, caps=False)
    _floor(g, "#8d99ae", "#7b869b")


def _bg_bank(g):
    g.rect(-5, 0, W + 5, FLOOR_Y, fill="#f1e4c8", outline=None, w=0)
    for x in (90, 370, 650, 930):
        g.rect(x, 85, x + 130, FLOOR_Y, fill="#fbf5e6", outline=K, w=5)
        g.rect(x - 14, 65, x + 144, 100, fill="#e9dcc0", outline=K, w=5)
        for ly in range(120, FLOOR_Y - 40, 100):
            g.line([(x + 30, ly), (x + 30, ly + 60)], fill="#d9c9a5", w=3, caps=False)
    g.rect(-5, 0, W + 5, 65, fill="#e9dcc0", outline=K, w=5)
    for i, x in enumerate(range(-20, W + 80, 110)):
        g.rect(x, FLOOR_Y, x + 110, H + 10, fill="#f8f3ea" if i % 2 == 0 else "#b8a98a", outline=K, w=3)
    g.rect(-10, FLOOR_Y, W + 10, FLOOR_Y + 8, fill="#6b5b45", outline=K, w=4)


def _bg_market(g):
    g.rect(-5, 0, W + 5, FLOOR_Y, fill="#fdf0d5", outline=None, w=0)
    cols = ["#e63946", "#f4a261", "#2a9d8f", "#ffd166", "#5aa9e6", "#9b5de5"]
    for row, y in enumerate((110, 250, 390)):
        g.rect(-5, y + 85, W + 5, y + 102, fill="#a9714b", outline=K, w=4)
        for i in range(0, W, 68):
            c = cols[(i // 68 + row * 2) % len(cols)]
            hh = 45 + ((i // 68) * 17 + row * 11) % 30
            g.rrect(i + 8, y + 85 - hh, i + 56, y + 85, r=6, fill=c, outline=K, w=3)
    g.rect(-5, 40, W + 5, 75, fill="#e63946", outline=K, w=5)
    _floor(g, "#e9ecef", "#ced4da")


def _bg_nature(g):
    _gradient(g, 0, FLOOR_Y, (140, 205, 250), (230, 247, 255))
    g.ellipse(90, 60, 190, 160, fill="#ffe27a", outline=K, w=5)
    _cloud(g, 460, 110, 1.0)
    _cloud(g, 920, 135, 0.9)
    g.ellipse(-180, 360, 560, 720, fill="#95d5b2", outline=K, w=5)
    g.ellipse(420, 380, 1400, 740, fill="#74c69d", outline=K, w=5)
    for x, y in ((140, 390), (620, 400), (1040, 385), (1160, 420)):
        g.rect(x - 9, y, x + 9, y + 100, fill="#a9714b", outline=K, w=4)
        g.ellipse(x - 52, y - 90, x + 52, y + 20, fill="#52b788", outline=K, w=5)
    _floor(g, "#8ac926", "#6fa51d")


def _bg_space(g):
    _gradient(g, 0, FLOOR_Y, (14, 16, 48), (60, 40, 110))
    rnd = random.Random(7)
    for _ in range(95):
        x, y, r = rnd.randint(5, W - 5), rnd.randint(5, FLOOR_Y - 30), rnd.choice((2, 2, 3, 4))
        g.ellipse(x - r, y - r, x + r, y + r, fill="#ffffff", outline=None, w=0)
    g.ellipse(920, 80, 1110, 270, fill="#f4a261", outline=K, w=6)
    g.arc(870, 135, 1160, 215, 200, 340, fill=K, w=6)
    g.ellipse(140, 130, 225, 215, fill="#8ecae6", outline=K, w=5)
    _floor(g, "#9aa0b4", "#868ca3")
    for x, y, r in ((180, 610, 46), (640, 650, 62), (1040, 600, 40)):
        g.ellipse(x - r, y - r * 0.4, x + r, y + r * 0.4, fill="#868ca3", outline=K, w=3)


def _bg_castle(g):
    g.rect(-5, 0, W + 5, FLOOR_Y, fill="#b8bcc7", outline=None, w=0)
    for row, y in enumerate(range(0, FLOOR_Y, 65)):
        g.line([(0, y), (W, y)], fill="#8e93a1", w=3, caps=False)
        for x in range(-40 if row % 2 else 0, W, 115):
            g.line([(x, y), (x, y + 65)], fill="#8e93a1", w=3, caps=False)
    for wx in (360, 760):
        g.rrect(wx, 110, wx + 160, 380, r=75, fill="#2b2d42", outline=K, w=7)
        g.rrect(wx + 18, 128, wx + 142, 362, r=60, fill="#8ecae6", outline=None, w=0)
    for x in (110, 1080):
        g.poly([(x, 85), (x + 90, 85), (x + 90, 310), (x + 45, 275), (x, 310)], fill=RED, outline=K, w=5)
        g.ellipse(x + 25, 145, x + 65, 185, fill=YEL, outline=K, w=3)
    _floor(g, "#8d8a99", "#7a7788")


def _bg_ocean(g):
    _gradient(g, 0, FLOOR_Y, (88, 196, 220), (14, 90, 140))
    rnd = random.Random(11)
    for _ in range(36):
        x, y, r = rnd.randint(10, W - 10), rnd.randint(30, FLOOR_Y - 30), rnd.choice((6, 9, 12, 16))
        g.ellipse(x - r, y - r, x + r, y + r, fill="#bdeaf5", outline="#e8f9ff", w=2)
    for x, h in ((70, 170), (160, 120), (1060, 185), (1160, 135)):
        g.poly([(x, FLOOR_Y), (x - 26, FLOOR_Y - h * 0.5), (x + 6, FLOOR_Y - h * 0.8), (x - 8, FLOOR_Y - h),
                (x + 30, FLOOR_Y - h * 0.6), (x + 14, FLOOR_Y - h * 0.3), (x + 34, FLOOR_Y)], fill="#2a9d8f", outline=K, w=4)
    g.rect(-10, FLOOR_Y, W + 10, H + 10, fill="#e9c46a", outline=K, w=5)
    for x, y, r in ((180, 620, 40), (680, 650, 56), (1050, 615, 34)):
        g.ellipse(x - r, y - r * 0.5, x + r, y + r * 0.5, fill="#d4a24c", outline=K, w=3)


def _bg_sky(g):
    _gradient(g, 0, FLOOR_Y, (70, 150, 235), (200, 232, 252))
    g.ellipse(1040, 65, 1160, 185, fill="#ffe27a", outline=K, w=5)
    for x, y, sc in ((180, 130, 1.1), (560, 200, 0.95), (860, 140, 0.85), (340, 320, 0.9), (980, 340, 0.8)):
        _cloud(g, x, y, sc)
    g.rect(-10, FLOOR_Y, W + 10, H + 10, fill="#f4faff", outline=K, w=5)
    for x in range(-20, W + 80, 120):
        g.ellipse(x - 20, FLOOR_Y - 35, x + 110, FLOOR_Y + 35, fill="#f4faff", outline=K, w=4)
    g.rect(-10, FLOOR_Y + 2, W + 10, H + 10, fill="#f4faff", outline=None, w=0)


def _bg_lab(g):
    g.rect(-5, 0, W + 5, FLOOR_Y, fill="#e0f2ef", outline=None, w=0)
    g.rect(70, 85, 420, 310, fill="#ffffff", outline=K, w=5)
    for i, col in enumerate(("#e63946", "#2a9d8f", "#ffd166", "#5aa9e6", "#9b5de5", "#f4a261")):
        x, y = 95 + (i % 3) * 105, 110 + (i // 3) * 95
        g.rect(x, y, x + 75, y + 72, fill=col, outline=K, w=3)
        g.text(x + 37, y + 36, "H" if i % 2 else "Fe", 22, fill="#ffffff")
    g.rect(780, 85, 1180, 360, fill="#cdeffd", outline=K, w=6)
    g.line([(980, 85), (980, 360)], w=5, caps=False)
    g.line([(780, 222), (1180, 222)], w=5, caps=False)
    for r_i, y in enumerate(range(FLOOR_Y, H + 60, 65)):
        for c_i, x in enumerate(range(-20, W + 80, 100)):
            xx = x + (50 if r_i % 2 else 0)
            g.rect(xx, y, xx + 100, y + 65, fill="#ffffff" if (r_i + c_i) % 2 == 0 else "#ced4da", outline=K, w=3)
    g.rect(-10, FLOOR_Y, W + 10, FLOOR_Y + 8, fill="#6c757d", outline=K, w=4)


def _bg_desert(g):
    _gradient(g, 0, FLOOR_Y, (255, 190, 120), (255, 238, 190))
    g.ellipse(100, 70, 220, 190, fill="#fff3b0", outline=K, w=5)
    g.poly([(520, FLOOR_Y - 10), (720, FLOOR_Y - 260), (920, FLOOR_Y - 10)], fill="#e9c46a", outline=K, w=5)
    g.poly([(860, FLOOR_Y - 10), (990, FLOOR_Y - 170), (1120, FLOOR_Y - 10)], fill="#d4a24c", outline=K, w=5)
    g.rect(220, 340, 248, 520, fill="#52b788", outline=K, w=5)
    g.rect(180, 400, 220, 424, fill="#52b788", outline=K, w=4)
    g.rect(248, 385, 290, 409, fill="#52b788", outline=K, w=4)
    _floor(g, "#f2cc8f", "#dfb677")


def _bg_plain(g):
    _gradient(g, 0, FLOOR_Y, (255, 244, 224), (255, 226, 190))
    g.ellipse(440, 80, 840, 440, fill="#ffe8cc", outline=None, w=0)
    _floor(g, "#e9c9a0", "#d8b183")


BACKGROUNDS = {
    "city": _bg_city, "indoor": _bg_indoor, "office": _bg_office, "bank": _bg_bank,
    "market": _bg_market, "nature": _bg_nature, "space": _bg_space, "castle": _bg_castle,
    "ocean": _bg_ocean, "sky": _bg_sky, "lab": _bg_lab, "desert": _bg_desert,
    "plain": _bg_plain,
}

_BG_CACHE = {}

_SETTING_WORDS = {
    "bank": "bank", "vault": "bank", "market": "market", "shop": "market", "store": "market", "supermarket": "market",
    "office": "office", "company": "office", "business": "office", "school": "indoor", "class": "indoor",
    "classroom": "indoor", "home": "indoor", "house": "indoor", "room": "indoor", "bed": "indoor",
    "bedroom": "indoor", "kitchen": "indoor", "indoor": "indoor", "space": "space", "galaxy": "space",
    "planet": "space", "universe": "space", "castle": "castle", "palace": "castle", "history": "castle",
    "kingdom": "castle", "battlefield": "castle", "war": "castle", "nature": "nature", "forest": "nature",
    "jungle": "nature", "park": "nature", "outdoor": "nature", "farm": "nature", "mountain": "nature",
    "city": "city", "street": "city", "town": "city", "road": "city", "ocean": "ocean", "sea": "ocean",
    "underwater": "ocean", "beach": "ocean", "lake": "ocean", "river": "ocean", "sky": "sky", "air": "sky",
    "airport": "sky", "plane": "sky", "flight": "sky", "cloud": "sky", "clouds": "sky", "lab": "lab",
    "laboratory": "lab", "science": "lab", "chemistry": "lab", "research": "lab", "hospital": "lab",
    "desert": "desert", "egypt": "desert", "pyramid": "desert", "sahara": "desert", "ancient": "desert",
}


def normalize_setting(name):
    import re
    n = str(name or "").lower()
    if n in BACKGROUNDS:
        return n
    for tok in re.findall(r"[a-z]+", n):
        if tok in _SETTING_WORDS:
            return _SETTING_WORDS[tok]
    return "plain"


def make_background(setting):
    setting = normalize_setting(setting)
    if setting not in _BG_CACHE:
        img = Image.new("RGB", (W * S, H * S), "#f3e9dc")
        g = G(img, S)
        BACKGROUNDS[setting](g)
        _BG_CACHE[setting] = img.reduce(S)
    return _BG_CACHE[setting].copy()


# =============================================================================
# KARAKTER STICKMAN
# =============================================================================
def _limb(sx, sy, sgn, a1, a2, l1=58, l2=56):
    r1 = math.radians(a1)
    ex, ey = sx + sgn * l1 * math.sin(r1), sy + l1 * math.cos(r1)
    r2 = math.radians(a2)
    return (ex, ey), (ex + sgn * l2 * math.sin(r2), ey + l2 * math.cos(r2))


def arm_angles(pose, t, amp, speaking):
    s = math.sin
    if pose == "point":
        return (96 + s(t * 3) * 3, 96), (14 + s(t * 1.7) * 3, 8)
    if pose == "panic":
        a = s(t * 20) * 10
        return (150 + a, 172 - a), (150 - a, 172 + a)
    if pose == "shrug":
        return (62, 138 + s(t * 3) * 6), (62, 138 - s(t * 3) * 6)
    if pose == "cry":
        return (28, -155), (28, -155)
    if pose == "celebrate":
        j = s(t * 5) * 12
        return (150 + j, 165), (150 - j, 165)
    if pose == "think":
        return (24, -150), (14 + s(t * 1.7) * 3, 8)
    if pose == "idle":
        return (12 + s(t * 1.6) * 3, 6), (12 + s(t * 1.6) * 3, 6)
    g1 = s(t * 2.7) * 16
    boost = amp * 22 if speaking else 0
    return (58 + g1 + boost, 118 + g1 * 1.4 + boost), (16 + s(t * 2.1) * 6, 8)


def _dome(cx, y, rx, ry):
    return [(cx + rx * math.cos(math.radians(a)), y + ry * math.sin(math.radians(a))) for a in range(180, 361, 12)]


def _draw_hat(g, hat, cx, ht):
    if hat == "tophat":
        g.rrect(cx - 36, ht - 56, cx + 36, ht + 6, r=4, fill="#2b2d42", outline=K, w=4)
        g.rect(cx - 36, ht - 14, cx + 36, ht + 2, fill=RED, outline=K, w=3)
        g.rrect(cx - 58, ht - 2, cx + 58, ht + 12, r=6, fill="#2b2d42", outline=K, w=4)
    elif hat == "crown":
        pts = [(cx - 44, ht + 8), (cx - 48, ht - 36), (cx - 20, ht - 14), (cx, ht - 44),
               (cx + 20, ht - 14), (cx + 48, ht - 36), (cx + 44, ht + 8)]
        g.poly(pts, fill=YEL, outline=K, w=4)
        g.ellipse(cx - 6, ht - 28, cx + 6, ht - 16, fill=RED, outline=K, w=2)
    elif hat == "hardhat":
        g.poly(_dome(cx, ht + 14, 52, 46), fill=YEL, outline=K, w=4)
        g.rrect(cx - 64, ht + 8, cx + 64, ht + 22, r=6, fill=YEL, outline=K, w=4)
        g.line([(cx, ht - 30), (cx, ht + 8)], fill=K, w=3, caps=False)
    elif hat == "cap":
        g.poly(_dome(cx, ht + 14, 52, 44), fill="#e63946", outline=K, w=4)
        g.rrect(cx + 10, ht + 6, cx + 78, ht + 20, r=6, fill="#c1121f", outline=K, w=4)
    elif hat == "graduate":
        g.poly([(cx - 66, ht - 6), (cx, ht - 30), (cx + 66, ht - 6), (cx, ht + 14)], fill="#22223b", outline=K, w=4)
        g.rrect(cx - 34, ht + 4, cx + 34, ht + 22, r=4, fill="#22223b", outline=K, w=3)
        g.line([(cx + 50, ht - 8), (cx + 56, ht + 26)], fill=YEL, w=4)
    elif hat == "police":
        g.poly(_dome(cx, ht + 12, 54, 40), fill="#1d3557", outline=K, w=4)
        g.rrect(cx - 60, ht + 6, cx + 60, ht + 18, r=5, fill="#14213d", outline=K, w=4)
        g.ellipse(cx - 9, ht - 16, cx + 9, ht + 2, fill=YEL, outline=K, w=2)


def draw_character(g, cx, ground, t, amp, speaking, pose="talk", emotion="neutral",
                   hat="none", outfit="tshirt", face=1):
    shirt = BLUE if outfit == "tshirt" else "#3d405b"
    bob = math.sin(t * 2.4) * 2
    jump = abs(math.sin(t * 5.0)) * 32 if pose == "celebrate" else 0.0
    cx = cx + (math.sin(t * 28) * 3.5 if pose == "panic" else 0)
    if speaking:
        bob -= amp * 4
    base = ground - jump
    hip_y = base - 122
    top = hip_y - 114 + bob
    sh_y = top + 24
    head_cy = top - 44
    HR = 56

    g.ellipse(cx - 70, ground - 8, cx + 70, ground + 12, fill=(0, 0, 0, 50), outline=None, w=0)

    wob = math.sin(t * 26) * 5 if pose == "panic" else 0
    for sgn in (-1, 1):
        fx = cx + sgn * (30 + (7 if pose == "celebrate" else 0)) + wob * sgn
        g.line([(cx + sgn * 15, hip_y), (fx, base - 6)], fill=K, w=10)
        g.ellipse(fx - 16 + face * 5, base - 12, fx + 16 + face * 5, base + 4, fill=K, outline=None, w=0)

    g.rrect(cx - 44, top, cx + 44, hip_y + 10, r=30, fill=shirt, outline=K, w=5)
    if outfit == "suit":
        g.poly([(cx - 14, top + 2), (cx + 14, top + 2), (cx, top + 46)], fill="#ffffff", outline=K, w=3)
        g.poly([(cx - 5, top + 14), (cx + 5, top + 14), (cx + 8, top + 60), (cx, top + 72), (cx - 8, top + 60)],
               fill=RED, outline=K, w=3)

    act, pas = arm_angles(pose, t, amp, speaking)
    angs = {1: act, -1: pas} if face == 1 else {1: pas, -1: act}
    for sgn in (-1, 1):
        sx, sy = cx + sgn * 38, sh_y + 4
        (a1, a2) = angs[sgn]
        e, h = _limb(sx, sy, sgn, a1, a2)
        g.line([(sx, sy), e, h], fill=K, w=9)
        g.ellipse(h[0] - 8, h[1] - 8, h[0] + 8, h[1] + 8, fill=K, outline=None, w=0)
        g.ellipse(sx - 17, sy - 15, sx + 17, sy + 19, fill=shirt, outline=K, w=4)

    g.ellipse(cx - HR, head_cy - HR, cx + HR, head_cy + HR, fill="#ffffff", outline=K, w=6)

    ex = cx + face * 7
    ey = head_cy - 6
    blink = (t % 3.4) < 0.12
    for sgn in (-1, 1):
        x = ex + sgn * 20
        if blink:
            g.line([(x - 8, ey), (x + 8, ey)], w=4)
        elif emotion == "happy":
            g.arc(x - 10, ey - 6, x + 10, ey + 14, 200, 340, w=4)
        elif emotion == "shocked":
            g.ellipse(x - 12, ey - 13, x + 12, ey + 13, fill="#ffffff", outline=K, w=3)
            g.ellipse(x - 3 + face * 3, ey - 3, x + 3 + face * 3, ey + 3, fill=K, outline=None, w=0)
        else:
            g.ellipse(x - 5, ey - 6, x + 5, ey + 6, fill=K, outline=None, w=0)
        if emotion == "sad":
            y1, y2 = (ey - 14, ey - 25) if sgn == -1 else (ey - 25, ey - 14)
            g.line([(x - 11, y1), (x + 11, y2)], w=4)
        elif emotion == "angry":
            y1, y2 = (ey - 27, ey - 15) if sgn == -1 else (ey - 15, ey - 27)
            g.line([(x - 11, y1), (x + 11, y2)], w=5)
        elif emotion == "shocked":
            g.arc(x - 12, ey - 36, x + 12, ey - 20, 200, 340, w=4)
        elif emotion == "thinking":
            if sgn == 1:
                g.arc(x - 12, ey - 36, x + 12, ey - 20, 200, 340, w=4)
            else:
                g.line([(x - 11, ey - 23), (x + 11, ey - 23)], w=4)
        elif emotion == "happy":
            pass
        else:
            g.line([(x - 10, ey - 22), (x + 10, ey - 22)], w=3)

    mx, my = cx + face * 9, head_cy + 28
    if speaking and amp > 0.12:
        ow, oh = 11 + amp * 8, 4 + amp * 21
        g.rrect(mx - ow, my - 4, mx + ow, my + oh, r=9, fill="#c1121f", outline=K, w=4)
        if amp > 0.45:
            g.ellipse(mx - ow * 0.55, my + oh - 9, mx + ow * 0.55, my + oh + 1, fill="#f28482", outline=None, w=0)
    else:
        if emotion == "happy":
            g.arc(mx - 18, my - 12, mx + 18, my + 12, 15, 165, w=4)
        elif emotion in ("sad", "angry"):
            g.arc(mx - 16, my + 2, mx + 16, my + 20, 200, 340, w=4)
        elif emotion == "shocked":
            g.ellipse(mx - 9, my - 3, mx + 9, my + 17, fill="#c1121f", outline=K, w=4)
        elif emotion == "thinking":
            g.line([(mx - 10, my + 6), (mx + 12, my + 2)], w=4)
        else:
            g.line([(mx - 12, my + 4), (mx + 12, my + 4)], w=4)

    if emotion == "sad" or pose == "cry":
        for sgn in (-1, 1):
            for k in range(2):
                ph = (t * 0.9 + k * 0.5 + (0.2 if sgn == 1 else 0)) % 1.0
                tx, ty = ex + sgn * 24, ey + 10 + ph * 50
                g.ellipse(tx - 5, ty - 5, tx + 5, ty + 9, fill="#7bdff2", outline=K, w=2)
    if pose == "panic":
        ph = (t * 1.6) % 1.0
        g.ellipse(cx + 62, head_cy - 36 + ph * 40, cx + 76, head_cy - 10 + ph * 40, fill="#7bdff2", outline=K, w=3)
        ph = (t * 1.6 + 0.5) % 1.0
        g.ellipse(cx - 76, head_cy - 36 + ph * 40, cx - 62, head_cy - 10 + ph * 40, fill="#7bdff2", outline=K, w=3)

    _draw_hat(g, hat, cx, head_cy - HR)
