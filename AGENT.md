# Project Information

## Tech Stack
- **Backend**: FastAPI, Python 3.10+, sentence-transformers, PyMongo, BeautifulSoup4
- **Frontend**: Vue 3, Vite, Axios
- **Database**: MongoDB (Official Image)
- **Database GUI**: Mongo Express
- **Containerization**: Docker, Docker Compose

## Key Files
- `backend/app/services/linkedin_scraper.py`: Scrapes public LinkedIn job postings into MongoDB
- `backend/app/services/nlp.py`: Similarity scoring and dynamic keyword extraction from MongoDB
- `frontend/src/App.vue`: Main UI component for file upload and results display

## Commands
- `docker compose up --build`: Build and start services
- `docker compose down`: Stop services
- `docker compose exec backend python -m app.services.linkedin_scraper`: Run scraper manually

## API
- `POST /api/match`: Accepts CV file and job description, returns similarity score and insights

## Notes
- Keywords are dynamically fetched from the `cv_matcher.linkedin_jobs` MongoDB collection.
- Mongo Express is available at `http://localhost:8081` (admin/password).
- CORS allows requests from `http://localhost:5173`.
- Model `all-MiniLM-L6-v2` is pre-downloaded in Docker image.
