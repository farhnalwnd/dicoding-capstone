import json
import os

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")
_available_domains = None

def get_available_domains():
    global _available_domains
    if _available_domains is None:
        _available_domains = []
        if os.path.exists(SKILLS_DIR):
            for f in os.listdir(SKILLS_DIR):
                if f.endswith(".json"):
                    _available_domains.append(f.replace(".json", ""))
    return _available_domains

def load_domain_config(domain: str = "general"):
    filepath = os.path.join(SKILLS_DIR, f"{domain}.json")
    if not os.path.exists(filepath):
        filepath = os.path.join(SKILLS_DIR, "general.json")
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading domain config {domain}: {e}")
        # fallback minimal config
        return {
            "domain": domain.capitalize(),
            "threshold_direct_match": 0.75,
            "threshold_master_match": 0.77,
            "skills": [],
            "experience_keywords": [],
            "education_keywords": []
        }

def get_skills_for_domain(domain: str):
    config = load_domain_config(domain)
    return config.get("skills", [])
