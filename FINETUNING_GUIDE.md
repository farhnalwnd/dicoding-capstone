# Fine-Tuning Guide: CV Summarizer & Job Matching System

Panduan lengkap strategi fine-tuning untuk meningkatkan akurasi pencocokan CV dan Job Description menggunakan pendekatan Bi-Encoder berbasis domain.

> **Catatan Arsitektur**: Model Cross-Encoder telah dihapus dari backend dan frontend untuk menyederhanakan alur kerja dan menghemat konsumsi memori RAM/GPU. Semua alur scoring similarity, ranking, dan matching saat ini sepenuhnya ditenagai oleh **Bi-Encoder** (`bi-encoder-cv-matcher`).

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Restructured Fine-Tuning Pipeline (NEW)](#restructured-fine-tuning-pipeline-new)
3. [CSV Dataset Specifications](#csv-dataset-specifications)
4. [Strategi 1: Dynamic Domain-Specific Skills](#strategi-1-dynamic-domain-specific-skills)
5. [Strategi 2: Contrastive Learning (Bi-Encoder)](#strategi-2-contrastive-learning-bi-encoder)
6. [Strategi 3: Cross-Encoder (Re-Ranking) [REMOVED/HISTORICAL]](#strategi-3-cross-encoder-re-ranking)
7. [Strategi 4: Custom Classification Layer (Hybrid) [FUTURE WORK]](#strategi-4-custom-classification-layer-hybrid)
8. [Strategi 5: TSDAE & SimCSE (Unsupervised Adaptation) [FUTURE WORK]](#strategi-5-tsdae--simcse-unsupervised-adaptation)
9. [Perbandingan Strategi](#perbandingan-strategi)

---

## Problem Statement

### Masalah Saat Ini
1. **Skill pattern bersifat hardcode**: File `STANDARD_SKILLS` di `backend/app/services/nlp.py` hanya berisi 50+ skill IT statis. Tidak bisa menangani domain lain seperti HR, Finance, Marketing, dsb.
2. **Embedding kurang akurat untuk sinonim**:
   - "Saya menggunakan Docker selama 4 tahun" vs "Expert dalam menggunakan Docker" → vector masih kurang dekat.
   - Model default `paraphrase-multilingual-MiniLM-L12-v2` tidak dilatih khusus untuk domain rekrutmen.
3. **Threshold statis**: Nilai threshold `0.75` dan `0.82` di `nlp.py` tidak adaptif tergantung konteks.

---

## Restructured Fine-Tuning Pipeline (NEW)

Untuk menjaga modularitas, performa server, dan skalabilitas pengerjaan, pipeline pelatihan dibagi menjadi beberapa bagian terpisah:

```
caps-final/
├── data/
│   └── training/
│       ├── bi_encoder_train.csv      # Data training (Triplet)
│       └── bi_encoder_eval.csv       # Data evaluasi (Triplet)
├── training/
│   ├── scripts/
│   │   └── train_bi_encoder.py       # Script train Bi-Encoder
│   └── notebooks/
│       └── finetuning-model.ipynb    # Jupyter orchestrator
└── models/
    └── bi-encoder-cv-matcher/        # Output model Bi-Encoder
```

---

## CSV Dataset Specifications

Anda harus mempersiapkan dataset dalam bentuk CSV di folder `data/training/` dengan format berikut sebelum menjalankan training:

### 1. Bi-Encoder Dataset (`bi_encoder_train.csv`, `bi_encoder_eval.csv`)
Menggunakan format **Triplet (Anchor, Positive, Negative)** untuk melatih model memahami kedekatan sinonim (semantik).

* **Header**: `anchor,positive,negative`
* **Format**:
  * `anchor`: Kebutuhan job description (misal: "Docker expert required")
  * `positive`: Bagian CV yang relevan (misal: "Menggunakan Docker selama 4 tahun")
  * `negative`: Bagian CV yang tidak relevan (misal: "Keahlian Adobe Photoshop")

* **Contoh Isi CSV**:
  ```csv
  anchor,positive,negative
  "Backend Engineer Python & FastAPI","Pengalaman 3 tahun REST API dengan FastAPI","UI/UX Designer mahir Figma"
  "Docker expert required","Menggunakan Docker selama 4 tahun","Keahlian Adobe Photoshop"
  ```

---

## Strategi 1: Dynamic Domain-Specific Skills

Membuat skill pattern menjadi dinamis berdasarkan domain pekerjaan dengan thresholds yang disesuaikan tingkat sensitivitasnya.

### 1. Struktur File Konfigurasi (`backend/app/core/skills/`)
Dibuat JSON untuk masing-masing domain (IT, HR, Finance, dsb.) dengan dynamic thresholds. Contoh `it.json` (Strict) vs `creative.json` (Relaxed):

#### `it.json` (Strict)
```json
{
  "domain": "IT",
  "threshold_direct_match": 0.80,
  "threshold_master_match": 0.82,
  "skills": ["Python", "Docker", "FastAPI", "Kubernetes", "SQL"],
  "experience_keywords": ["years of experience", "pengalaman tahun"],
  "education_keywords": ["bachelor", "computer science", "informatika"]
}
```

#### `creative.json` (Relaxed)
```json
{
  "domain": "Creative & Marketing",
  "threshold_direct_match": 0.70,
  "threshold_master_match": 0.72,
  "skills": ["Photoshop", "Illustrator", "Figma", "UI/UX", "Copywriting"],
  "experience_keywords": ["portfolio", "creative design"],
  "education_keywords": ["desain", "dkv", "komunikasi"]
}
```

---

## Strategi 2: Contrastive Learning (Bi-Encoder)

Melatih Bi-Encoder menggunakan data triplet dari CSV untuk mengubah representasi spasial vektor agar sinonim recruitment lebih berdekatan.

### Script Training (`training/scripts/train_bi_encoder.py`)
```python
import pandas as pd
from sentence_transformers import SentenceTransformer, InputExample, losses, SentenceTransformerTrainingArguments, SentenceTransformerTrainer
from torch.utils.data import DataLoader

def train_bi_encoder(train_csv, eval_csv, output_path, epochs=5, batch_size=16):
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    # Load custom CSV
    df_train = pd.read_csv(train_csv)
    train_examples = [
        InputExample(texts=[row['anchor'], row['positive'], row['negative']])
        for _, row in df_train.iterrows()
    ]
    
    train_loader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)
    train_loss = losses.MultipleNegativesRankingLoss(model)
    
    args = SentenceTransformerTrainingArguments(
        output_dir=output_path,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=2e-5,
        save_strategy="epoch",
        fp16=True
    )
    
    trainer = SentenceTransformerTrainer(
        model=model,
        args=args,
        train_dataloader=train_loader,
        loss=train_loss
    )
    
    trainer.train()
    model.save_pretrained(output_path)
    print(f"Bi-Encoder Model saved to {output_path}")
```

---

## Strategi 4: Custom Classification Layer (Hybrid)

Menggabungkan embedding static $[u, v, |u - v|]$ ke Dense Network PyTorch/TensorFlow untuk scoring kustom 0-1.

---

## Strategi 5: TSDAE & SimCSE (Unsupervised Adaptation)

Latihan domain-specific menggunakan corpus teks mentah (tanpa label) untuk melatih model memahami pola sintaksis dokumen lamaran kerja dan lowongan kerja.

---

## Perbandingan Strategi

| Strategi | Data Required | Akurasi | Output Model | Use Case |
|---|---|---|---|---|
| **Dynamic Skills** | JSON manual | Medium | Model Default | Deteksi skill per departemen |
| **Bi-Encoder** | Triplet CSV | Tinggi | `models/bi-encoder-cv-matcher` | Semantic search, similarity scoring, filtering |

---

## How to Run Fine-Tuning Now

Ikuti langkah-langkah di bawah untuk mengeksekusi proses fine-tuning pada perangkat Anda:

### Langkah 1: Generate Dataset Sintetis
Jalankan script generator untuk membuat dataset training (bilingual, 11 domain) secara otomatis:
```bash
python training/scripts/generate_dataset.py --num_triplets 2000
```
Dataset akan disimpan di:
- `data/training/bi_encoder_train.csv`

*(Opsional: Jika memiliki data real, timpa file CSV di atas dengan format kolom yang sama).*

### Langkah 2: Jalankan Fine-Tuning
Anda dapat memilih salah satu cara di bawah:

#### Opsi A: Menggunakan Jupyter Notebook (Direkomendasikan untuk monitoring/visual)
1. Buka file `training/notebooks/finetuning-model.ipynb` menggunakan Jupyter Lab / VS Code.
2. Jalankan sel secara bertahap mulai dari **Phase 1** (verifikasi dataset) hingga **Phase 3** (verifikasi output model).

#### Opsi B: Menjalankan Script Python Secara Langsung via Terminal
Jika ingin proses training berjalan di background tanpa membuka Jupyter:

1. **Train Bi-Encoder** (WAJIB):
   ```bash
   python training/scripts/train_bi_encoder.py \
     --train_csv data/training/bi_encoder_train.csv \
     --output_path models/bi-encoder-cv-matcher \
     --epochs 5 \
     --batch_size 16
   ```

### Langkah 3: Verifikasi Output Model
Setelah training selesai, pastikan folder Bi-Encoder terisi (wajib):
```bash
ls -la models/bi-encoder-cv-matcher/
```
