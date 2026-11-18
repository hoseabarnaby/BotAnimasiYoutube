"""
Pembuat gambar adegan. Urutan penyedia (otomatis, sesuai kunci yang tersedia di .env):
  1. gemini      -> GEMINI_API_KEY            (kualitas terbaik, berbayar per gambar)
  2. cloudflare  -> CF_ACCOUNT_ID + CF_API_TOKEN (FLUX schnell, ada kuota gratis harian)
  3. huggingface -> HF_TOKEN                  (FLUX schnell, kredit gratis bulanan terbatas)
  4. pollinations-> hanya jika IMAGE_PROVIDER=pollinations (gratis, tapi 1 gambar / 45 detik & ada watermark)
  5. local       -> generator sketsa bawaan (gratis, tanpa batas, selalu berhasil)
Jika penyedia AI gagal untuk sebuah adegan, otomatis memakai generator sketsa bawaan.
"""
import base64
import io
import os
import time

import requests
from PIL import Image, ImageFilter

from sketch_style import render_sketch_image

OUT_W, OUT_H = 1920, 1080

STYLE_PREFIX = (
    "Hand-drawn pencil and black ink sketch illustration on cream off-white paper, whiteboard doodle explainer style. "
    "The only character is a simple stick figure: round white head with a thin outline, minimal dot eyes and expressive "
    "eyebrows, thin line body, arms and legs, no clothes, no hair. Loose gray pencil shading, rough sketchy linework, "
    "mostly black, white and gray with ONE warm yellow-orange accent color only on the most important object. "
    "Soft vignette, wide 16:9 composition with plenty of empty paper space, absolutely no text, no letters, "
    "no numbers, no watermark. Scene: "
)

_state = {"disabled": set(), "fails": {}, "last_poll": 0.0}


def providers():
    mode = os.getenv("IMAGE_PROVIDER", "auto").strip().lower()
    avail = []
    if os.getenv("GEMINI_API_KEY", "").strip():
        avail.append("gemini")
    if os.getenv("CF_ACCOUNT_ID", "").strip() and os.getenv("CF_API_TOKEN", "").strip():
        avail.append("cloudflare")
    if os.getenv("HF_TOKEN", "").strip():
        avail.append("huggingface")
    if mode in ("", "auto"):
        return avail
    if mode == "local":
        return []
    return [mode]


# ----------------------------------------------------------------------------- penyedia
def _bytes_to_image(data):
    return Image.open(io.BytesIO(data)).convert("RGB")


def _gen_gemini(prompt, seed):
    key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image").strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "imageConfig": {"aspectRatio": "16:9"}},
    }
    r = requests.post(url, json=body, headers={"x-goog-api-key": key}, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"gemini {r.status_code}: {r.text[:200]}")
    for cand in r.json().get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                return _bytes_to_image(base64.b64decode(inline["data"]))
    raise RuntimeError("gemini: tidak ada gambar di respons")


def _gen_cloudflare(prompt, seed):
    acc = os.getenv("CF_ACCOUNT_ID", "").strip()
    tok = os.getenv("CF_API_TOKEN", "").strip()
    url = f"https://api.cloudflare.com/client/v4/accounts/{acc}/ai/run/@cf/black-forest-labs/flux-1-schnell"
    r = requests.post(url, json={"prompt": prompt[:2000], "steps": 8, "seed": seed},
                      headers={"Authorization": f"Bearer {tok}"}, timeout=120)
    if r.headers.get("content-type", "").startswith("image/"):
        return _bytes_to_image(r.content)
    data = r.json()
    if r.status_code == 200 and data.get("success") and data.get("result", {}).get("image"):
        return _bytes_to_image(base64.b64decode(data["result"]["image"]))
    raise RuntimeError(f"cloudflare {r.status_code}: {str(data)[:200]}")


def _gen_huggingface(prompt, seed):
    tok = os.getenv("HF_TOKEN", "").strip()
    url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    r = requests.post(url, json={"inputs": prompt[:2000], "parameters": {"width": 1280, "height": 720, "seed": seed}},
                      headers={"Authorization": f"Bearer {tok}"}, timeout=180)
    if r.status_code == 200 and r.headers.get("content-type", "").startswith("image/"):
        return _bytes_to_image(r.content)
    raise RuntimeError(f"huggingface {r.status_code}: {r.text[:200]}")


