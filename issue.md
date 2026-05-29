# System Issue: CV Summarizer & Job Matching System Upgrades

This document outlines three new features to be implemented by Junior Data & NLP Developers. The system uses a FastAPI backend, Vue 3 frontend, and a MongoDB database.

---

## 1. Feature 1: Scrape & Job Recommendation (Job Seeker)

### Objective
Allow users to trigger a LinkedIn scraping job from the frontend, specify the job age limit, upload their CV, and receive the top 5 matching jobs from the database with their URLs.

### Requirements
- **Frontend UI**:
  - Time range dropdown options: `1 Week`, `1 Month`, `2 Months`, `3 Months`.
  - Button: "Scrape & Find Matches".
  - CV file upload field (PDF/DOCX).
- **Backend API (`POST /api/scrape-recommend`)**:
  - **Inputs**: `cv` (UploadFile), `time_range` (Form field: `1w`, `1m`, `2m`, `3m`), `keyword` (Form field, default "Python Developer"), `location` (Form field, default "Jakarta").
  - **Pipeline**:
    1. Scrape latest job posts from LinkedIn based on keyword, location, and the selected time range filter.
    2. Save new jobs to MongoDB (preventing duplicates using `upsert`).
    3. Extract text from the uploaded CV.
    4. Compute embeddings for the CV text and all jobs matching the keyword/location in MongoDB.
    5. Calculate similarity scores between the CV and each job description.
    6. Return the **Top 5 jobs** sorted by highest match score, including Job Title, Company, URL, and Match Percentage.

---

## 2. Feature 2: Detailed CV-JD Analysis with Missing Skills (Job Seeker)

### Objective
Enhance the existing single-matching output to show not just a score, but specifically what requirements are met and what requirements are missing.

### Requirements
- **Frontend UI**:
  - Drag-and-drop CV upload + Job Description textarea.
  - Interactive output section displaying:
    - Overall match percentage.
    - Met Skills & Requirements list.
    - Missing Skills & Requirements list.
- **Backend API (`POST /api/match-detailed`)**:
  - **Inputs**: `cv` (UploadFile), `job_description` (Form field).
  - **Pipeline**:
    1. Extract text from CV.
    2. Run NLP keyword/skill extraction on both CV text and Job Description.
    3. Compare the two skill sets:
       - **Matched Skills**: Intersection of CV skills and Job Description skills.
       - **Missing Skills**: Skills present in Job Description but missing in CV.
    4. Return JSON response:
       ```json
       {
         "similarity_score": 78.5,
         "matched_skills": ["python", "fastapi", "docker"],
         "missing_skills": ["kubernetes", "tensorflow"]
       }
       ```

---

## 3. Feature 3: Bulk CV Ranking Dashboard (HR Feature)

### Objective
Allow HR personnel to upload multiple CVs at once, input a single Job Description, and get a ranked list of candidates based on their suitability.

### Requirements
- **Frontend UI**:
  - Multiple file upload field (accepts multiple PDF/DOCX files).
  - Job Description textarea.
  - Table displaying ranked results: `Rank`, `Candidate Name`, `Match Percentage`.
- **Backend API (`POST /api/hr/rank`)**:
  - **Inputs**: `cvs` (List of UploadFile), `job_description` (Form field).
  - **Pipeline**:
    1. Loop through each uploaded CV.
    2. Extract text and compute similarity score against the Job Description.
    3. Extract the Candidate's Name (either from CV content using a simple regex/NLP name extractor, or fallback to the file name without extension).
    4. Sort the candidates in descending order of similarity score.
    5. Return JSON list:
       ```json
       [
         { "rank": 1, "name": "John Doe", "score": 92.4 },
         { "rank": 2, "name": "Alice Smith", "score": 85.1 }
       ]
       ```

---

## Definition of Done (DoD)
- All 3 API endpoints functional and tested.
- MongoDB integration used for storing and retrieving scraped jobs.
- UI elements reactively display data returned by backend.
