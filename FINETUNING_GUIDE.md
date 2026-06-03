# Fine-Tuning Guide: CV Summarizer & Job Matching System

Panduan lengkap strategi fine-tuning untuk meningkatkan akurasi pencocokan CV dan Job Description.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Strategi 1: Dynamic Domain-Specific Skills](#strategi-1-dynamic-domain-specific-skills)
3. [Strategi 2: Contrastive Learning (Bi-Encoder)](#strategi-2-contrastive-learning-bi-encoder)
4. [Strategi 3: Custom Classification Layer (Hybrid)](#strategi-3-custom-classification-layer-hybrid)
5. [Strategi 4: Cross-Encoder](#strategi-4-cross-encoder)
6. [Strategi 5: TSDAE (Unsupervised Adaptation)](#strategi-5-tsdae-unsupervised-adaptation)
7. [Strategi 6: SimCSE (Self-Supervised Contrastive)](#strategi-6-simcse-self-supervised-contrastive)
8. [Perbandingan Strategi](#perbandingan-strategi)
9. [Rekomendasi Pipeline](#rekomendasi-pipeline)

---

## Problem Statement

### Masalah Saat Ini

1. **Skill pattern bersifat hardcode**: File `STANDARD_SKILLS` di `backend/app/services/nlp.py` hanya berisi 50+ skill IT statis. Tidak bisa menangani domain lain seperti HR, Finance, Marketing, dsb.

2. **Embedding kurang akurat untuk sinonim**:
   - "Saya menggunakan Docker selama 4 tahun" vs "Expert dalam menggunakan Docker" → vector masih kurang dekat.
   - Model default `paraphrase-multilingual-MiniLM-L12-v2` tidak dilatih khusus untuk domain rekrutmen.

3. **Threshold statis**: Nilai threshold `0.75` dan `0.82` di `nlp.py` tidak adaptif tergantung konteks.

### Target yang Ingin Dicapai

- Skill pattern dinamis berdasarkan domain (IT, HR, Finance, dsb).
- Model memahami sinonim rekrutmen (pengalaman 4 tahun $\approx$ expert).
- Skor kecocokan lebih akurat dan interpretable.

---

## Strategi 1: Dynamic Domain-Specific Skills

### Kegunaan

Membuat skill pattern menjadi dinamis berdasarkan domain pekerjaan. HR recruiter membutuhkan skill yang berbeda dari IT developer. Dengan domain-specific skills, perbandingan menjadi lebih relevan.

### Cara Melakukan

#### 1. Buat Struktur Direktori

```
backend/app/core/skills/
├── it.json
├── hr.json
├── finance.json
├── marketing.json
└── general.json
```

#### 2. Format File JSON

```json
{
  "domain": "IT",
  "skills": [
    "Python", "JavaScript", "TypeScript", "Vue.js", "React",
    "Angular", "Node.js", "FastAPI", "Flask", "Django",
    "Docker", "Kubernetes", "SQL", "PostgreSQL", "MySQL",
    "MongoDB", "Git", "NLP", "Machine Learning", "Deep Learning",
    "AWS", "GCP", "Azure", "Tailwind CSS", "HTML", "CSS",
    "Java", "C++", "C#", "Linux", "Bash", "REST API", "GraphQL",
    "TensorFlow", "PyTorch", "Scikit-Learn", "Pandas", "NumPy",
    "Apache Spark", "Hadoop", "Kafka", "RabbitMQ", "Redis",
    "Elasticsearch", "CI/CD", "Jenkins", "Terraform", "Ansible",
    "Agile", "Scrum", "Next.js", "Express.js"
  ],
  "experience_keywords": [
    "years of experience", "pengalaman tahun",
    "previously worked", "sebelumnya bekerja"
  ],
  "education_keywords": [
    "bachelor", "master", "degree", "sarjana", "magister",
    "university", "universitas"
  ]
}
```

```json
{
  "domain": "HR",
  "skills": [
    "Recruitment", "Talent Acquisition", "Onboarding",
    "Performance Management", "Employee Relations",
    "Compensation & Benefits", "Training & Development",
    "HRIS", "SAP SuccessFactors", "Workday",
    "Labor Law", "Industrial Relations", "Payroll",
    "Workforce Planning", "Succession Planning",
    "Diversity & Inclusion", "Employee Engagement",
    "Exit Interview", "Conflict Resolution", "Coaching"
  ],
  "experience_keywords": [
    "years in HR", "pengalaman di HR",
    "managing recruitment", "mengelola rekrutmen"
  ],
  "education_keywords": [
    "bachelor", "master", "degree", "sarjana",
    "psychology", "psikologi", "human resource"
  ]
}
```

#### 3. Modifikasi Backend

```python
# backend/app/core/domain_loader.py
import json
import os

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")
_available_domains = None

def get_available_domains():
    global _available_domains
    if _available_domains is None:
        _available_domains = []
        for f in os.listdir(SKILLS_DIR):
            if f.endswith(".json"):
                _available_domains.append(f.replace(".json", ""))
    return _available_domains

def load_domain_config(domain: str = "general"):
    filepath = os.path.join(SKILLS_DIR, f"{domain}.json")
    if not os.path.exists(filepath):
        filepath = os.path.join(SKILLS_DIR, "general.json")
    with open(filepath, "r") as f:
        return json.load(f)

def get_skills_for_domain(domain: str):
    config = load_domain_config(domain)
    return config.get("skills", [])
```

#### 4. Update Endpoint

```python
# backend/app/api/endpoints.py
from fastapi import APIRouter, UploadFile, File, Form
from app.services.parser import extract_text
from app.services.nlp import get_similarity_score, match_cv_jd_hybrid, model
from app.core.domain_loader import get_skills_for_domain

@router.post("/match-detailed")
async def match_cv_to_job_detailed(
    cv: UploadFile = File(...),
    job_description: str = Form(...),
    domain: str = Form("it")  # Parameter domain baru
):
    file_bytes = await cv.read()
    cv_text = extract_text(file_bytes, cv.filename)

    # Load skill berdasarkan domain
    domain_skills = get_skills_for_domain(domain)

    similarity_score = get_similarity_score(cv_text, job_description)
    matched_skills, missing_skills = match_cv_jd_hybrid(
        cv_text, job_description, custom_skills=domain_skills
    )

    return {
        "similarity_score": similarity_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "domain": domain
    }
```

---

## Strategi 2: Contrastive Learning (Bi-Encoder)

### Kegunaan

Mendekatkan vector embedding antara frasa yang memiliki makna sama meskipun berbeda kata.
Contoh: "Saya menggunakan Docker selama 4 tahun" $\rightarrow$ vector akan dekat dengan "Expert dalam menggunakan Docker".

Ini menggunakan pendekatan **siamese network** di mana dua input diproses oleh model yang sama, dan loss function memaksa positive pair berdekatan sementara negative pair menjauh.

### Konsep

```
Anchor: "Keahlian Docker tingkat lanjut"
         ↓
    [SentenceTransformer] → vector u
         ↓

Positive: "Pengalaman 4 tahun deploy Docker container"
         ↓
    [SentenceTransformer] → vector v
         ↓

Loss: minimize distance(u, v) untuk positive
      maximize distance(u, n) untuk negative
```

### Cara Melakukan

#### 1. Persiapan Dataset

Format **Triplet** (Anchor, Positive, Negative):

```python
from sentence_transformers import InputExample

training_examples = [
    InputExample(
        texts=[
            "Dibutuhkan Backend Engineer Python & FastAPI",        # Anchor (JD)
            "Pengalaman 2 tahun develop REST API pakai FastAPI",   # Positive
            "UI/UX Designer mahir Figma dan Adobe Illustrator"     # Negative
        ]
    ),
    InputExample(
        texts=[
            "Backend Engineer Python & FastAPI",
            "Expert dalam menggunakan Docker selama 4 tahun",      # Positive
            "Sales Executive dengan pengalaman 3 tahun di retail"  # Negative
        ]
    ),
    InputExample(
        texts=[
            "DevOps Engineer",
            "Mengelola CI/CD pipeline dengan Jenkins dan Docker",  # Positive
            "Content Writer untuk blog perusahaan"                  # Negative
        ]
    ),
    # Tambahkan ribuan contoh serupa untuk hasil optimal
]
```

#### 2. Setup DataLoader dan Loss

```python
from torch.utils.data import DataLoader
from sentence_transformers import SentenceTransformer, losses

# Load model dasar
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Buat dataloader
train_dataloader = DataLoader(
    training_examples,
    shuffle=True,
    batch_size=16
)

# Loss function: MultipleNegativesRankingLoss
# Membandingkan anchor-positive vs anchor-negative
train_loss = losses.MultipleNegativesRankingLoss(model=model)
```

#### 3. Training Loop

```python
from sentence_transformers import SentenceTransformerTrainingArguments
from sentence_transformers.trainer import SentenceTransformerTrainer

# Konfigurasi training
args = SentenceTransformerTrainingArguments(
    output_dir="./models/finetuned-cv-matcher",
    num_train_epochs=5,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
    warmup_steps=50,
    weight_decay=0.01,
    logging_steps=10,
    save_strategy="epoch",
    fp16=True,  # Gunakan jika GPU mendukung
)

# Train
trainer = SentenceTransformerTrainer(
    model=model,
    args=args,
    train_dataloader=train_dataloader,
    loss=train_loss,
)

trainer.train()

# Simpan model
model.save_pretrained("./models/finetuned-cv-matcher")
```

#### 4. Evaluasi

```python
from sentence_transformers.evaluation import InformationRetrievalEvaluator

evaluator = InformationRetrievalEvaluator(
    queries=eval_queries,       # list of JD texts
    corpus=eval_corpus,         # list of CV texts
    relevant_docs=eval_mapping, # dict {query_id: {corpus_id: 1}}
)

score = evaluator(model)
print(f"MRR@10: {score['main_score']:.4f}")
```

### Hyperparameters

| Parameter | Nilai | Keterangan |
|---|---|---|
| Base Model | `paraphrase-multilingual-MiniLM-L12-v2` | Multilingual, support Indonesia |
| Optimizer | `AdamW` | Standard untuk transformer |
| Learning Rate | `2e-5` | Terlalu besar = catastrophic forgetting |
| Epochs | `3-5` | Lebih dari 5 = overfitting |
| Batch Size | `16-32` | Sesuaikan dengan VRAM GPU |
| Warmup Steps | `10%` total steps | Stabilkan training awal |
| Weight Decay | `0.01` | Regularisasi |

---

## Strategi 3: Custom Classification Layer (Hybrid)

### Kegunaan

Menggabungkan dua embedding (CV + JD) ke dalam neural network custom untuk menghasilkan skor kecocokan 0-1. Model BERT/MiniLM bertindak sebagai **feature extractor** statis, sedangkan Dense Layers yang menentukan kecocokan.

### Konsep

```
CV Text → [SentenceTransformer] → Vector u (384-dim)
                                        ↓
JD Text → [SentenceTransformer] → Vector v (384-dim)
                                        ↓
                              [u, v, |u - v|] (1152-dim)
                                        ↓
                              Dense(256) → ReLU → Dropout(0.2)
                                        ↓
                              Dense(128) → ReLU → Dropout(0.2)
                                        ↓
                              Dense(1) → Sigmoid
                                        ↓
                              Skor Kecocokan (0.0 - 1.0)
```

### Cara Melakukan

#### 1. Buat Model PyTorch

```python
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer

class CVMatchClassifier(nn.Module):
    def __init__(self, base_model_name, dropout=0.2):
        super().__init__()
        self.base_model = SentenceTransformer(base_model_name)
        embedding_dim = self.base_model.get_sentence_embedding_dimension()

        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(embedding_dim * 3, 256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

        # Freeze base model (optional, bisa di-unfreeze untuk fine-tune)
        for param in self.base_model.parameters():
            param.requires_grad = False

    def forward(self, cv_text, jd_text):
        u = self.base_model.encode(cv_text, convert_to_tensor=True)
        v = self.base_model.encode(jd_text, convert_to_tensor=True)

        # Gabungkan: [u, v, |u - v|]
        combined = torch.cat([u, v, torch.abs(u - v)], dim=-1)

        score = self.classifier(combined)
        return score.squeeze(-1)
```

#### 2. Dataset dan Training

```python
from torch.utils.data import Dataset, DataLoader

class CVJDDataset(Dataset):
    def __init__(self, cv_texts, jd_texts, labels):
        self.cv_texts = cv_texts
        self.jd_texts = jd_texts
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.cv_texts[idx], self.jd_texts[idx], self.labels[idx]

# Training loop
model = CVMatchClassifier("paraphrase-multilingual-MiniLM-L12-v2")
optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
criterion = nn.BCEWithLogitsLoss()

for epoch in range(5):
    model.train()
    for cv_text, jd_text, label in train_loader:
        optimizer.zero_grad()
        score = model(cv_text, jd_text)
        loss = criterion(score, label)
        loss.backward()
        optimizer.step()
```

### Hyperparameters

| Parameter | Nilai | Keterangan |
|---|---|---|
| Hidden Layers | 256, 128 | Cukup untuk match task |
| Activation | ReLU | Standard |
| Output Activation | Sigmoid | Output 0-1 |
| Dropout | 0.2 | Cegah overfitting |
| Loss Function | `BCEWithLogitsLoss` | Binary classification |
| Optimizer | `AdamW` | |
| Learning Rate | `2e-5` | |
| Epochs | `5-10` | |

---

## Strategi 4: Cross-Encoder

### Kegunaan

Memproses CV dan JD **bersama-sama** dalam satu forward pass. Lebih akurat dari Bi-Encoder karena model bisa melihat interaksi langsung antara CV dan JD. Cocok untuk **re-ranking** kandidat setelah screening awal.

### Konsep

```
"[CLS] CV Text [SEP] JD Text [SEP]"
         ↓
   [Cross-Encoder Transformer]
         ↓
   [CLS] token embedding
         ↓
   Linear Layer → Sigmoid
         ↓
   Skor Kecocokan (0.0 - 1.0)
```

### Cara Melakukan

#### 1. Setup Cross-Encoder

```python
from sentence_transformers import CrossEncoder

# Model pre-trained untuk NLI/match task
model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2",
    max_length=512
)

# Prediksi
pairs = [
    ("Pengalaman 3 tahun Python Django", "Backend Engineer Python & Django"),
    ("UI/UX Designer mahir Figma", "Backend Engineer Python & Django"),
]
scores = model.predict(pairs)
# Output: [0.87, 0.12]
```

#### 2. Fine-Tune Cross-Encoder

```python
from sentence_transformers import CrossEncoder
from sentence_transformers.readers import InputExample

# Dataset
train_examples = [
    InputExample(texts=["CV text...", "JD text..."], label=1.0),  # Match
    InputExample(texts=["CV text...", "JD text..."], label=0.0),  # No match
]

# Fine-tune
model = CrossEncoder(
    "paraphrase-multilingual-MiniLM-L12-v2",
    num_labels=1,
    max_length=512
)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=3,
    warmup_steps=100,
    output_dir="./models/cross-encoder-cv-matcher"
)
```

### Bi-Encoder vs Cross-Encoder

| Aspek | Bi-Encoder | Cross-Encoder |
|---|---|---|
| Kecepatan | Cepat (encode terpisah) | Lambat (encode bersama) |
| Akurasi | Baik | Sangat Baik |
| Use Case | Semantic search, screening | Re-ranking, final scoring |
| Skalabilitas | Cocok untuk ribuan CV | Cocok untuk ratusan CV |

---

## Strategi 5: TSDAE (Unsupervised Adaptation)

### Kegunaan

Adaptasi model ke domain rekrutmen tanpa perlu **label data**. Model belajar memahami struktur kalimat CV dan JD melalui tugas rekonstruksi teks yang dirusak (denoising). Cocok untuk tahap awal sebelum supervised fine-tuning.

### Konsep

```
Original: "Pengalaman 3 tahun menggunakan Docker dan Kubernetes"
              ↓
Denoised: "Pengalaman    tahun       Docker     Kubernetes" (hapus random words)
              ↓
Model diminta: prediksi teks asli dari teks yang dirusak
              ↓
Model belajar: konteks dan struktur kalimat domain rekrutmen
```

### Cara Melakukan

#### 1. Siapkan Dataset Teks Mentah

```python
# Kumpulkan teks CV dan JD tanpa label
corpus_texts = [
    "Pengalaman 2 tahun backend developer Python FastAPI",
    "Menguasai Docker Kubernetes CI/CD pipeline",
    "Sarjana Informatika Universitas Indonesia",
    # ... ribuan teks lainnya
]
```

#### 2. Training TSDAE

```python
from sentence_transformers import SentenceTransformer, losses, models
from torch.utils.data import DataLoader

# Load model
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Buat dataset
train_examples = [InputExample(texts=[text]) for text in corpus_texts]
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

# Loss function TSDAE
train_loss = losses.DenoisingAutoEncoderLoss(
    model,
    decoder_name_or_path="paraphrase-multilingual-MiniLM-L12-v2",
    tie_encoder_decoder=True  # Hemat memori
)

# Training
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=10,
    weight_decay=0,
    scheduler="constantlr",
    optimizer_params={"lr": 3e-5}
)

model.save_pretrained("./models/tsdae-cv-matcher")
```

---

## Strategi 6: SimCSE (Self-Supervised Contrastive)

### Kegunaan

Meningkatkan kualitas embedding dengan konsep sederhana: teks yang sama harus dekat di vector space, meskipun diberikan dropout yang berbeda. Tanpa perlu dataset label, model belajar representasi yang lebih robust.

### Konsep

```
Same Sentence: "Pengalaman 3 tahun Python"
         ↓
    [Dropout mask A] → vector u
    [Dropout mask B] → vector v
         ↓
    Loss: minimize distance(u, v)
    Maximize distance dari negative samples
```

### Cara Melakukan

```python
from sentence_transformers import SentenceTransformer, losses, InputExample
from torch.utils.data import DataLoader

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Dataset: teks saja tanpa label
train_texts = [
    "Pengalaman 3 tahun Python Django REST API",
    "Menguasai Docker Kubernetes dan CI/CD",
    # ... kumpulan teks CV dan JD
]

# Buat pair: setiap teks jadi anchor + positive (dirinya sendiri)
train_examples = [InputExample(texts=[t, t]) for t in train_texts]
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

# MultipleNegativesRankingLoss otomatis treat setiap pair
# dalam batch sebagai positive dan sisanya sebagai negatives
train_loss = losses.MultipleNegativesRankingLoss(model)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=1,
    warmup_steps=100,
    weight_decay=0.01
)

model.save_pretrained("./models/simcse-cv-matcher")
```

---

## Perbandingan Strategi

| Strategi | Data Required | Akurasi | Komputasi | Kompleksitas | Hasil |
|---|---|---|---|---|---|
| **Dynamic Skills** | JSON manual | Medium | Rendah | Rendah | Skill pattern relevan per domain |
| **Contrastive Learning** | Triplet pairs | Tinggi | Medium | Medium | Vector sinonim lebih dekat |
| **Custom Classifier** | Labeled pairs | Tinggi | Medium | Tinggi | Skor match yang lebih presisi |
| **Cross-Encoder** | Labeled pairs | Sangat Tinggi | Tinggi | Medium | Re-ranking terbaik |
| **TSDAE** | Teks mentah saja | Medium | Rendah | Rendah | Model适应 domain |
| **SimCSE** | Teks mentah saja | Medium | Rendah | Rendah | Embedding lebih robust |

---

## Rekomendasi Pipeline

### Fase 1: Domain Adaptation (Tanpa Label)

```
Raw CV/JD Texts
      ↓
  TSDAE Training → Model adapted ke domain rekrutmen
      ↓
  SimCSE Training → Embedding lebih robust
      ↓
  Simpan: models/adapted-base/
```

### Fase 2: Supervised Fine-Tuning (Dengan Label)

```
Triplet Dataset (Anchor, Positive, Negative)
      ↓
  Contrastive Learning → Model paham sinonim rekrutmen
      ↓
  Simpan: models/finetuned-contrastive/
      ↓
  (Opsional) Cross-Encoder → Fine-tune untuk re-ranking
      ↓
  Simpan: models/finetuned-cross-encoder/
```

### Fase 3: Integration ke Backend

```
User Request
      ↓
  Dynamic Skills Loader → Pilih skill berdasarkan domain
      ↓
  Bi-Encoder (Adapted Model) → Screening awal (cepat)
      ↓
  Cross-Encoder → Re-ranking top-N kandidat (akurat)
      ↓
  Custom Classifier → Skor final (opsional)
      ↓
  Response ke Frontend
```

### Estimasi Kebutuhan

| Fase | Data | Waktu Training | Hardware |
|---|---|---|---|
| TSDAE + SimCSE | 1000+ teks CV/JD | 2-4 jam | CPU atau GPU |
| Contrastive | 500+ triplet | 4-8 jam | GPU (recommended) |
| Cross-Encoder | 1000+ labeled pairs | 6-12 jam | GPU (wajib) |
| Dynamic Skills | JSON manual | 1 jam | Tidak perlu |
