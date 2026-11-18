import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Kamu adalah Penulis Naskah Dokumenter & Sutradara Storyboard kelas atas untuk channel YouTube animasi edukasi bergaya "20 Minute Tech Animation / Asal Mula Bitcoin / The Paint Explainer / Kok Bisa?".

TUGAS UTAMAMU:
Membuat naskah video YouTube Widescreen 16:9 yang SANGAT MENDALAM, DRAMATIS, BERCERITA RUNTUT (Storytelling), dan BIKIN PENONTON TERPAKU DARI AWAL SAMPAI AKHIR (terdiri dari 14 sampai 16 adegan/scenes lengkap).

KARAKTERISTIK GAYA VISUAL & CERITA (PERSIS CONTOH "ASAL MULA BITCOIN"):
1. Setiap adegan adalah **1 Ilustrasi Sketsa Tinta & Pensil di atas Kertas Krem** (dengan aksen warna kuning/emas/oranye pada objek utama), disertai **JUDUL BAB SINGKAT (2-3 KATA KAPITAL)** di bagian atas gambar!
   Contoh judul bab (`title` di tiap scene): "NILAI MELEDAK", "BANKRUT TOTAL", "BLOK PERTAMA", "TEMBOK MATEMATIKA", "WASIT TERPUSAT", "OTOMATIS DITOLAK", "INSENTIF PENAMBANG", "BATAS MUTLAK", "KEBAL BOBOL".
2. Naskah (`narration`) harus berbobot, punya alur dokumenter yang memikat:
   - ADEGAN 1 (COLD OPEN / HOOK 3-5 DETIK PERTAMA!): WAJIB singkat, tajam, maksimal 10-14 kata saja (sekitar 4 detik)! Jangan langsung bercerita panjang. Lemparkan 1 kalimat atau pertanyaan paling mengejutkan/mind-blowing sebagai pancingan pembuka (Cold Open), dengan `title` berupa pertanyaan singkat atau judul hook (contoh: "UANG TANPA TUAN?", "KENAPA BISA RUNTUH?").
   - ADEGAN 2-3 (BAB PEMBUKA & KONTRAS MENGEJUTKAN): Baru mulai masuk ke cerita pembuka dengan fakta gila atau kontras sejarah.
   - ADEGAN 4-6: Akar Masalah / Krisis / Sejarah Awal (mengapa hal ini terjadi? apa masalah besarnya?).
   - ADEGAN 7-11: Cara Kerja / Mekanisme Inti (dijelaskan dengan analogi brilian yang mudah dipahami anak SMP sekalipun, tapi tetap akurat dan cerdas).
   - ADEGAN 12-14: Uji Ketahanan / Konflik / Plot Twist Nyata di Dunia.
   - ADEGAN 15-16: Masa Depan, Kesimpulan Filosofis & Pertanyaan Diskusi untuk penonton.
   - Panjang `narration` Adegan 1 (Hook): 10 sampai 14 kata saja (3-5 detik).
   - Panjang `narration` Adegan 2 dan seterusnya: 22 sampai 32 kata (kalimat Bahasa Indonesia yang mengalir natural, dramatis, TANPA emoji di dalam teks `narration`).

