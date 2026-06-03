# CV Summarizer & Job Matching System

A web-based application for CV Summarization, Job Matching, and Talent Analytics using Natural Language Processing (NLP).

## Features

- **Job Seeker Portal**:
  - **Scrape Jobs**: Pull real-time jobs from LinkedIn using keywords and locations.
  - **CV-JD Analysis**: Detailed analysis using hybrid semantic matching (80% CV-JD direct match + 20% Master Skills) to find similarity scores, matched skills, and missing skills.
  - **Semantic Search**: Upload CV and search for the most relevant jobs stored in MongoDB using vector embeddings.
- **HR Panel**:
  - **Bulk CV Ranking**: Upload multiple CVs to rank candidates against a target job description.
  - **Talent Clustering**: Group candidates into dynamically labeled clusters using K-Means clustering of CV embeddings.

## Architecture

- **Backend**: FastAPI (Python 3.10+)
- **Frontend**: Vue.js (Vue 3 with Vite & Vue Router)
- **Database**: MongoDB (Storage for scraped jobs and embeddings)
- **Database GUI**: Mongo Express
- **NLP Engine**: `sentence-transformers` (configurable, default: `paraphrase-multilingual-MiniLM-L12-v2`)
- **Containerization**: Docker & Docker Compose

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints.py       # Core APIs (scrape, match, search)
│   │   │   ├── hr_endpoints.py    # HR APIs (rank, cluster)
│   │   │   └── jobs_endpoints.py  # Jobs operations
│   │   ├── core/
│   │   │   ├── domain_loader.py   # Dynamic domain config loader
│   │   │   ├── mongodb.py         # MongoDB connection helper
│   │   │   └── skills/            # Domain-specific JSON configs
│   │   │       ├── it.json
│   │   │       ├── hr.json
│   │   │       ├── finance.json
│   │   │       ├── creative.json
│   │   │       ├── sales.json
│   │   │       ├── legal.json
│   │   │       ├── pr.json
│   │   │       ├── ga.json
│   │   │       ├── cs.json
│   │   │       ├── operational.json
│   │   │       └── general.json
│   │   ├── services/
│   │   │   ├── linkedin_scraper.py# BeautifulSoup job scraper
│   │   │   ├── nlp.py             # NLP match, search, clustering logic
│   │   │   └── parser.py          # PDF/DOCX parsing & cleaning logic
│   │   └── main.py                # FastAPI app entrypoint
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/            # Reusable UI components
│   │   ├── views/                 # View pages (Analyze, Cluster, Scrape, etc.)
│   │   ├── router/                # Vue Router configuration
│   │   ├── App.vue                # Root App component
│   │   └── main.js                # App entrypoint
│   ├── Dockerfile
│   └── package.json
├── training/
│   ├── scripts/
│   │   ├── generate_dataset.py    # Synthetic data generator
│   │   ├── train_bi_encoder.py    # Bi-Encoder training script
│   │   └── train_cross_encoder.py # Cross-Encoder training script
│   ├── templates/
│   │   ├── anchor_templates.json  # Job description templates
│   │   ├── positive_templates.json# Matching CV templates
│   │   └── negative_templates.json# Non-matching CV templates
│   └── notebooks/
│       └── finetuning-model.ipynb # Training orchestrator
├── data/
│   └── training/                  # Generated CSV datasets
├── models/                        # Fine-tuned model outputs
├── .env.example                   # Env template
└── docker-compose.yml             # Orchestration file
```

## Installation & Setup

Follow these steps to run the project on a new device:

### Prerequisites

Make sure you have the following installed on your machine:
- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: [Install Docker Compose](https://docs.docker.com/compose/install/)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd caps-final
```

### Step 2: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and configure your credentials and preference:
   ```env
   MONGO_ROOT_USER=admin
   MONGO_ROOT_PASSWORD=password
   MONGO_EXPRESS_USER=admin
   MONGO_EXPRESS_PASSWORD=password
   MODEL_MAIN=paraphrase-multilingual-MiniLM-L12-v2
   ```

### Step 3: Start the Application

Build and run all services in the background using Docker Compose:

```bash
docker compose up --build
```

*(Note: The first run might take a few minutes as it downloads the model cache and builds images.)*

## Service Access URLs

Once Docker Compose is running, access the services using the following URLs:

- **Frontend Interface**: http://localhost:5173
- **Backend API Docs (Swagger)**: http://localhost:8000/docs
- **Mongo Express (Database Web UI)**: http://localhost:8081

## API Documentation

### Core Endpoints

- **POST `/api/scrape-recommend`**: Trigger scraping LinkedIn jobs and saving them in MongoDB.
- **POST `/api/match-detailed`**: Direct semantic match of CV and Job Description.
- **POST `/api/jobs/semantic-search`**: Compare uploaded CV against all scraped jobs using vector similarity.
- **POST `/api/hr/rank`**: Rank bulk CV uploads against a job description.
- **POST `/api/hr/cluster`**: Perform cluster analysis on candidate CVs.
- **GET `/api/jobs`**: Fetch jobs stored in MongoDB.
- **DELETE `/api/jobs/clear`**: Clear all jobs from MongoDB.

