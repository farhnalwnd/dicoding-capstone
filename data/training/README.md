# Dataset Training CV Matching System

Folder ini berisi dataset training untuk fine-tuning model Bi-Encoder dan Cross-Encoder.

## Struktur File

```
data/training/
├── bi_encoder_train.csv      # Data training Bi-Encoder (Triplet)
├── bi_encoder_eval.csv       # Data evaluasi Bi-Encoder (Triplet)
├── cross_encoder_train.csv   # Data training Cross-Encoder (Pairs)
├── cross_encoder_eval.csv    # Data evaluasi Cross-Encoder (Pairs)
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

### 2. Cross-Encoder Dataset (Pairs)

Format: **Labeled Pairs**

**Header CSV:**
```csv
cv_text,jd_text,label
```

**Kolom:**
- `cv_text`: Teks CV atau bagian CV
- `jd_text`: Teks job description
- `label`: `1.0` (Match/Cocok) atau `0.0` (No Match/Tidak Cocok)

**Contoh:**
```csv
cv_text,jd_text,label
"Pengalaman 3 tahun Python Django","Backend Engineer Python & Django required",1.0
"UI/UX Designer mahir Figma","Backend Engineer Python required",0.0
"Menggunakan Docker 4 tahun","DevOps Engineer with Docker experience",1.0
```

**Rekomendasi:**
- Minimal 2000 baris untuk training
- 400-800 baris untuk evaluasi
- Balance antara label 1.0 dan 0.0 (sekitar 50-70% label 1.0)

## Cara Menggunakan

1. **Siapkan dataset Anda** dalam format CSV di folder ini
2. **Jalankan notebook** `finetuning-model.ipynb` di root project
3. **Pilih phase training** yang diinginkan (Bi-Encoder atau Cross-Encoder)
4. **Model output** akan tersimpan di `models/`

## Catatan Penting

- Pastikan CSV menggunakan encoding UTF-8
- Hindari baris kosong atau nilai null
- Gunakan tanda kutip (`"`) untuk teks yang mengandung koma
- Dataset harus representatif untuk domain target (IT, HR, Finance, dll)