def _gen_pollinations(prompt, seed):
    wait = 46 - (time.time() - _state["last_poll"])
    if wait > 0:
        time.sleep(wait)
    _state["last_poll"] = time.time()
    import urllib.parse
    url = (f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt[:1500])}"
           f"?width=1280&height=720&model=flux&nologo=true&seed={seed}")
    headers = {}
    if os.getenv("POLLINATIONS_KEY", "").strip():
        headers["Authorization"] = "Bearer " + os.getenv("POLLINATIONS_KEY").strip()
    r = requests.get(url, headers=headers, timeout=150)
    if r.status_code == 200 and len(r.content) > 8000:
        return _bytes_to_image(r.content)
    raise RuntimeError(f"pollinations {r.status_code}: {r.text[:150]}")


_GEN = {"gemini": _gen_gemini, "cloudflare": _gen_cloudflare, "huggingface": _gen_huggingface,
        "pollinations": _gen_pollinations}


# ----------------------------------------------------------------------------- utilitas
def fit_16_9(img, w=OUT_W, h=OUT_H):
    """Ubah gambar ke 16:9. Gambar persegi diperlebar dengan perpanjangan 'kertas' di kiri-kanan."""
    img = img.convert("RGB")
    iw, ih = img.size
    if abs(iw / float(ih) - 16 / 9.0) < 0.06:
        return img.resize((w, h), Image.Resampling.LANCZOS)
    scale = h / float(ih)
    nw = int(iw * scale)
    res = img.resize((max(1, nw), h), Image.Resampling.LANCZOS)
    if nw >= w:
        x = (nw - w) // 2
        return res.crop((x, 0, x + w, h))
    left = (w - nw) // 2
    right = w - nw - left
    canvas = Image.new("RGB", (w, h))
    canvas.paste(res.crop((0, 0, 6, h)).resize((max(1, left), h)).filter(ImageFilter.GaussianBlur(14)), (0, 0))
    canvas.paste(res.crop((nw - 6, 0, nw, h)).resize((max(1, right), h)).filter(ImageFilter.GaussianBlur(14)),
                 (left + nw, 0))
    mask = Image.new("L", (nw, h), 255)
    for i in range(30):
        v = int(255 * i / 30.0)
        for x in (i, nw - 1 - i):
            mask.paste(v, (x, 0, x + 1, h))
    canvas.paste(res, (left, 0), mask)
    return canvas


def build_prompt(scene):
    base = str(scene.get("image_prompt", "")).strip()
    if not base:
        base = "a stick figure thinking about " + str(scene.get("narration", ""))[:120]
    return STYLE_PREFIX + base


def get_scene_image(scene, idx, work_dir, log=print):
    """Mengembalikan (PIL.Image RGB 1920x1080, sumber). Selalu berhasil (ada cadangan lokal)."""
    cache = os.path.join(work_dir, f"scene_{idx:03d}.jpg")
    if os.path.exists(cache):
        return Image.open(cache).convert("RGB"), "cache"

    prompt = build_prompt(scene)
    for name in providers():
        if name in _state["disabled"] or name not in _GEN:
            continue
        for attempt in range(2):
            try:
                img = fit_16_9(_GEN[name](prompt, 1000 + idx * 7 + attempt))
                img.save(cache, quality=93)
                _state["fails"][name] = 0
                return img, name
            except Exception as e:
                msg = str(e)
                log(f"       [!] {name} gagal untuk adegan {idx}: {msg[:140]}")
                if any(k in msg for k in ("429", "4006", "quota", "RESOURCE_EXHAUSTED", "402", "401", "403")):
                    time.sleep(8)
                time.sleep(2)
        _state["fails"][name] = _state["fails"].get(name, 0) + 1
        if _state["fails"][name] >= 3:
            _state["disabled"].add(name)
            log(f"       [!] {name} dimatikan untuk sisa video (gagal berturut-turut), memakai sketsa bawaan.")

    img = render_sketch_image(scene, idx)
    img.save(cache, quality=93)
    return img, "local"


def get_thumbnail_base(storyboard, work_dir, log=print):
    """Gambar dasar thumbnail dari AI (jika tersedia), atau None."""
    prompt = str(storyboard.get("thumbnail_prompt", "")).strip()
    if not prompt:
        return None
    full = (STYLE_PREFIX + prompt + " Dramatic close-up composition, the most important object is large and glowing "
            "yellow-orange, keep the left 45 percent of the frame as empty paper for a title.")
    for name in providers():
        if name in _state["disabled"] or name not in _GEN:
            continue
        try:
            return fit_16_9(_GEN[name](full, 4242), 1280, 720)
        except Exception as e:
            log(f"       [!] thumbnail AI ({name}) gagal: {str(e)[:140]}")
    return None