---

## Dataset & Customization

### Training Dataset

The project uses synthetic training data generated from domain-specific templates and skill configurations. Datasets are stored in `data/training/` as CSV files.

**File Structure:**
```
data/training/
├── bi_encoder_train.csv      # Triplet data (anchor, positive, negative)
├── cross_encoder_train.csv   # Pairs data (cv_text, jd_text, label)
└── README.md                 # Dataset format documentation
```

### Domain Configurations

Each domain has its own JSON configuration file in `backend/app/core/skills/`. These files define skills, roles, thresholds, and other domain-specific data.

**Available Domains:**
| File | Domain | Threshold (Direct) | Threshold (Master) |
|------|--------|-------------------|-------------------|
| `it.json` | IT | 0.80 | 0.82 |
| `hr.json` | HR | 0.75 | 0.77 |
| `finance.json` | Finance | 0.75 | 0.77 |
| `creative.json` | Creative & Marketing | 0.70 | 0.72 |
| `sales.json` | Sales & Business Development | 0.70 | 0.72 |
| `legal.json` | Legal | 0.78 | 0.80 |
| `pr.json` | PR & Corcom | 0.72 | 0.74 |
| `ga.json` | GA | 0.70 | 0.72 |
| `cs.json` | CS & Aftersales | 0.70 | 0.72 |
| `operational.json` | Operational | 0.73 | 0.75 |
| `general.json` | General (Default) | 0.75 | 0.77 |

### Customizing Domain Skills

To add or modify skills for a specific domain, edit the corresponding JSON file in `backend/app/core/skills/`.

**Example: Adding a skill to `it.json`:**

```json
{
  "domain": "IT",
  "skills": [
    "Python", "JavaScript", "Docker", "Kubernetes",
    "Rust", "Go", "Terraform"
  ],
  "roles": [
    "Backend Engineer", "DevOps Engineer", "Site Reliability Engineer"
  ],
  "projects": [
    "REST API development", "CI/CD pipeline setup"
  ]
}
```

**Available Fields per Domain:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `skills` | `string[]` | Core competencies for the domain | `["Python", "Docker", "SQL"]` |
| `roles` | `string[]` | Job titles specific to the domain | `["Backend Engineer", "DevOps"]` |
| `teams` | `string[]` | Department/team names | `["Engineering", "Data Science"]` |
| `projects` | `string[]` | Domain-specific project types | `["API development", "migration"]` |
| `unrelated_industries` | `string[]` | Industries unrelated to domain | `["Farming", "Mining"]` |
| `unrelated_roles` | `string[]` | Roles from other domains | `["Graphic Designer", "Accountant"]` |
| `unrelated_tools` | `string[]` | Tools not used in this domain | `["Photoshop", "AutoCAD"]` |
| `experience_keywords` | `string[]` | Phrases indicating experience | `["years of experience"]` |
| `education_keywords` | `string[]` | Education-related terms | `["bachelor", "computer science"]` |
| `threshold_direct_match` | `float` | Similarity threshold for direct matching | `0.80` |
| `threshold_master_match` | `float` | Similarity threshold for master skill matching | `0.82` |

### Customizing Templates

Templates control how synthetic training data is generated. They are located in `training/templates/`.

**Template Files:**
| File | Purpose | Example |
|------|---------|---------|
| `anchor_templates.json` | Job description templates | `"Dibutuhkan {role} yang menguasai {skill}"` |
| `positive_templates.json` | Matching CV templates | `"Pengalaman {years} tahun menggunakan {skill}"` |
| `negative_templates.json` | Non-matching CV templates | `"Keahlian {skill_unrelated} untuk {role_unrelated}"` |

**Available Placeholders:**

| Placeholder | Source | Description |
|-------------|--------|-------------|
| `{skill}` | Domain `skills` array | Random skill from current domain |
| `{skill1}`, `{skill2}` | Domain `skills` array | Multiple skills |
| `{role}` | Domain `roles` array | Random role from current domain |
| `{years}` | Global | Random experience years |
| `{company}` | Global | Random company name |
| `{project}` | Domain `projects` array | Domain-specific project |
| `{skill_unrelated}` | Other domain's `skills` | Skill from different domain |
| `{role_unrelated}` | Domain `unrelated_roles` | Unrelated role |
| `{industry_unrelated}` | Domain `unrelated_industries` | Unrelated industry |
| `{tool_unrelated}` | Domain `unrelated_tools` | Unrelated tool |

**Example: Adding a template to `it.json`:**

```json
{
  "it": [
    "Dibutuhkan {role} yang menguasai {skill}",
    "We are looking for a {role} skilled in {skill}",
    "Minimal {years} tahun pengalaman di {skill} dan {skill2}",
    "Hiring {role} for {team} team - expert in {skill}"
  ]
}
```

### Generating Datasets

After customizing domains and templates, regenerate the training dataset:

```bash
# Generate 2000 triplets and 2000 pairs
python training/scripts/generate_dataset.py \
  --num_triplets 2000 \
  --num_pairs 2000
```

Or use the Jupyter notebook:
```bash
jupyter notebook training/notebooks/finetuning-model.ipynb
```
