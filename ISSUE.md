# ISSUE: Next Steps - CV Summarizer & Job Matching System

Dokumen ini mencatat apa yang sudah selesai dan apa yang harus dilakukan selanjutnya.

---

## Status Saat Ini

### Selesai
- [x] Dynamic Domain Skills (11 domain JSON + loader)
- [x] Backend integration (nlp.py dynamic threshold + domain parameter)
- [x] Synthetic data generator (generate_dataset.py + 11 domain templates bilingual)
- [x] Dataset CSV generated (bi_encoder_train.csv & cross_encoder_train.csv)
- [x] Training scripts (train_bi_encoder.py & train_cross_encoder.py)
- [x] Jupyter notebook orchestrator (finetuning-model.ipynb)
- [x] FINETUNING_GUIDE.md updated with execution steps

### Belum Selesai
- [ ] Training Bi-Encoder model
- [ ] Training Cross-Encoder model
- [ ] Frontend domain dropdown integration
- [ ] Backend model loading update
- [ ] End-to-end testing

---

## Langkah Selanjutnya

### 1. Training Model

**Prasyarat:**
- GPU (recommended) atau CPU (lama)
- Python dependencies installed: `pip install -r backend/requirements.txt`
- Dataset CSV sudah ada di `data/training/`

**Eksekusi:**

```bash
# Bi-Encoder (estimasi 4-8 jam dengan GPU)
python training/scripts/train_bi_encoder.py \
  --train_csv data/training/bi_encoder_train.csv \
  --output_path models/bi-encoder-cv-matcher \
  --epochs 5 --batch_size 16

# Cross-Encoder (estimasi 6-12 jam dengan GPU)
python training/scripts/train_cross_encoder.py \
  --train_csv data/training/cross_encoder_train.csv \
  --output_path models/cross-encoder-cv-matcher \
  --epochs 3 --batch_size 16
```

**Output yang diharapkan:**
- `models/bi-encoder-cv-matcher/` (berisi config.json, model.safetensors, tokenizer)
- `models/cross-encoder-cv-matcher/` (berisi config.json, model.safetensors, tokenizer)

---

### 2. Backend Model Loading Update

**File yang perlu diupdate:**

#### `backend/app/services/nlp.py`
- Ubah loading model dari `model_main` ke path model baru:
  ```python
  # Sebelumnya
  model = SentenceTransformer(os.getenv("MODEL_MAIN"))
  
  # Sesudahnya
  model = SentenceTransformer("models/bi-encoder-cv-matcher")
  ```
- Atau tetap pakai `MODEL_MAIN` dan update `.env`:
  ```env
  MODEL_MAIN=models/bi-encoder-cv-matcher
  ```

#### `backend/app/services/nlp.py` (match_cv_jd_hybrid)
- Sudah support dynamic domain dan threshold dari JSON (sudah selesai)
- Tidak perlu perubahan tambahan

#### Tambahkan Cross-Encoder service
- Buat `backend/app/services/cross_encoder.py` untuk load Cross-Encoder
- Tambahkan endpoint baru `/api/hr/rank-detailed` yang pakai Cross-Encoder untuk re-ranking

---

### 3. Frontend Domain Dropdown Integration

**File yang perlu diupdate:**

#### `frontend/src/views/AnalyzeView.vue`
- Tambahkan dropdown domain selection
- Kirim parameter `domain` ke API `/api/match-detailed`

#### `frontend/src/views/HRRankView.vue`
- Tambahkan dropdown domain selection
- Kirim parameter `domain` ke API `/api/hr/rank`

#### `frontend/src/views/ScrapeView.vue`
- (Opsional) Tambahkan dropdown domain untuk filter scraping

**Contoh kode dropdown:**
```vue
<template>
  <div class="form-group">
    <label>Domain</label>
    <select v-model="selectedDomain" class="input-field">
      <option value="general">General</option>
      <option value="it">IT</option>
      <option value="hr">HR</option>
      <option value="finance">Finance</option>
      <option value="creative">Creative & Marketing</option>
      <option value="sales">Sales & Business Development</option>
      <option value="legal">Legal</option>
      <option value="pr">PR & Corcom</option>
      <option value="ga">GA</option>
      <option value="cs">CS & Aftersales</option>
      <option value="operational">Operational</option>
    </select>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const selectedDomain = ref('general')
</script>
```

---

### 4. End-to-End Testing

**Test Cases:**

| No | Test | Endpoint | Expected Result |
|---|---|---|---|
| 1 | Upload CV + JD (IT domain) | POST /api/match-detailed | similarity_score, matched_skills, missing_skills |
| 2 | Upload CV + JD (HR domain) | POST /api/match-detailed | similarity_score dengan threshold HR (0.75) |
| 3 | Upload CV + JD (Creative domain) | POST /api/match-detailed | similarity_score dengan threshold Creative (0.70) |
| 4 | Upload multiple CVs (HR rank) | POST /api/hr/rank | Ranked candidates list |
| 5 | Semantic search | POST /api/jobs/semantic-search | Top 10 matching jobs |
| 6 | Scrape jobs | POST /api/scrape-recommend | Scraped job count + recommendations |

**Verifikasi:**
- Pastikan dropdown domain muncul di frontend
- Pastikan threshold berbeda per domain (IT strict, Creative relaxed)
- Pastikan model yang digunakan adalah model hasil fine-tuning

---

### 5. Deployment Update

**Docker Compose:**
- Tambahkan volume mount untuk folder `models/` agar model tersedia di container:
  ```yaml
  backend:
    volumes:
      - ./backend:/app
      - ./models:/app/models  # Tambahkan ini
  ```

**Environment Variables:**
- Update `.env` jika menggunakan path model baru:
  ```env
  MODEL_MAIN=models/bi-encoder-cv-matcher
  ```

---

## Timeline Estimasi

| No | Task | Estimasi | Dependencies |
|---|---|---|---|
| 1 | Training Bi-Encoder | 4-8 jam (GPU) | Dataset CSV |
| 2 | Training Cross-Encoder | 6-12 jam (GPU) | Dataset CSV |
| 3 | Backend model loading update | 1 jam | Model hasil training |
| 4 | Frontend domain dropdown | 2-3 jam | Tidak ada |
| 5 | End-to-end testing | 1-2 jam | Semua task selesai |
| 6 | Deployment update | 0.5 jam | Semua task selesai |
| **Total** | | **15-27 jam** | |

---

## Pertanyaan untuk Diputuskan

1. **Model loading**: Apakah mau update `.env` ke path model baru atau tetap pakai HuggingFace Hub?
2. **Cross-Encoder endpoint**: Apakah perlu tambah endpoint baru atau gabungkan dengan endpoint yang ada?
3. **Training environment**: Apakah akan training di local machine atau cloud server?
4. **Deployment**: Apakah model akan di-bundle dalam Docker image atau di-mount dari host?
