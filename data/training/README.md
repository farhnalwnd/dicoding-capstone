# Dataset Training CV Matching System

Folder ini berisi dataset training untuk fine-tuning model Bi-Encoder dan Cross-Encoder.

## Struktur File

```
data/training/
├── bi_encoder_train.csv      # Data training Bi-Encoder (Triplet)
├── bi_encoder_eval.csv       # Data evaluasi Bi-Encoder (Triplet)
└── README.md                 # File ini
```

## Format Dataset

### 1. Bi-Encoder Dataset (Triplet)

Format: **Triplet (Anchor, Positive, Negative)**

**Header CSV:**
```csv
anchor,positive,negative
```

**Kolom:**
- `anchor`: Kebutuhan job description atau skill requirement
- `positive`: Bagian CV yang relevan/mencocokkan
- `negative`: Bagian CV yang tidak relevan/tidak mencocokkan

**Contoh:**
```csv
anchor,positive,negative
"Backend Engineer Python & FastAPI","Pengalaman 3 tahun REST API dengan FastAPI","UI/UX Designer mahir Figma"
"Docker expert required","Menggunakan Docker selama 4 tahun","Keahlian Adobe Photoshop"
"Recruitment Specialist","Merekrut 30 staff selama 2 tahun","Backend Developer Python"
```

**Rekomendasi:**
- Minimal 1000 baris untuk training
- 200-500 baris untuk evaluasi
- Variasi domain (IT, HR, Finance, dll)

## Cara Menggunakan

1. **Siapkan dataset Anda** dalam format CSV di folder ini
2. **Jalankan notebook** `finetuning-model.ipynb` di root project
3. **Model output** akan tersimpan di `models/`

## Catatan Penting

- Pastikan CSV menggunakan encoding UTF-8
- Hindari baris kosong atau nilai null
- Gunakan tanda kutip (`"`) untuk teks yang mengandung koma
- Dataset harus representatif untuk domain target (IT, HR, Finance, dll)
