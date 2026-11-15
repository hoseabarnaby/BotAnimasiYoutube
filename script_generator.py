import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Kamu adalah penulis naskah dan sutradara untuk channel YouTube Shorts animasi stickman bergaya "The Paint Explainer" / "Kok Bisa?".
Tugas: buat naskah Shorts vertikal 40-55 detik, tepat 7 adegan, yang bercerita runtut (sebab-akibat), lucu/relatable, dan bikin penasaran.

ATURAN NARASI:
- Adegan 1 = HOOK 3 detik pertama (fakta mengejutkan / pertanyaan yang bikin orang batal scroll).
- Bahasa Indonesia santai seperti ngobrol dengan teman. Tiap adegan 14-22 kata, kalimat utuh, TANPA emoji dan tanpa simbol aneh.
- Adegan terakhir = kesimpulan + pertanyaan ke penonton agar komentar.

ATURAN VISUAL (SANGAT PENTING). Animasi digambar oleh engine dengan karakter stickman tetap (kepala bulat putih, kaos biru).
Kamu memilih elemen visual untuk tiap adegan agar SESUAI ISI NARASI ADEGAN ITU. Jangan ulangi kombinasi yang sama antar adegan.
Pilih elemen visual dari daftar ini:
- "setting": city, indoor, office, bank, market, nature, space, castle, ocean, sky, lab, desert, plain
  (ocean = laut/sungai/air/hewan air, sky = pesawat/langit/cuaca, lab = sains/biologi/kesehatan, desert = Mesir/gurun/sejarah kuno,
   castle = sejarah/perang/kerajaan, space = luar angkasa, nature = hewan darat/hutan/alam/danau)
- "props" (WAJIB 2 sampai 3 item per adegan!). Ada 2 jenis yang bisa kamu tulis di dalam array `props`:
  A) Nama properti animasi vektor:
     money_pile, shopping_cart, bank_building, printing_machine, laptop, house, fire, trophy,
     chart_down, chart_up, wallet_empty, bread, price_tag, coins, lightbulb, question_marks, clock, phone, book, globe,
     rocket, heart, warning, boom, gear, balance_scale, zzz, battery, briefcase, storm_cloud, banknotes_rain
  B) KARAKTER EMOJI UNICODE APAPUN SECARA LANGSUNG (misalnya: "🦎", "🌊", "🏃", "🐙", "❤️", "🚢", "💣", "🏰", "✈️", "🧬", "🔬", "🦖", "🌋", "🧠", "🦠", "👑", "⚔️", "🛡️", "🦁", "🦈", "🦅", "🐍", "🐜", "🐝", "🌍", "⚡", "❄️", "🍕", "☕", "🏥", "💊", "🧲", "🔭")!
     Engine kami merender SEMUA karakter emoji Unicode yang ada di dunia menjadi gambar ilustrasi besar berwarna dengan garis tepi stiker hitam tebal!
     ATURAN KERAS UNTUK `props`:
     - Untuk objek spesifik apa pun yang disebut di narasi (hewan apa saja, benda apa saja, negara/simbol apa saja, aktivitas apa saja) yang tidak ada di daftar A, TULIS LANGSUNG KARAKTER EMOJI UNICODE-NYA di dalam `props`!
     - Contoh 1 (Topik Kadal Basilisk lari di atas air):
       Scene 1: `"setting": "nature", "props": ["🦎", "🌊", "🏃"]`
       Scene 2: `"setting": "ocean", "props": ["🦎", "🦶", "💧"]`
       Scene 3: `"setting": "lab", "props": ["🦎", "⚡", "🔬"]`
     - Contoh 2 (Topik Gurita punya 3 jantung & darah biru):
       Scene 1: `"setting": "ocean", "props": ["🐙", "❤️", "question_marks"]`
       Scene 2: `"setting": "lab", "props": ["🐙", "💙", "🩸"]`
     - Contoh 3 (Topik Perang 38 Menit Inggris vs Zanzibar):
       Scene 1: `"setting": "castle", "props": ["⚔️", "clock", "👑"]`
       Scene 2: `"setting": "ocean", "props": ["🚢", "💣", "boom"]`
     - JANGAN PERNAH memakai `lightbulb` kecuali narasi memang berbicara tentang lampu atau ide!
- "pose": talk, point, panic, shrug, cry, celebrate, think, idle
- "emotion": neutral, happy, sad, shocked, angry, thinking
- "hat": none, tophat, crown, hardhat, cap, graduate, police
- "outfit": tshirt, suit
- "camera_effect": zoom_in, zoom_out, pan_left, pan_right

Contoh pemetaan: "harga roti naik tiap jam" -> props [price_tag, chart_up, bread], emotion shocked, pose panic.
"pemerintah cetak uang" -> setting bank, props [printing_machine, banknotes_rain], hat tophat, outfit suit, pose point.
"nilai uang anjlok" -> props [chart_down, storm_cloud]. "dompet kosong" -> props [wallet_empty], pose cry, emotion sad.
"dapat ide / solusi" -> props [lightbulb], pose celebrate, emotion happy.

