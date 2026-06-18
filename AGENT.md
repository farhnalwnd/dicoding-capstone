# Project Information

## Tech Stack
- **Backend**: FastAPI, Python 3.10+, sentence-transformers, scikit-learn, PyMongo
- **Frontend**: Vue 3, Vite, Axios, Vue Router
- **Database**: MongoDB (Official Image)
- **Database GUI**: Mongo Express
- **Containerization**: Docker, Docker Compose

## Key Files
- `backend/app/services/nlp.py`: Bi-Encoder matching engine, phrase extraction, skill matching, clustering
- `backend/app/services/parser.py`: Text extraction (PDF/DOCX), `clean_text()` for noise removal, STOPWORDS
- `backend/app/services/linkedin_scraper.py`: LinkedIn job scraping with embedding generation
- `backend/app/api/endpoints.py`: Main API routes (scrape-recommend, match-detailed, semantic-search)
- `backend/app/api/hr_endpoints.py`: HR routes (rank, cluster)
- `backend/app/api/jobs_endpoints.py`: Job listing routes (list, clear)
- `frontend/src/views/`: Vue components for each feature
- `frontend/src/router/index.js`: Route configuration
- `training/scripts/generate_dataset.py`: Synthetic dataset generation for Bi-Encoder (triplets)
- `training/scripts/train_bi_encoder.py`: Bi-Encoder training script

## API Endpoints
- `POST /api/scrape-recommend`: Scrape LinkedIn + recommend top 5 jobs
- `POST /api/match-detailed`: Bi-Encoder skill matching (matched vs missing skills)
- `POST /api/jobs/semantic-search`: Vector-based job search using Bi-Encoder
- `GET  /api/jobs`: List all scraped jobs
- `DELETE /api/jobs/clear`: Clear all jobs from database
- `POST /api/hr/rank`: Rank multiple CVs against job description using Bi-Encoder
- `POST /api/hr/cluster`: Auto-cluster candidates by skills using K-Means

## Commands
- `docker compose up --build`: Build and start services
- `docker compose down`: Stop services
- `docker compose exec backend python -m app.services.linkedin_scraper`: Run scraper manually

## Features
1. **Scrape & Find Matches**: Scrape LinkedIn jobs and recommend top 5 matches
2. **Detailed CV-JD Analysis**: Bi-Encoder cosine similarity + semantic skill matching (matched vs missing)
3. **Bulk CV Ranking**: Rank multiple CVs against a job description
4. **Semantic Job Search**: Search jobs using natural language queries
5. **HR Clustering**: Auto-group candidates into talent clusters via K-Means

## Text Processing Pipeline
### 1. Text Cleaning (`clean_text`)
- Removes HTML tags, URLs, emails, phone numbers
- Removes bracketed content: `(e.g., Python)`, `[WFO]`, `(Teknik Informatika)`
- Preserves casing (SQL, CI/CD, Docker remain uppercase)
- Preserves tech symbols: `+`, `#`, `-`, `/`

### 2. Phrase Extraction (`extract_phrases`)
- Splits text by: `\n , ; • | . : ( ) [ ]`
- Strips stopwords from start/end of each phrase iteratively
- Splits phrases containing conjunctions (`and`, `or`, `dan`, `atau`)
- Extracts ALL CAPS acronyms: `SQL`, `AWS`, `GCP`
- Extracts tech-symbol words: `C++`, `C#`, `Vue.js`, `CI/CD`

### 3. Skill Matching (`match_cv_jd_hybrid`)
- **Target skills**: Extracted from JD + domain skills found in JD (via `domain_skills/*.json`)
- **Exact match**: Case-insensitive word boundary regex
- **Semantic fallback**: Cosine similarity with Bi-Encoder embeddings
- **Thresholds**: Domain-specific (e.g., IT: 0.82 for domain skills, 0.75 for extracted phrases)

### 4. Similarity Scoring (`get_similarity_score`)
- Pure Bi-Encoder (Cosine Similarity)
- `model.encode(text1)` + `model.encode(text2)` → `cos_sim()` → 0-100%

## Notes
- Cross-Encoder is removed from the project; Bi-Encoder is used for all scoring
- All text inputs (CV and JD) are cleaned before processing via `clean_text()`
- Domain skill configs are stored in `backend/app/core/skills/*.json`
- Job descriptions are embedded and stored in MongoDB for vector search
- K-Means clustering auto-labels clusters based on extracted skills
- Model `paraphrase-multilingual-MiniLM-L12-v2` is used as the Bi-Encoder
- Mongo Express available at `http://localhost:8081` (admin/password)
