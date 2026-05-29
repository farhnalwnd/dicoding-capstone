# Code Flow Documentation

## Overview

```
USER (Browser)
    │
    ▼
frontend/src/App.vue          ← Vue 3 SPA (port 5173)
    │
    │ HTTP POST multipart/form-data
    ▼
backend/app/main.py           ← FastAPI entrypoint (port 8000)
    │
    ▼
backend/app/api/endpoints.py  ← Route handler
    │
    ├──► backend/app/services/parser.py   ← Text extraction
    │
    └──► backend/app/services/nlp.py      ← Similarity + dynamic keywords
              │
              └──► MongoDB (cv_matcher.linkedin_jobs) ← Data source
```

---

## 1. Data Ingestion (Scraping)

```
backend/app/services/linkedin_scraper.py
    │
    ├── scrape_linkedin_jobs(keyword, location)
    │     ├── format URL (LinkedIn guest search)
    │     ├── requests.get() with random User-Agent
    │     ├── BeautifulSoup parse <li> elements
    │     └── upsert to MongoDB (cv_matcher.linkedin_jobs) via PyMongo
```

---

## 2. Startup (Backend)

```
uvicorn app.main:app
    │
    ├── main.py
    │     ├── FastAPI() instance created
    │     ├── CORSMiddleware registered → allow_origins=["http://localhost:5173"]
    │     └── api_router mounted at prefix "/api"
    │
    └── services/nlp.py (module-level, runs once on import)
          ├── SentenceTransformer('all-MiniLM-L6-v2') → model loaded into memory
          └── MongoClient(MONGO_URI) connects to MongoDB container
```

---

## 3. Frontend User Interaction

```
App.vue
│
├── handleFileSelect(event)
│     └── selectedFile.value = event.target.files[0]   ← stores File object
│
├── jobDescription.value                                ← v-model bound to textarea
│
└── submit()   ← triggered by button click
      ├── loading.value = true
      ├── new FormData()
      │     ├── .append('cv', selectedFile.value)       ← File object
      │     └── .append('job_description', jobDescription.value)
      │
      └── axios.post('http://localhost:8000/api/match', formData)
                │
                ▼ (HTTP request crosses to backend)
```

---

## 4. Backend Request Handling

```
POST /api/match
    │
    ▼
main.py → CORSMiddleware checks Origin header → passes if localhost:5173
    │
    ▼
api/endpoints.py → match_cv_to_job(cv: UploadFile, job_description: str)
    │
    ├── await cv.read()
    │     └── returns: file_bytes (bytes)
    │
    ├── extract_text(file_bytes, cv.filename)
    │     └── → [goes to parser.py]
    │
    ├── get_similarity_score(cv_text, job_description)
    │     └── → [goes to nlp.py]
    │
    ├── cv_text + " " + job_description → combined_text
    │
    └── extract_keywords(combined_text)
          └── → [goes to nlp.py]
```

---

## 5. parser.py — Text Extraction

```
extract_text(file_bytes: bytes, filename: str) → str
    │
    ├── ext = filename.split(".")[-1].lower()
    │
    ├── ext == "pdf"
    │     └── extract_text_from_pdf(file_bytes)
    │               ├── PdfReader(io.BytesIO(file_bytes))
    │               └── loop pdf.pages → page.extract_text() → concat → return str
    │
    ├── ext in ["docx", "doc"]
    │     └── extract_text_from_docx(file_bytes)
    │               ├── Document(io.BytesIO(file_bytes))
    │               └── loop doc.paragraphs → para.text → join("\n") → return str
    │
    └── fallback
          └── file_bytes.decode("utf-8", errors="ignore") → return str
```

---

## 6. nlp.py — Similarity Scoring

```
get_similarity_score(text1: str, text2: str) → float
    │
    ├── model.encode(text1, convert_to_tensor=True) → emb1 (tensor)
    ├── model.encode(text2, convert_to_tensor=True) → emb2 (tensor)
    ├── util.cos_sim(emb1, emb2).item()             → similarity (float -1.0 to 1.0)
    └── round(max(0.0, min(1.0, similarity)) * 100, 2) → return float (0.0 to 100.0)
```

---

## 7. nlp.py — Keyword Extraction

```
extract_keywords(text: str) → dict
    │
    ├── get_dynamic_keywords()
    │     ├── query MongoDB (linkedin_jobs) for job titles
    │     └── extract unique words → dynamic_skills list
    │
    ├── text_lower = text.lower()
    │
    ├── match text_lower against dynamic skills patterns → populate skills set
    ├── match text_lower against static experience patterns → populate experience set
    └── match text_lower against static education patterns  → populate education set
          │
          └── return {
                "skills":     list(skills),
                "experience": list(experience),
                "education":  list(education)
              }
```

---

## 8. Response — Backend to Frontend

```
endpoints.py
    │
    └── return {
          "similarity_score": float,     ← 0.0 to 100.0
          "insights": {
            "skills":     [str, ...],
            "experience": [str, ...],
            "education":  [str, ...]
          }
        }
              │
              ▼ (JSON HTTP response)
```

---

## 9. Frontend Response Handling

```
App.vue → submit()
    │
    ├── res = await axios.post(...)
    │     └── res.data = { similarity_score, insights }
    │
    ├── result.value = res.data           ← reactive ref updated
    │
    └── Vue re-renders template
          ├── result.similarity_score → progress-bar width (CSS style binding)
          ├── result.insights.skills  → v-for list render
          ├── result.insights.experience → v-for list render
          └── result.insights.education  → v-for list render

    error path:
    └── catch(e) → error.value = e.response?.data?.detail || fallback string
```