Balas HANYA JSON valid dengan struktur:
{
  "title": "Judul clickbait jujur, maks 70 karakter #Shorts",
  "thumbnail_text": "2-4 KATA KAPITAL",
  "description": "3 paragraf singkat + hashtag di akhir",
  "tags": ["Shorts", "..."],
  "scenes": [
    {"scene_id": 1, "narration": "...", "setting": "market", "props": ["shopping_cart", "price_tag"],
     "pose": "panic", "emotion": "shocked", "hat": "none", "outfit": "tshirt", "camera_effect": "zoom_in"}
  ]
}
"""


def generate_script(topic, language="Indonesia"):
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key or api_key.startswith("sk-xxxx"):
        print("[!] DEEPSEEK_API_KEY belum diisi di .env! Menggunakan skrip contoh bawaan...")
        return get_fallback_demo_script(topic)

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    user_prompt = (
        f"Buat naskah Shorts tentang topik: '{topic}'. Bahasa {language}. "
        f"Pastikan setting, props, pose, dan emotion tiap adegan benar-benar cocok dengan kalimat narasinya. "
        f"Balas hanya JSON."
    )
    print(f"[*] Menghubungi DeepSeek untuk menulis skrip & storyboard: '{topic}'...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
        response_format={"type": "json_object"},
        temperature=0.8,
    )
    return json.loads(response.choices[0].message.content)


def get_fallback_demo_script(topic):
    return {
        "title": "Kenapa Negara Tidak Cetak Uang Terus Biar Kaya? #Shorts",
        "thumbnail_text": "CETAK UANG = BANGKRUT?!",
        "description": (
            "Kenapa pemerintah tidak mencetak uang sebanyak-banyaknya saja untuk mengatasi krisis? "
            "Ternyata ini yang terjadi di Jerman tahun 1923.\n\n"
            "Menurutmu, apa solusi terbaik saat negara kehabisan uang? Tulis di komentar ya!\n\n"
            "#Shorts #KrisisEkonomi #Inflasi #AnimasiStickman #Edukasi #FaktaUnik"
        ),
        "tags": ["Shorts", "Ekonomi", "Inflasi", "Hiperinflasi", "AnimasiStickman", "FaktaUnik", "Edukasi"],
        "scenes": [
            {"scene_id": 1, "narration": "Bayangin kamu belanja ke pasar bawa satu gerobak penuh uang, tapi pulangnya cuma dapat sepotong roti. Gila, kan?",
             "setting": "market", "props": ["shopping_cart", "price_tag"], "pose": "shrug", "emotion": "shocked",
             "hat": "none", "outfit": "tshirt", "camera_effect": "zoom_in"},
            {"scene_id": 2, "narration": "Ini bukan dongeng. Di Jerman tahun seribu sembilan ratus dua puluh tiga, harga roti naik berkali-kali lipat dalam hitungan jam.",
             "setting": "city", "props": ["chart_up", "clock", "bread"], "pose": "panic", "emotion": "shocked",
             "hat": "none", "outfit": "tshirt", "camera_effect": "pan_right"},
            {"scene_id": 3, "narration": "Awalnya pemerintah kehabisan uang, lalu mereka ambil jalan pintas: cetak uang sebanyak-banyaknya biar semua masalah selesai!",
             "setting": "bank", "props": ["printing_machine", "banknotes_rain"], "pose": "point", "emotion": "happy",
             "hat": "tophat", "outfit": "suit", "camera_effect": "zoom_out"},
            {"scene_id": 4, "narration": "Masalahnya, uang yang beredar makin banyak, sementara barang di pasar tetap segitu-gitu aja. Akibatnya, nilai uang anjlok.",
             "setting": "office", "props": ["chart_down", "storm_cloud"], "pose": "talk", "emotion": "thinking",
             "hat": "none", "outfit": "suit", "camera_effect": "pan_left"},
            {"scene_id": 5, "narration": "Gaji yang dibayar pagi hari sudah tidak cukup buat makan siang. Bahkan ada orang yang membakar uang untuk menghangatkan badan.",
             "setting": "indoor", "props": ["wallet_empty", "fire"], "pose": "cry", "emotion": "sad",
             "hat": "none", "outfit": "tshirt", "camera_effect": "zoom_in"},
            {"scene_id": 6, "narration": "Krisis ini disebut hiperinflasi, dan sampai sekarang jadi pelajaran mahal buat banyak negara di dunia.",
             "setting": "city", "props": ["globe", "warning"], "pose": "talk", "emotion": "neutral",
             "hat": "graduate", "outfit": "tshirt", "camera_effect": "zoom_out"},
            {"scene_id": 7, "narration": "Jadi cetak uang tanpa batas bukan solusi. Menurutmu, apa cara terbaik atasi krisis? Tulis di komentar ya!",
             "setting": "nature", "props": ["lightbulb", "question_marks"], "pose": "celebrate", "emotion": "happy",
             "hat": "none", "outfit": "tshirt", "camera_effect": "zoom_in"},
        ],
    }
