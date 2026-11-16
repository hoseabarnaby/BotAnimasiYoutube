import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Kamu adalah Penulis Naskah Utama & Sutradara Visual untuk channel YouTube Long-Form (16:9 Widescreen) animasi edukasi-hiburan bergaya "The Paint Explainer", "OverSimplified", dan "Kok Bisa?".
Tugas: Buat naskah video YouTube Widescreen 16:9 berdurasi panjang (sekitar 2,5 sampai 3,5 menit, terdiri dari 12 sampai 14 adegan/scenes yang mendalam, seru, penuh contoh konyol/nyata, dan bikin penonton betah menonton sampai detik terakhir).

ATURAN PENULISAN NARASI LONG-VIDEO:
- ADEGAN 1 (HOOK KUAT): Buka dengan pertanyaan mind-blowing, paradoks aneh, atau skenario ekstrem yang membuat penonton penasaran.
- ADEGAN 2-4 (LATAR BELAKANG & SEJARAH/PENYEBAB): Jelaskan asal-usul atau cara kerjanya dengan perumpamaan sehari-hari yang mudah dibayangkan.
- ADEGAN 5-9 (STUDI KASUS NYATA & FAKTA MENGEJUTKAN): Berikan contoh nyata, angka unik, eksperimen sains, atau kejadian sejarah yang seru (sebab-akibat).
- ADEGAN 10-11 (DAMPAK ATAU PLOT TWIST): Hal yang jarang disadari orang banyak.
- ADEGAN TERAKHIR (KESIMPULAN & AJAKAN DISKUSI): Rangkum secara cerdas dan ajukan pertanyaan menarik agar penonton berdebat di kolom komentar & klik Subscribe.
- Panjang kalimat per adegan: sekitar 22 sampai 32 kata per adegan (mengalir natural seperti bercerita ke teman, TANPA emoji di dalam teks `narration`).

ATURAN VISUAL WIDESCREEN 16:9 (SANGAT PENTING):
Animasi digambar oleh engine vektor 16:9 dengan karakter stickman tetap (kepala bulat putih, kaos biru/jas).
Kamu memilih elemen visual untuk tiap adegan agar 100% SESUAI ISI NARASI ADEGAN ITU:
- "setting": city, indoor, office, bank, market, nature, space, castle, ocean, sky, lab, desert, plain
- "props" (WAJIB 2 sampai 3 item per adegan! Jangan kurang dari 2 item):
  A) Properti animasi vektor:
     money_pile, shopping_cart, bank_building, printing_machine, laptop, house, fire, trophy,
     chart_down, chart_up, wallet_empty, bread, price_tag, coins, lightbulb, question_marks, clock, phone, book, globe,
     rocket, heart, warning, boom, gear, balance_scale, zzz, battery, briefcase, storm_cloud, banknotes_rain
  B) KARAKTER EMOJI UNICODE APAPUN SECARA LANGSUNG (misalnya: "🦎", "🌊", "🏃", "🐙", "❤️", "🚢", "💣", "🏰", "✈️", "🧬", "🔬", "🦖", "🌋", "🧠", "🦠", "👑", "⚔️", "🛡️", "🦁", "🦈", "🦅", "🐍", "🐜", "🐝", "🌍", "⚡", "❄️", "🍕", "☕", "🏥", "💊", "🧲", "🔭")!
     Engine kami merender SEMUA karakter emoji Unicode di dunia menjadi gambar ilustrasi besar berwarna dengan garis tepi stiker hitam tebal!
     ATURAN KERAS: Untuk objek spesifik apa pun yang disebut di narasi (hewan, benda, organ tubuh, makanan, senjata, fenomena alam), TULIS LANGSUNG KARAKTER EMOJI UNICODE-NYA di dalam array `props`!
- "pose": talk, point, panic, shrug, cry, celebrate, think, idle
- "emotion": neutral, happy, sad, shocked, angry, thinking
- "hat": none, tophat, crown, hardhat, cap, graduate, police
- "outfit": tshirt, suit
- "camera_effect": zoom_in, zoom_out, pan_left, pan_right

