# Code Flow Documentation

## Overview

```
USER (Browser)
    │
    ▼
frontend/src/App.vue          ← Vue 3 SPA (port 5173) with Vue Router
    │
    │ HTTP POST multipart/form-data / JSON
    ▼
backend/app/main.py           ← FastAPI entrypoint (port 8000)
    │
    ├──► backend/app/api/endpoints.py   ← General API routes (match, search, scrape)
    ├──► backend/app/api/hr_endpoints.py ← HR API routes (rank, cluster)
    ├──► backend/app/api/jobs_endpoints.py ← Job listing API routes
    │
    ├──► backend/app/services/parser.py   ← Text extraction + stopword filtering
    ├──► backend/app/services/nlp.py      ← Bi-Encoder matching, phrase extraction, clustering
    └──► backend/app/services/linkedin_scraper.py ← Job scraping + embedding
              │
              └──► MongoDB (cv_matcher.linkedin_jobs) ← Data source with stored vectors
```

---

## 2. Text Cleaning Pipeline

All text (CV and JD) goes through `clean_text()` before any matching:

```
Raw Text (CV/JD)
    │
    ├──► Remove HTML tags          <p>, <strong>, <br>, etc.
    ├──► Remove bracketed content  (e.g., Python), [WFO], (Teknik Informatika)
    ├──► Remove URLs               https://company.com/...
    ├──► Remove Emails             hr@company.com
    ├──► Remove Phone Numbers      +62 812-3456-7890
    ├──► Remove special chars     保留: +, #, -, / (tech symbols)
    ├──► Collapse whitespace       "  " → " "
    │
    └──► Clean Text Output
```

**Important**: `clean_text()` preserves casing (does NOT lowercase), so skill acronyms like `SQL`, `AWS`, `CI/CD` are correctly detected in subsequent steps.

---

## 3. Hybrid Semantic Skill Matching Flow

```
[Match Detailed: CV-JD Analysis]
  │
  ├──► cv_text = extract_text(cv_file)
  │      └──► extract_text_from_pdf/docx → clean_text()
  │
  ├──► jd_clean = clean_text(job_description)
  │
  ├──► similarity_score = get_similarity_score(cv_text, jd_clean)
  │      ├── model.encode(cv_text) → cv_emb  (Bi-Encoder)
  │      ├── model.encode(jd_clean) → jd_emb  (Bi-Encoder)
  │      └── cosine_similarity(cv_emb, jd_emb) × 100 → percentage
  │
  ├──► matched_skills, missing_skills = match_cv_jd_hybrid(cv_text, jd_clean, domain)
  │      │
  │      ├── Extract target skills from JD:
  │      │     ├── extract_phrases(jd_clean) → jd_phrases
  │      │     │     └── Split by: \n , ; • | . : ( ) [ ]
  │      │     ├── Strip stopwords from start/end of each phrase
  │      │     ├── Split phrases containing conjunctions (and/or/dan/atau)
  │      │     ├── Validate each sub-phrase against domain_skills (semantic similarity)
  │      │     └── Add exact-match domain skills found in JD
  │      │
  │      ├── Extract CV phrases:
  │      │     └── extract_phrases(cv_text) → cv_phrases
  │      │
  │      ├── For each target skill:
  │      │     ├── 1. Exact match check in CV (case-insensitive)
  │      │     │     └── Matched with score 100.0
  │      │     └── 2. Semantic fallback (cosine similarity)
  │      │           ├── Encode skill → encode each cv_phrase
  │      │           ├── If max_sim >= threshold → matched
  │      │           └── Else → missing
  │      │
  │      ├── Thresholds from domain config (e.g., it.json):
  │      │     ├── threshold_master_match: 0.82 (for domain skills)
  │      │     └── threshold_direct_match: 0.75 (for extracted phrases)
  │      │
  │      └── Return top 15 matched and top 15 missing skills
  │
  └──► Return { similarity_score, matched_skills, missing_skills, domain }
```

---

## 4. Scrape & Recommend Flow (Job Seeker)