ATURAN ELEMEN VISUAL TIAP ADEGAN:
Untuk setiap adegan, berikan:
- "scene_id": nomor urut adegan (1, 2, 3, ...)
- "title": JUDUL BAB 2-3 KATA KAPITAL di atas gambar (wajib singkat, padat, nendang, contoh: "BANKRUT TOTAL", "WASIT TERPUSAT", "KEBAL BOBOL")
- "narration": kalimat narasi voiceover Bahasa Indonesia
- "image_prompt": deskripsi detail ilustrasi dalam Bahasa Inggris untuk digambar di adegan itu (contoh: "a shocked stick figure with round white head standing in front of a crumbling bank building with a crashing downward arrow and dust clouds")
- "setting": pilih dari [city, indoor, office, bank, market, nature, space, castle, ocean, sky, lab, desert, plain]
- "props": WAJIB 2 sampai 3 item per adegan! Urutkan objek PALING PENTING di urutan pertama (karena item pertama akan diberi sorotan cahaya kuning emas/oranye!).
  Bisa memilih dari daftar prop vektor:
  [money_pile, shopping_cart, bank_building, printing_machine, laptop, house, fire, trophy, chart_down, chart_up, wallet_empty, bread, price_tag, coins, lightbulb, question_marks, clock, phone, book, globe, rocket, heart, warning, boom, gear, balance_scale, zzz, battery, briefcase, storm_cloud, banknotes_rain]
  ATAU TULIS LANGSUNG KARAKTER EMOJI UNICODE APAPUN untuk objek spesifik (contoh: "🪙", "🍕", "🏦", "🧱", "⛏️", "📦", "📢", "🔒", "⛓️", "🦎", "🌊", "🐙", "✈️", "🧬", "🔬", "🦖", "🌋", "🧠", "👑", "⚔️", "🛡️", "🚢", "💣").
- "pose": pilih dari [talk, point, panic, shrug, cry, celebrate, think, idle]
- "emotion": pilih dari [neutral, happy, sad, shocked, angry, thinking]
- "hat": pilih dari [none, tophat, crown, hardhat, cap, graduate, police]
- "camera_effect": pilih dari [zoom_in, zoom_out, pan_left, pan_right]