ATURAN THUMBNAIL KELAS ATAS (`thumbnail_text` & Judul):
- "title": Judul YouTube Long Video yang memancing rasa ingin tahu tinggi (Maks 80 karakter, JANGAN pakai tag #Shorts karena ini video panjang 16:9!).
- "thumbnail_text": 2 sampai 4 KATA KAPITAL SINGKAT & NENDANG untuk dipasang besar di Thumbnail (Contoh: "KENAPA BISA GINI?!", "RAHASIA TERSEMBUNYI!", "CETAK UANG = HANCUR!").

Balas HANYA JSON valid dengan struktur:
{
  "title": "Judul YouTube Long Video yang Menarik & Bikin Penasaran",
  "thumbnail_text": "TEKS THUMBNAIL 2-4 KATA",
  "description": "Deskripsi lengkap YouTube 3-4 paragraf + timestamps bab singkat + hashtags di akhir",
  "tags": ["Edukasi", "FaktaUnik", "AnimasiIndonesia", "Sejarah", "Sains", "KokBisa"],
  "scenes": [
    {"scene_id": 1, "narration": "...", "setting": "market", "props": ["shopping_cart", "price_tag", "💸"],
     "pose": "panic", "emotion": "shocked", "hat": "none", "outfit": "tshirt", "camera_effect": "zoom_in"}
  ]
}
"""


def generate_script(topic, language="Indonesia"):
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key or api_key.startswith("sk-xxxx"):
        print("[!] DEEPSEEK_API_KEY belum diisi di .env! Menggunakan skrip Long Video bawaan...")
        return get_fallback_demo_script(topic)

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    user_prompt = (
        f"Buatkan naskah YouTube Long Video (Format 16:9 Widescreen, 12 sampai 14 adegan lengkap) tentang topik: '{topic}'. "
        f"Bahasa {language} yang santai, mendalam, lucu, dan sangat informatif. "
        f"Pastikan setiap adegan memiliki minimal 2-3 `props` (kombinasi prop vektor dan emoji Unicode langsung) yang 100% cocok dengan kalimat narasinya. "
        f"Jangan gunakan #Shorts pada judul karena ini video panjang 16:9. Balas hanya JSON."
    )
    print(f"[*] Menghubungi DeepSeek untuk menulis skrip Long Video (12-14 adegan) & storyboard: '{topic}'...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
        response_format={"type": "json_object"},
        temperature=0.8,
        max_tokens=4000,
    )
    return json.loads(response.choices[0].message.content)


def get_fallback_demo_script(topic):
    return {
        "title": "Kenapa Negara Tidak Mencetak Uang Sebanyak-banyaknya Saat Krisis Ekonomi?",
        "thumbnail_text": "CETAK UANG = BANGKRUT?!",
        "description": (
            "Pernahkah kamu berpikir: kalau pemerintah bisa mencetak uang sendiri, kenapa tidak cetak uang sebanyak-banyaknya saja untuk melunasi utang dan membuat semua warga jadi kaya raya?\n\n"
            "Di video animasi kali ini, kita akan membahas secara lengkap bagaimana cara kerja uang, bahaya hiperinflasi, hingga kisah nyata negara-negara yang hancur karena mencetak uang tanpa batas!\n\n"
            "#Ekonomi #Inflasi #FaktaUnik #AnimasiIndonesia #Edukasi #SejarahDunia"
        ),
        "tags": ["Ekonomi", "Inflasi", "Hiperinflasi", "AnimasiStickman", "FaktaUnik", "Edukasi", "KokBisa"],
        "scenes": [
            {"scene_id": 1, "narration": "Pernah nggak sih kamu kepikiran, kalau pemerintah punya mesin pencetak uang resmi, kenapa mereka nggak cetak uang sebanyak-banyaknya aja supaya semua warga jadi miliarder?",
             "setting": "bank", "props": ["printing_machine", "money_pile", "question_marks"], "pose": "shrug", "emotion": "shocked",
             "hat": "none", "outfit": "tshirt", "camera_effect": "zoom_in"},
            {"scene_id": 2, "narration": "Sekilas ide ini terdengar sangat jenius. Bayangkan kalau setiap keluarga dikirimi satu koper penuh uang tunai, bukankah kemiskinan bakal langsung hilang dalam semalam?",
             "setting": "city", "props": ["briefcase", "banknotes_rain", "💰"], "pose": "celebrate", "emotion": "happy",
             "hat": "tophat", "outfit": "suit", "camera_effect": "pan_right"},
            {"scene_id": 3, "narration": "Sayangnya di dunia nyata, uang kertas itu sebenarnya tidak punya nilai sakti pada dirinya sendiri. Uang hanyalah alat tukar untuk mewakili barang dan jasa yang ada.",
             "setting": "office", "props": ["balance_scale", "coins", "bread"], "pose": "talk", "emotion": "thinking",
             "hat": "graduate", "outfit": "tshirt", "camera_effect": "zoom_out"},
            {"scene_id": 4, "narration": "Coba kita bayangkan sebuah pulau kecil yang hanya punya sepuluh potong roti, dan total uang yang dipegang seluruh penduduknya hanya sepuluh ribu rupiah.",
             "setting": "market", "props": ["bread", "coins", "🏝️"], "pose": "point", "emotion": "neutral",
             "hat": "none", "outfit": "tshirt", "camera_effect": "pan_left"},
            {"scene_id": 5, "narration": "Artinya harga satu potong roti di pulau itu adalah seribu rupiah. Semuanya berjalan seimbang antara jumlah uang yang beredar dan makanan yang tersedia.",
             "setting": "market", "props": ["shopping_cart", "price_tag", "bread"], "pose": "talk", "emotion": "happy",
             "hat": "none", "outfit": "tshirt", "camera_effect": "zoom_in"},
            {"scene_id": 6, "narration": "Tiba-tiba kepala suku di pulau itu mencetak uang baru dan membagikan sejuta rupiah ke setiap warga, padahal jumlah rotinya tetap cuma sepuluh potong!",
             "setting": "bank", "props": ["printing_machine", "banknotes_rain", "👑"], "pose": "point", "emotion": "happy",
             "hat": "crown", "outfit": "suit", "camera_effect": "zoom_out"},
            {"scene_id": 7, "narration": "Karena semua orang sekarang memegang uang jutaan rupiah dan berebut roti yang sedikit, penjual roti pun langsung menaikkan harganya menjadi satu juta rupiah per potong!",
             "setting": "market", "props": ["chart_up", "price_tag", "🔥"], "pose": "panic", "emotion": "shocked",
             "hat": "none", "outfit": "tshirt", "camera_effect": "pan_right"},
            {"scene_id": 8, "narration": "Hasilnya? Warga memang memegang jutaan lembar uang di tangan mereka, tapi kekayaan asli mereka sama sekali tidak bertambah karena harga barang ikut meroket.",
             "setting": "city", "props": ["chart_down", "wallet_empty", "storm_cloud"], "pose": "shrug", "emotion": "sad",
             "hat": "none", "outfit": "tshirt", "camera_effect": "zoom_in"},
            {"scene_id": 9, "narration": "Bencana ini benar-benar pernah terjadi di Jerman pada tahun seribu sembilan ratus dua puluh tiga, ketika pemerintahnya mencetak uang gila-gilaan untuk membayar utang perang.",
             "setting": "castle", "props": ["⚔️", "printing_machine", "warning"], "pose": "talk", "emotion": "shocked",
             "hat": "helmet", "outfit": "tshirt", "camera_effect": "pan_left"},
            {"scene_id": 10, "narration": "Saat itu harga barang naik dua kali lipat setiap beberapa jam! Pekerja yang gajian di pagi hari harus berlari kencang ke pasar sebelum uangnya tidak laku di siang hari.",
             "setting": "city", "props": ["clock", "🏃", "shopping_cart"], "pose": "panic", "emotion": "shocked",
             "hat": "none", "outfit": "tshirt", "camera_effect": "zoom_in"},
            {"scene_id": 11, "narration": "Bahkan saking tidak berharganya uang kertas waktu itu, warga Jerman lebih memilih membakar tumpukan uang di tungku perapian karena lebih murah daripada membeli kayu bakar!",
             "setting": "indoor", "props": ["fire", "money_pile", "💸"], "pose": "cry", "emotion": "sad",
             "hat": "none", "outfit": "tshirt", "camera_effect": "zoom_out"},
            {"scene_id": 12, "narration": "Hal serupa juga menimpa Zimbabwe pada tahun dua ribu delapan, di mana pemerintahnya sampai harus mencetak selembar uang pecahan seratus triliun dolar yang hanya cukup buat naik bus.",
             "setting": "city", "props": ["🚌", "money_pile", "globe"], "pose": "talk", "emotion": "shocked",
             "hat": "none", "outfit": "tshirt", "camera_effect": "pan_right"},
            {"scene_id": 13, "narration": "Itulah alasan kenapa bank sentral sangat berhati-hati menjaga jumlah uang agar selalu seimbang dengan produksi barang dan jasa yang nyata di masyarakat.",
             "setting": "bank", "props": ["bank_building", "balance_scale", "🛡️"], "pose": "point", "emotion": "happy",
             "hat": "tophat", "outfit": "suit", "camera_effect": "zoom_out"},
            {"scene_id": 14, "narration": "Jadi kemakmuran sebuah negara tidak ditentukan oleh banyaknya kertas yang dicetak, melainkan produktivitas warganya. Menurutmu topik ekonomi apa lagi yang seru kita bahas? Tulis di komentar ya!",
             "setting": "nature", "props": ["lightbulb", "trophy", "🚀"], "pose": "celebrate", "emotion": "happy",
             "hat": "graduate", "outfit": "tshirt", "camera_effect": "zoom_in"},
        ],
    }