```
[Scrape & Find Matches]
  │
  ├──► scrape_linkedin_jobs(keyword, location, time_range)
  │      ├── Fetch jobs from LinkedIn guest API
  │      ├── For each job card:
  │      │     ├── scrape_job_description(job_url) → raw description
  │      │     ├── description_embedding = model.encode(description)
  │      │     └── Save to MongoDB (upsert by URL)
  │      └── Return scraped_count
  │
  └──► Response: { scraped_count, recommendations: [...] }
```

---

## 5. Bulk CV Ranking Flow (HR)

```
[Bulk CV Ranking]
  │
  ├──► For each uploaded CV:
  │     ├── cv_text = extract_text(file) → clean_text()
  │     ├── candidate_name = extract_candidate_name(cv_text)
  │     ├── similarity_score = get_similarity_score(cv_text, job_description)
  │     └── Append to candidates list
  │
  ├──► Sort candidates by score (descending)
  ├──► Add rank numbers (1, 2, 3, ...)
  └──► Return ranked candidates list
```

---

## 6. Candidate Clustering Flow (HR)

```
[Candidate Clustering]
  │
  ├──► For each uploaded CV:
  │     ├── cv_text = extract_text(file) → clean_text()
  │     └── Collect texts and filenames
  │
  ├──► cluster_documents(texts, filenames, num_clusters)
  │     ├── model.encode(texts) → document embeddings
  │     ├── K-Means clustering (sklearn)
  │     ├── For each cluster:
  │     │     ├── extract_phrases from combined cluster texts
  │     │     ├── Match against domain skills (cosine similarity > 0.82)
  │     │     └── Suggest label: "Skill A / Skill B / Skill C"
  │     └── Return list of clusters
  │
  └──► Return clusters with candidates and suggested labels
```

---

## 7. Semantic Job Search Flow

```
[Semantic Job Search]
  │
  ├──► cv_text = extract_text(cv_file) → clean_text()
  ├──► query_emb = model.encode(cv_text)
  ├──► Load all jobs with description embeddings from MongoDB
  ├──► For each job:
  │     ├── Compute cosine similarity: np.dot(query_emb, desc_emb)
  │     └── Bound to [0, 1] and scale to percentage
  ├──► Sort jobs by highest similarity
  └──► Return Top 10 matching jobs
```

---

## 8. Phrase Extraction Rules (`extract_phrases`)

```
Raw Text Input
    │
    ├──► Split by: \n , ; • | . : ( ) [ ]
    │
    ├──► For each fragment:
    │     ├── Skip if length <= 2
    │     ├── Skip if more than 4 words
    │     ├── If contains conjunction (and/or/dan/atau/with/...) in middle:
    │     │     └── Split into sub-fragments, evaluate each separately
    │     ├── Strip ALL stopwords from start and end (iteratively)
    │     ├── Skip if all remaining words are stopwords
    │     └── Add to valid_phrases if length > 2
    │
    ├──► Single word extraction:
    │     ├── Extract words with tech characters (+, #, ., -): C++, C#, Vue.js, CI/CD
    │     ├── Extract ALL CAPS acronyms (>= 2 chars): SQL, AWS, GCP
    │     └── Skip if word is in STOPWORDS
    │
    └──► Return deduplicated valid_phrases
```

---

## 9. Key File Reference

| File | Purpose |
|------|---------|
| `backend/app/services/nlp.py` | Bi-Encoder scoring, phrase extraction, hybrid skill matching |
| `backend/app/services/parser.py` | Text extraction (PDF/DOCX), `clean_text()`, STOPWORDS |
| `backend/app/services/linkedin_scraper.py` | LinkedIn job scraping, embedding generation |
| `backend/app/api/endpoints.py` | `/match-detailed`, `/scrape-recommend`, `/jobs/semantic-search` |
| `backend/app/api/hr_endpoints.py` | `/hr/rank`, `/hr/cluster` |
| `backend/app/api/jobs_endpoints.py` | `/jobs`, `/jobs/clear` |
| `backend/app/core/domain_loader.py` | Domain config loader (skills, thresholds) |
| `backend/app/core/skills/*.json` | Domain skill definitions and thresholds |