ATURAN JUDUL UTAMA & THUMBNAIL (`thumbnail_text`):
- "title": Judul YouTube utama yang sangat menarik dan membuat orang wajib klik (Maks 75 karakter, tanpa #Shorts).
- "thumbnail_text": 2 sampai 3 KATA KAPITAL SINGKAT untuk dipasang di bagian atas Thumbnail (seperti "ASAL MULA BITCOIN", "RAHASIA UANG", "KENAPA BANGKRUT?!").
- "thumbnail_prompt": deskripsi visual Inggris untuk adegan thumbnail (stick figure terkejut menunjuk ke objek utama yang bersinar emas di tengah latar dramatis).

Balas HANYA dalam format JSON valid:
{
  "title": "Judul Video YouTube...",
  "thumbnail_text": "JUDUL THUMBNAIL SINGKAT",
  "thumbnail_prompt": "a shocked stick figure pointing at a glowing golden coin in front of a crumbling bank building",
  "description": "Deskripsi lengkap 3-4 paragraf + daftar bab + hashtags",
  "tags": ["Edukasi", "Dokumenter", "Animasi", "Teknologi", "Sejarah", "FaktaUnik"],
  "scenes": [
    {
      "scene_id": 1,
      "title": "NILAI MELEDAK",
      "narration": "...",
      "image_prompt": "...",
      "setting": "city",
      "props": ["🪙", "🍕", "boom"],
      "pose": "panic",
      "emotion": "shocked",
      "hat": "none",
      "camera_effect": "zoom_in"
    }
  ]
}
"""


def generate_script(topic, language="Indonesia"):
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key or api_key.startswith("sk-xxxx"):
        print("[!] DEEPSEEK_API_KEY belum diisi di .env! Menggunakan skrip dokumenter bawaan...")
        return get_fallback_demo_script(topic)

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    user_prompt = (
        f"Buatkan naskah dokumenter animasi YouTube Widescreen 16:9 (14 sampai 16 adegan mendalam) tentang topik: '{topic}'. "
        f"Gunakan gaya penceritaan yang persis seperti video 'Asal Mula Bitcoin' (tiap adegan punya `title` bab 2-3 kata kapital yang nendang di atas gambar, narasi Bahasa {language} yang cerdas dan bikin penasaran, serta `props` 2-3 objek yang sangat relevan di mana item pertama adalah fokus utama). "
        f"Pastikan outputnya murni JSON sesuai skema."
    )
    print(f"[*] Menghubungi DeepSeek untuk merancang naskah dokumenter & storyboard sketsa: '{topic}'...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
        response_format={"type": "json_object"},
        temperature=0.78,
        max_tokens=4500,
    )
    return json.loads(response.choices[0].message.content)


def get_fallback_demo_script(topic):
    return {
        "title": "Asal Mula Bitcoin: Bagaimana Koin Digital Mengguncang Bank Dunia",
        "thumbnail_text": "ASAL MULA BITCOIN",
        "thumbnail_prompt": "a shocked stick figure pointing at a glowing golden bitcoin coin in front of a crumbling bank building with a pizza slice on the ground",
        "description": (
            "Bagaimana sebuah kode komputer yang dulunya hanya cukup untuk membeli dua loyang pizza kini bernilai miliaran rupiah dan menantang sistem perbankan dunia?\n\n"
            "Di video animasi sketsa ini, kita membedah tuntas sejarah lahirnya Bitcoin dari krisis finansial 2008, cara kerja blockchain, penambangan, hingga alasan kenapa jumlahnya dibatasi 21 juta koin!\n\n"
            "#Bitcoin #Teknologi #Ekonomi #AnimasiEdukasi #SejarahUang #FaktaUnik"
        ),
        "tags": ["Bitcoin", "Blockchain", "Ekonomi", "Teknologi", "AnimasiIndonesia", "Edukasi", "Sejarah"],
        "scenes": [
            {"scene_id": 1, "title": "UANG TANPA BANK?",
             "narration": "Bagaimana jadinya jika ada uang yang tidak bisa dikendalikan oleh pemerintah atau bank mana pun di dunia?",
             "image_prompt": "a shocked stick figure pointing at a glowing golden coin in front of a crumbling bank building",
             "setting": "bank", "props": ["🪙", "bank_building", "question_marks"], "pose": "point", "emotion": "shocked", "hat": "none", "camera_effect": "zoom_in"},
            {"scene_id": 2, "title": "NILAI MELEDAK",
             "narration": "Pada tahun dua ribu sepuluh, seorang programmer membeli dua loyang pizza dengan sepuluh ribu koin digital yang kini nilainya setara lima belas triliun rupiah!",
             "image_prompt": "a shocked stick figure looking at a pizza box and an exploding volcano of golden coins",
             "setting": "city", "props": ["🪙", "🍕", "boom"], "pose": "panic", "emotion": "shocked", "hat": "none", "camera_effect": "zoom_in"},
            {"scene_id": 2, "title": "BANKRUT TOTAL",
             "narration": "Semuanya bermula pada krisis finansial dua ribu delapan, ketika bank-bank raksasa dunia runtuh dan uang tabungan masyarakat tergerus habis dalam semalam.",
             "setting": "bank", "props": ["chart_down", "bank_building", "🏚️"], "pose": "panic", "emotion": "shocked", "hat": "none", "camera_effect": "pan_right"},
            {"scene_id": 3, "title": "WASIT TERPUSAT",
             "narration": "Selama ratusan tahun, setiap kali kita mengirim uang, kita selalu membutuhkan bank sentral sebagai wasit pencatat yang memegang kendali penuh atas rekening kita.",
             "setting": "bank", "props": ["book", "bank_building", "⚖️"], "pose": "point", "emotion": "neutral", "hat": "police", "camera_effect": "zoom_out"},
            {"scene_id": 4, "title": "BLOK PERTAMA",
             "narration": "Di tengah krisis itu, sosok misterius bernama Satoshi Nakamoto menciptakan sistem uang baru yang berjalan otomatis tanpa bank dan tanpa bos sama sekali.",
             "setting": "office", "props": ["📦", "laptop", "question_marks"], "pose": "talk", "emotion": "thinking", "hat": "none", "camera_effect": "pan_left"},
            {"scene_id": 5, "title": "BUKU TERBUKA",
             "narration": "Alih-alih disimpan di satu gedung bank, buku catatan transaksi ini disebarkan ke ribuan komputer di seluruh dunia sehingga semua orang bisa saling mengawasi.",
             "setting": "lab", "props": ["globe", "book", "💻"], "pose": "point", "emotion": "happy", "hat": "none", "camera_effect": "zoom_in"},
            {"scene_id": 6, "title": "OTOMATIS DITOLAK",
             "narration": "Jika ada satu pihak nakal yang mencoba memalsukan saldo di komputernya, ribuan komputer lain akan langsung menyadari perbedaan itu dan menolaknya secara otomatis!",
             "setting": "office", "props": ["warning", "🛡️", "💻"], "pose": "panic", "emotion": "angry", "hat": "none", "camera_effect": "zoom_out"},
            {"scene_id": 7, "title": "TEMBOK MATEMATIKA",
             "narration": "Untuk mengunci setiap halaman transaksi agar menjadi blok yang sah, komputer harus memecahkan teka-teki matematika kriptografi yang sangat rumit.",
             "setting": "castle", "props": ["🧱", "🔒", "gear"], "pose": "think", "emotion": "thinking", "hat": "hardhat", "camera_effect": "pan_right"},
            {"scene_id": 8, "title": "INSENTIF PENAMBANG",
             "narration": "Siapa pun yang berhasil memecahkan teka-teki itu paling cepat akan mendapat hadiah koin baru, dan proses inilah yang disebut sebagai penambangan atau mining.",
             "setting": "desert", "props": ["coins", "⛏️", "lightbulb"], "pose": "celebrate", "emotion": "happy", "hat": "hardhat", "camera_effect": "zoom_in"},
            {"scene_id": 9, "title": "BLOK DIPASANG",
             "narration": "Blok yang sudah terverifikasi kemudian diumumkan ke seluruh jaringan dan disambungkan dengan rantai kode ke blok sebelumnya hingga membentuk rantai abadi.",
             "setting": "city", "props": ["⛓️", "📦", "📢"], "pose": "point", "emotion": "happy", "hat": "none", "camera_effect": "pan_left"},
            {"scene_id": 10, "title": "KEBAL BOBOL",
             "narration": "Karena setiap blok saling mengunci, mengubah satu transaksi lama berarti harus membongkar seluruh rantai di ribuan komputer sekaligus, yang hampir mustahil dilakukan.",
             "setting": "castle", "props": ["🔒", "🛡️", "⛓️"], "pose": "talk", "emotion": "happy", "hat": "none", "camera_effect": "zoom_out"},
            {"scene_id": 11, "title": "BATAS MUTLAK",
             "narration": "Berbeda dengan uang kertas yang bisa dicetak terus-menerus, jumlah koin ini sudah dikunci oleh kode program maksimal hanya dua puluh satu juta keping selamanya.",
             "setting": "bank", "props": ["coins", "🔒", "balance_scale"], "pose": "point", "emotion": "neutral", "hat": "graduate", "camera_effect": "zoom_in"},
            {"scene_id": 12, "title": "HARGA MEROKET",
             "narration": "Kelangkaan mutlak itulah yang membuat nilainya terus meroket setiap kali semakin banyak orang dan perusahaan besar ikut menyimpannya sebagai emas digital.",
             "setting": "sky", "props": ["rocket", "chart_up", "🪙"], "pose": "celebrate", "emotion": "happy", "hat": "none", "camera_effect": "pan_right"},
            {"scene_id": 13, "title": "BURSA RUNTUH",
             "narration": "Meski begitu, perjalanannya penuh drama: mulai dari peretasan bursa pertukaran raksasa hingga harga yang bisa naik-turun secara ekstrem dalam hitungan hari.",
             "setting": "city", "props": ["fire", "chart_down", "storm_cloud"], "pose": "cry", "emotion": "sad", "hat": "none", "camera_effect": "zoom_out"},
            {"scene_id": 14, "title": "TIDAK PERNAH MATI",
             "narration": "Namun selama internet masih menyala, jaringan tanpa tuan ini terus berdetak setiap sepuluh menit. Menurutmu apakah koin digital adalah masa depan uang? Tulis di komentar ya!",
             "setting": "space", "props": ["🪙", "globe", "⛓️"], "pose": "celebrate", "emotion": "happy", "hat": "crown", "camera_effect": "zoom_in"},
        ],
    }
