import re
import json
import os
from sentence_transformers import SentenceTransformer, util

# Load model once on startup
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load keywords configuration
KEYWORDS_FILE = os.path.join(os.path.dirname(__file__), "../core/keywords.json")
with open(KEYWORDS_FILE, "r") as f:
    KEYWORDS = json.load(f)

def get_similarity_score(text1: str, text2: str) -> float:
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    similarity = util.cos_sim(emb1, emb2).item()
    return round(max(0.0, min(1.0, similarity)) * 100, 2)

def extract_keywords(text: str):
    skills_patterns = [re.compile(r"\b(" + "|".join(re.escape(s) for s in KEYWORDS["skills"]) + r")\b")]
    experience_patterns = [re.compile(p) for p in KEYWORDS["experience_patterns"]]
    education_patterns = [re.compile(p) for p in KEYWORDS["education_patterns"]]

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
