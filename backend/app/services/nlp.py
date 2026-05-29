import re
import os
from sentence_transformers import SentenceTransformer, util
from pymongo import MongoClient

# Load model once on startup
model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.cv_matcher
jobs_collection = db.linkedin_jobs

def get_similarity_score(text1: str, text2: str) -> float:
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    similarity = util.cos_sim(emb1, emb2).item()
    return round(max(0.0, min(1.0, similarity)) * 100, 2)

def get_dynamic_keywords():
    # Fetch job titles and companies from MongoDB to use as dynamic keywords
    jobs = list(jobs_collection.find({}, {"title": 1, "company": 1, "_id": 0}))
    
    dynamic_skills = set()
    for job in jobs:
        # Simple extraction for demo: split titles into words
        words = job.get("title", "").lower().replace("-", " ").split()
        for w in words:
            if len(w) > 2:
                dynamic_skills.add(w)
                
    # Fallback default skills if DB is empty
    if not dynamic_skills:
        dynamic_skills = {"python", "javascript", "vue", "react", "fastapi", "docker", "sql"}
        
    return list(dynamic_skills)

def extract_keywords(text: str):
    # Dynamic skills from DB
    skills_list = get_dynamic_keywords()
    skills_patterns = [re.compile(r"\b(" + "|".join(re.escape(s) for s in skills_list) + r")\b")]
    
    # Static patterns for exp/edu (could also be moved to DB if needed)
    experience_patterns = [
        re.compile(r"\b(\d+\+?\s*(years?|yrs?)\s*(of\s*)?experience)\b"),
        re.compile(r"\b(experience\b.*?years?)\b"),
        re.compile(r"\b(worked\s*as|developer|engineer|manager|analyst|intern|lead|senior|junior|staff)\b")
    ]
    education_patterns = [
        re.compile(r"\b(bachelor|master|phd|degree|university|college|diploma|computer science|engineering|science)\b")
    ]

    skills = set()
    experience = set()
    education = set()

    text_lower = text.lower()
    for pat in skills_patterns:
        for match in pat.finditer(text_lower):
            skills.add(match.group(0))

    for pat in experience_patterns:
        for match in pat.finditer(text_lower):
            experience.add(match.group(0))

    for pat in education_patterns:
        for match in pat.finditer(text_lower):
            education.add(match.group(0))

    return {
        "skills": list(skills),
        "experience": list(experience),
        "education": list(education)
    }
