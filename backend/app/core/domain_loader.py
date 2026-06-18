import json
import os
from typing import Dict, List

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")
_available_domains = None
_domain_configs_cache = {}
_master_skills_set = None
_master_skills_list = None


def get_available_domains() -> List[str]:
    global _available_domains
    if _available_domains is None:
        _available_domains = []
        if os.path.exists(SKILLS_DIR):
            for f in os.listdir(SKILLS_DIR):
                if f.endswith(".json"):
                    _available_domains.append(f.replace(".json", ""))
    return _available_domains


def load_domain_config(domain: str = "general") -> Dict:
    domain = domain.lower()
    if domain in _domain_configs_cache:
        return _domain_configs_cache[domain]

    filepath = os.path.join(SKILLS_DIR, f"{domain}.json")
    if not os.path.exists(filepath):
        filepath = os.path.join(SKILLS_DIR, "general.json")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            config = json.load(f)
            _domain_configs_cache[domain] = config
            return config
    except Exception as e:
        print(f"Error loading domain config {domain}: {e}")
        # fallback minimal config
        config = {
            "domain": domain.capitalize(),
            "threshold_direct_match": 0.75,
            "threshold_master_match": 0.77,
            "skills": [],
            "experience_keywords": [],
            "education_keywords": [],
        }
        _domain_configs_cache[domain] = config
        return config


def get_skills_for_domain(domain: str) -> List[str]:
    config = load_domain_config(domain)
    return config.get("skills", [])


def get_master_skills() -> List[str]:
    """Returns a unified, deduplicated list of all skills across all domains."""
    global _master_skills_set, _master_skills_list
    if _master_skills_list is not None:
        return _master_skills_list

    _master_skills_set = set()
    domains = get_available_domains()
    for d in domains:
        skills = get_skills_for_domain(d)
        for s in skills:
            _master_skills_set.add(s)

    _master_skills_list = list(_master_skills_set)
    return _master_skills_list
