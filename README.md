# CV Summarizer & Job Matching System

A web-based application for CV Summarization and Job Matching using Natural Language Processing (NLP).

## Architecture

- **Backend**: FastAPI (Python 3.10+)
- **Frontend**: Vue.js (Vue 3 with Vite)
- **NLP Engine**: `sentence-transformers` (all-MiniLM-L6-v2)
- **Containerization**: Docker & Docker Compose

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── keywords.json      # Dynamic keyword patterns
│   │   ├── api/
│   │   │   └── endpoints.py       # POST /api/match
│   │   ├── services/
│   │   │   ├── parser.py          # PDF/DOCX text extraction
│   │   │   └── nlp.py             # Similarity & keyword extraction
│   │   └── main.py                # FastAPI entrypoint
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   └── App.vue                # Main UI component
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## Quick Start

1. **Build and run containers**:
   ```bash
   docker compose up --build
   ```

2. **Access services**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

3. **Usage**:
   - Upload a CV (PDF/DOCX)
   - Paste a job description
   - Click "Analyze Match"
   - View similarity score and extracted keywords

## API Endpoint

**POST /api/match**

- **Form data**:
  - `cv`: File (PDF/DOCX)
  - `job_description`: Text string
- **Response**:
  ```json
  {
    "similarity_score": 85.5,
    "insights": {
      "skills": ["python", "docker"],
      "experience": ["3 years experience"],
      "education": ["bachelor degree"]
    }
  }
  ```

## Configuration

Edit `backend/app/core/keywords.json` to customize keyword patterns for skills, experience, and education extraction.

## Development

- Backend changes: Auto-reload enabled in Docker
- Frontend changes: Hot-reload enabled via Vite
