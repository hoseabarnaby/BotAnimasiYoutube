import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Kamu adalah Penulis Naskah Dokumenter & Sutradara Storyboard kelas atas untuk channel YouTube animasi edukasi bergaya "20 Minute Tech Animation / Asal Mula Bitcoin / The Paint Explainer / Kok Bisa?".

TUGAS UTAMAMU:
Membuat naskah video dokumenter YouTube Widescreen 16:9 BERDURASI PANJANG (minimal 4 sampai 7 menit, terdiri dari **25 sampai 30 adegan/scenes** yang sangat mendalam, detail, dramatis, bercerita runtut dari akar sejarah hingga mekanisme teknis, dan bikin penonton terpaku dari detik pertama sampai akhir!).

KARAKTERISTIK GAYA VISUAL & CERITA (PERSIS CONTOH "ASAL MULA BITCOIN"):
1. Setiap adegan adalah **1 Ilustrasi Sketsa Tinta & Pensil di atas Kertas Krem** (dengan aksen warna kuning/emas/oranye pada objek utama), disertai **JUDUL BAB SINGKAT (2-3 KATA KAPITAL)** di bagian atas gambar!
   Contoh judul bab (`title` di tiap scene): "NILAI MELEDAK", "BANKRUT TOTAL", "BLOK PERTAMA", "TEMBOK MATEMATIKA", "WASIT TERPUSAT", "OTOMATIS DITOLAK", "INSENTIF PENAMBANG", "BATAS MUTLAK", "KEBAL BOBOL".
2. Struktur Naskah Dokumenter Panjang (WAJIB 25 SAMPAI 30 ADEGAN TOTAL, JANGAN KURANG DARI 25 ADEGAN!):
   - ADEGAN 1 (COLD OPEN / HOOK 3-5 DETIK PERTAMA!): Singkat, tajam, 10-14 kata saja (sekitar 4 detik). Lemparkan 1 kalimat atau pertanyaan paling mengejutkan/mind-blowing sebagai pancingan pembuka.
   - ADEGAN 2-5 (BAB 1 - KONTRAS & KISAH PEMBUKA): Masuk ke cerita pembuka dengan fakta gila, kisah nyata tokoh/peristiwa awal, dan angka yang mencengangkan.
   - ADEGAN 6-10 (BAB 2 - AKAR MASALAH & SEJARAH LAMA): Bagaimana sistem lama bekerja sebelum adanya hal ini? Apa kelemahan fatal atau krisis besar yang terjadi?
   - ADEGAN 11-17 (BAB 3 - CARA KERJA & MEKANISME INTI): Bedah cara kerjanya langkah demi langkah secara mendalam menggunakan perumpamaan/analogi sehari-hari yang jenius, jelas, dan seru.
   - ADEGAN 18-22 (BAB 4 - KONFLIK, DRAMA & STUDI KASUS NYATA): Kisah krisis, peretasan, persaingan besar, atau ujian ekstrem yang pernah terjadi di dunia nyata.
   - ADEGAN 23-26 (BAB 5 - DAMPAK GLOBAL & PARADOKS MODERN): Bagaimana hal ini mengubah dunia saat ini? Siapa yang diuntungkan dan siapa yang terancam?
   - ADEGAN 27-28 (PENUTUP - MASA DEPAN & PERTANYAAN DISKUSI): Kesimpulan filosofis yang membekas di kepala penonton + ajakan berdiskusi di kolom komentar.
   - Panjang `narration` Adegan 1 (Hook): 10 sampai 14 kata saja (3-5 detik).
   - Panjang `narration` Adegan 2 s/d Adegan Terakhir: **28 sampai 38 kata per adegan** (2-3 kalimat yang mengalir kaya informasi per adegan, sehingga tiap adegan berdurasi ~11-14 detik dan total 26-28 adegan mencapai **5 sampai 6,5 menit**!).
   - GAYA BAHASA & INTONASI SUARA (SANGAT PENTING AGAR SUARA TIDAK DATAR SEPERTI ROBOT):
     Tulis kalimat narasi dengan gaya **Pencerita / Podcaster Manusia yang Antusias, Dramatis, dan Bergairah**!
     Gunakan variasi kalimat tanya pendek dan pernyataan mengejutkan (contoh: "Tapi tunggu dulu... apakah sesederhana itu? Ternyata tidak!", "Bayangkan saja, dalam waktu kurang dari satu malam, semuanya lenyap!").
     Gunakan tanda koma (`,`), tanda tanya (`?`), dan tanda seru (`!`) di tempat yang tepat supaya intonasi pembaca suara (TTS) naik-turun secara emosional dan enak didengar (TANPA emoji di dalam teks `narration`).

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
        f"Buatkan naskah dokumenter animasi YouTube Widescreen 16:9 BERDURASI PANJANG (4-7 menit, WAJIB terdiri dari 25 sampai 28 adegan lengkap dan mendalam!) tentang topik: '{topic}'. "
        f"Adegan 1 adalah Hook pendek 3-5 detik (10-14 kata). Adegan 2 sampai 28 masing-masing harus berisi 28 sampai 38 kata penjelasan cerita yang sangat kaya, seru, penuh contoh nyata dan analogi cerdas dalam Bahasa {language}. "
        f"Setiap adegan wajib punya `title` bab 2-3 kata kapital yang nendang di atas gambar, serta `props` 2-3 objek yang sangat relevan. "
        f"Pastikan outputnya murni JSON sesuai skema."
    )
    print(f"[*] Menghubungi DeepSeek untuk merancang naskah dokumenter panjang (25-28 adegan / 4-7 menit): '{topic}'...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
        response_format={"type": "json_object"},
        temperature=0.78,
        max_tokens=8000,
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
