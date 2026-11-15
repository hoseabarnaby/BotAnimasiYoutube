"""Penyusun adegan: memilih latar, properti, pose, ekspresi sesuai narasi, lalu menggambar tiap frame."""
import math
from PIL import Image
from stick_core import (
    G, W, H, S, DYN_TOP, DYN_H, GROUND_Y, make_background, draw_character, normalize_setting,
)
from stick_props import get_prop, normalize_prop

POSES = {"idle", "talk", "point", "panic", "shrug", "cry", "celebrate", "think"}
EMOTIONS = {"neutral", "happy", "sad", "shocked", "angry", "thinking"}
HATS = {"none", "tophat", "crown", "hardhat", "cap", "graduate", "police"}
OUTFITS = {"tshirt", "suit"}
DEFAULT_POSES = ["talk", "point", "shrug", "think", "talk", "celebrate"]

# Slot penempatan (untuk karakter di kiri; otomatis dicerminkan jika karakter di kanan)
GROUND_SLOT = (535, GROUND_Y)
HIGH_SLOTS_WITH_GROUND = [(430, 360, 1.0), (175, 260, 0.75), (580, 205, 0.7)]
HIGH_SLOTS_NO_GROUND = [(505, 520, 1.25), (190, 300, 0.8), (565, 250, 0.75)]


def ease_back(p):
    p = max(0.0, min(1.0, p))
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2


def _extract_props_from_narration(narration):
    """Mencari otomatis kata benda/hewan/aktivitas di dalam kalimat narasi Bahasa Indonesia/Inggris."""
    import re
    from stick_props import EMOJI_WORDS, normalize_prop
    found = []
    tokens = re.findall(r"[a-z]+", str(narration or "").lower())
    for tok in tokens:
        if tok in EMOJI_WORDS:
            p = "emoji:" + EMOJI_WORDS[tok]
            if p not in found:
                found.append(p)
        else:
            np = normalize_prop(tok)
            if np and np not in found:
                found.append(np)
    return found


def prepare_scene(scene, idx=1):
    """Membersihkan data adegan dari DeepSeek & menyiapkan latar + penempatan properti."""
    pose = str(scene.get("pose", "")).lower()
    if pose not in POSES:
        pose = DEFAULT_POSES[(idx - 1) % len(DEFAULT_POSES)]
    emotion = str(scene.get("emotion", scene.get("mood", ""))).lower()
    if emotion not in EMOTIONS:
        emotion = {"cry": "sad", "panic": "shocked", "celebrate": "happy", "think": "thinking"}.get(pose, "neutral")
    hat = str(scene.get("hat", "none")).lower()
    hat = hat if hat in HATS else "none"
    outfit = str(scene.get("outfit", "tshirt")).lower()
    outfit = outfit if outfit in OUTFITS else "tshirt"

    raw_props = scene.get("props", [])
    if isinstance(raw_props, str):
        raw_props = [p for p in raw_props.replace(";", ",").split(",")]
    extra = scene.get("icons", [])
    if isinstance(extra, str):
        extra = [e for e in extra.replace(";", ",").split(",")]
    raw_props = list(raw_props) + list(extra)
    names = []
    for p in raw_props:
        n = normalize_prop(p)
        if n and n not in names:
            names.append(n)

    # Tambahkan otomatis objek dari kalimat narasi jika props dari AI kurang dari 2
    narration_props = _extract_props_from_narration(scene.get("narration", ""))
    for np in narration_props:
        if len(names) >= 3:
            break
        if np not in names:
            names.append(np)

    if not names:
        names = ["question_marks"]

    area = [n for n in names if get_prop(n)[1] == "area"]
    ground = [n for n in names if get_prop(n)[1] == "ground"]
    high = [n for n in names if get_prop(n)[1] == "high"]

    placed = []
    if ground:
        placed.append((ground[0], (GROUND_SLOT[0], GROUND_SLOT[1], 1.0)))
        high = high + ground[1:]
        slots = HIGH_SLOTS_WITH_GROUND
    else:
        slots = HIGH_SLOTS_NO_GROUND
    for n, slot in zip(high, slots):
        x, y, size = slot
        if get_prop(n)[1] == "ground":
            y = y + 90 * size
        placed.append((n, (x, y, size)))

    return {
        "bg": make_background(scene.get("setting", "plain")),
        "pose": pose, "emotion": emotion, "hat": hat, "outfit": outfit,
        "area": area, "placed": placed,
        "mirror": (idx % 2 == 0),
    }


def compose_frame(vis, t, amp, speaking):
    """Menggambar 1 frame (RGB 720x1280) tanpa subtitle."""
    frame = vis["bg"].copy()
    dyn = Image.new("RGBA", (W * S, DYN_H * S), (0, 0, 0, 0))
    g = G(dyn, S, 0, DYN_TOP)
    mirror = vis["mirror"]

    def mx(x):
        return W - x if mirror else x

    for name in vis["area"]:
        local = t - 0.2
        if local > 0:
            get_prop(name)[0](g, local)

    for i, (name, (x, y, size)) in enumerate(vis["placed"]):
        local = t - (0.15 + i * 0.3)
        if local <= 0:
            continue
        sc = ease_back(local / 0.45)
        if sc < 0.05:
            continue
        get_prop(name)[0](g, mx(x), y, size * sc, local)

    char_x = 505 if mirror else 215
    face = -1 if mirror else 1
    draw_character(g, char_x, GROUND_Y, t, amp, speaking, vis["pose"], vis["emotion"],
                   vis["hat"], vis["outfit"], face)

    small = dyn.reduce(S)
    frame.paste(small, (0, DYN_TOP), small)
    return frame
