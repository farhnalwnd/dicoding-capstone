import re
import os
import math
from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import KMeans
from typing import List, Dict, Any, Tuple
import numpy as np

from app.services.explainability import (
    build_match_explanation
)

MODEL_MAIN = os.getenv("MODEL_MAIN", "paraphrase-multilingual-MiniLM-L12-v2")
MODEL_BI_ENCODER = os.getenv("MODEL_BI_ENCODER")

print(f"[NLP] Loading Bi-Encoder from: {MODEL_BI_ENCODER}")
model = SentenceTransformer(MODEL_BI_ENCODER)

_skills_embeddings_cache = {}

def get_skill_embeddings_for_skills(skills: List[str]):
    embeddings = {}
    for skill in skills:
        if skill not in _skills_embeddings_cache:
            _skills_embeddings_cache[skill] = model.encode(skill, convert_to_tensor=True)
        embeddings[skill] = _skills_embeddings_cache[skill]
    return embeddings


def get_similarity_score(text1: str, text2: str) -> float:
    # Murni menggunakan Bi-Encoder (Cosine Similarity)
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    similarity = util.cos_sim(emb1, emb2).item()
    return round(max(0.0, min(1.0, similarity)) * 100, 2)
    
def analyze_cv_jd(
    cv_text: str,
    jd_text: str,
    domain: str
):
    """
    Complete explainable CV-JD analysis
    """
    from app.core.domain_loader import load_domain_config

    similarity_score = get_similarity_score(
        cv_text,
        jd_text
    )

    matched_skills, missing_skills, skill_scores = (
        match_cv_jd_hybrid(
            cv_text=cv_text,
            jd_text=jd_text,
            domain=domain
        )
    )

    # Domain relevance: how many of ALL domain skills appear in the CV
    # This rewards CVs that genuinely belong to the same domain as the JD.
    # An IT CV should score higher against an IT JD than a Finance JD.
    config = load_domain_config(domain)
    all_domain_skills = config.get("skills", [])
    if all_domain_skills:
        cv_domain_hits = sum(
            1 for s in all_domain_skills
            if has_skill_exact(s, cv_text)
        )
        domain_relevance = round(
            (cv_domain_hits / len(all_domain_skills)) * 100, 2
        )
    else:
        domain_relevance = 0.0

    explanation = build_match_explanation(
        similarity_score=similarity_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        domain_relevance=domain_relevance
    )
    explanation["skill_scores"] = skill_scores
    return explanation


def extract_phrases(text: str) -> List[str]:
    from app.services.parser import STOPWORDS
    
    # Tambah kurung () [] dan titik dua : ke split regex agar kalimat terpecah dengan baik
    phrases = re.split(r'[\n,;\t•|.:()\[\]]', text)
    valid_phrases = []
    
    # Stopwords tambahan lokal khusus untuk pemecahan frasa di tengah
    split_conjunctions = {"and", "or", "dan", "atau", "with", "using", "menggunakan", "dengan", "for", "untuk", "in", "di", "on", "pada", "from", "dari", "to", "ke", "by", "as", "including", "termasuk", "such as", "seperti", "maupun", "ataupun", "vs", "versus"}
    
    for p in phrases:
        p = p.strip()
        if not p or len(p) <= 2:
            continue
            
        # Jika frasa mengandung kata hubung tengah, kita pecah frasa tersebut.
        sub_candidates = []
        p_lower = p.lower()
        if any(f" {w} " in f" {p_lower} " for w in split_conjunctions):
            # Lakukan pemecahan
            parts = re.split(r'\b(?:and|or|dan|atau|with|using|menggunakan|dengan|for|untuk|in|di|on|pada|from|dari|to|ke|by|as|including|termasuk|such as|seperti|maupun|ataupun|vs|versus)\b', p, flags=re.IGNORECASE)
            for part in parts:
                part = part.strip()
                if part:
                    sub_candidates.append(part)
        else:
            sub_candidates.append(p)

        for sub_p in sub_candidates:
            sub_words = sub_p.split()
            # Batasi panjang frasa (maksimal 4 kata)
            if len(sub_words) > 4:
                continue
                
            # Periksa apakah semua kata di dalam frasa adalah stopwords
            if all(w.lower() in STOPWORDS for w in sub_words):
                continue
                
            # Bersihkan punctuation di awal/akhir frasa
            p_clean = re.sub(r'^[^\w+#-]+|[^\w+#-]+$', '', sub_p).strip()
            
            # Bersihkan ANY stopword di awal dan akhir frasa secara berulang (rekursif)
            p_words = p_clean.split()
            changed = True
            while changed and p_words:
                changed = False
                if p_words[0].lower() in STOPWORDS:
                    p_words = p_words[1:]
                    changed = True
                if p_words and p_words[-1].lower() in STOPWORDS:
                    p_words = p_words[:-1]
                    changed = True
            
            p_clean = " ".join(p_words).strip()
            
            if len(p_clean) > 2 and not p_clean.lower() in STOPWORDS:
                valid_phrases.append(p_clean)
    
    # Ekstraksi kata tunggal yang sangat mungkin berupa teknologi/spesifik
    words = re.findall(r'\b[a-zA-Z0-9+#.-]{2,20}\b', text)
    for w in words:
        w_lower = w.lower()
        if w_lower not in STOPWORDS:
            # 1. Mengandung karakter teknologi khusus (+, #, ., -) seperti C++, C#, Vue.js, CI/CD
            # 2. ATAU merupakan singkatan dengan huruf kapital penuh (SQL, AWS, GCP, IT)
            is_tech_char = any(c in w for c in '+#.-')
            is_all_caps = w.isupper() and len(w) >= 2
            
            if is_tech_char or is_all_caps:
                # Bersihkan punctuation
                w_clean = re.sub(r'^[^\w+#-]+|[^\w+#-]+$', '', w)
                if len(w_clean) >= 2 and w_clean.lower() not in STOPWORDS:
                    valid_phrases.append(w_clean)
            
    valid_phrases = list(set([p for p in valid_phrases if 2 <= len(p) < 50]))
    return valid_phrases

def normalize_skill_name(name: str) -> str:
    """
    Normalize skill name by converting to lowercase and stripping common suffixes
    like .js, js, framework, library to allow flexible exact matching.
    """
    n = name.lower().strip()
    n = re.sub(r'(?:[\s.-]?js|[\s.-]?j\.s|[\s.-]?j-s)$', '', n)
    n = re.sub(r'(?:[\s.-]?framework|[\s.-]?library)$', '', n)
    return n.strip()

def has_skill_exact(skill: str, text: str) -> bool:
    """
    Check if a skill is present in text as an exact word match (case-insensitive).
    Handles special characters like C++, C#, .NET, etc. safely.
    Also performs soft exact matching for variations like Vue.js vs Vue, ReactJS vs React.
    """
    skill_norm = normalize_skill_name(skill)
    
    # 1. Soft matching by tokenizing and normalizing each token in the text
    tokens = re.findall(r'\b[a-zA-Z0-9+#.-]+\b', text)
    for token in tokens:
        if normalize_skill_name(token) == skill_norm:
            return True
            
    # 2. Fallback to standard exact regex matching (for multi-word skills like "Machine Learning")
    skill_lower = skill.lower().strip()
    text_lower = text.lower()
    escaped = re.escape(skill_lower)
    
    pattern = ""
    if re.match(r'^\w', skill_lower):
        pattern += r'\b'
    pattern += escaped
    if re.search(r'\w$', skill_lower):
        pattern += r'\b'
        
    return bool(re.search(pattern, text_lower))


def clean_skill_phrase(skill: str) -> str:
    # Remove bullet symbols and formatting characters from start and end
    s = re.sub(r'^[-\*•\s]+', '', skill)
    s = re.sub(r'[-\*•\s]+$', '', s)
    return s.strip()

def is_valid_skill(phrase: str, domain_skills: set[str]) -> bool:
    # 6. Bersihkan bullet prefix sebelum validasi
    clean_phrase = re.sub(r'^[-\*•\s]+', '', phrase)
    clean_phrase = re.sub(r'[-\*•\s]+$', '', clean_phrase).strip()
    
    if len(clean_phrase) < 2:
        return False
        
    phrase_lower = clean_phrase.lower()
    
    # 2. Skill yang ada di whitelist domain harus selalu dianggap valid.
    domain_skills_lower = {s.lower() for s in domain_skills} if domain_skills else set()
    if phrase_lower in domain_skills_lower:
        return True
        
    # 3. Blacklist untuk generic words
    GENERIC_WORDS = {
        "key", "interface", "integration", "integrations", "principle", "principles",
        "testable", "building", "designing", "documented", "maintaining", "robust"
    }
    
    # 4. Blacklist role/job title
    ROLE_WORDS = {
        "engineer", "engineers", "developer", "developers", "architect", "architects",
        "manager", "managers", "consultant", "consultants", "analyst", "analysts",
        "officer", "officers"
    }
    
    # 5. Blacklist action verbs
    ACTION_WORDS = {
        "collaborate", "collaborating", "implement", "implementing", "build", "building",
        "maintain", "maintaining", "design", "designing", "develop", "developing",
        "support", "supporting", "integrate", "integrating"
    }
    
    # Standard stopwords
    from app.services.parser import STOPWORDS
    
    words = phrase_lower.split()
    if not words:
        return False
        
    # Check if the whole phrase matches any blacklist
    if phrase_lower in GENERIC_WORDS or phrase_lower in ROLE_WORDS or phrase_lower in ACTION_WORDS:
        return False
        
    # Check if any word is in ROLE_WORDS or GENERIC_WORDS
    if any(w in ROLE_WORDS for w in words):
        return False
        
    if any(w in GENERIC_WORDS for w in words):
        return False
        
    # Check if first word is in ACTION_WORDS
    if words[0] in ACTION_WORDS:
        return False
        
    # If all words in the phrase are stopwords or generic/action/role words
    if all(w in STOPWORDS or w in GENERIC_WORDS or w in ROLE_WORDS or w in ACTION_WORDS for w in words):
        return False
        
    return True

def _get_tokens(s: str) -> List[str]:
    return re.findall(r'[a-zA-Z0-9]+', s.lower())

def _is_sublist(sub: List[str], lst: List[str]) -> bool:
    n, m = len(sub), len(lst)
    for i in range(m - n + 1):
        if lst[i:i+n] == sub:
            return True
    return False

def deduplicate_skills(skills: List[str], domain_skills: List[str] = None) -> List[str]:
    if not skills:
        return []
        
    ds_lower = {s.lower() for s in domain_skills} if domain_skills else set()
    
    to_remove = set()
    n = len(skills)
    
    for i in range(n):
        for j in range(n):
            if i == j or j in to_remove or i in to_remove:
                continue
            s1 = skills[i]
            s2 = skills[j]
            
            t1 = _get_tokens(s1)
            t2 = _get_tokens(s2)
            
            if not t1 or not t2:
                continue
                
            if len(t1) < len(t2) and _is_sublist(t1, t2):
                s1_lower = s1.lower()
                s2_lower = s2.lower()
                
                if s1_lower in ds_lower and s2_lower not in ds_lower:
                    to_remove.add(j)
                elif s2_lower in ds_lower and s1_lower not in ds_lower:
                    to_remove.add(i)
                else:
                    to_remove.add(i)
                    
    return [skills[i] for i in range(n) if i not in to_remove]

def extract_jd_target_skills(jd_text: str, domain: str) -> List[str]:
    """
    Extract exact valid skills from JD text using the Master Skills list.
    This guarantees NO irrelevant skills (like "S1", "mampu bekerja") are extracted.
    """
    from app.core.domain_loader import get_master_skills, load_domain_config
    
    master_skills = get_master_skills()
    config = load_domain_config(domain)
    domain_skills = config.get("skills", [])
    
    target_skills = set()
    
    # Check all master skills if they exist exactly in the JD text
    for skill in master_skills:
        if has_skill_exact(skill, jd_text):
            target_skills.add(skill)
            
    # As a fallback, ensure any domain skills present in JD are included
    for skill in domain_skills:
        if has_skill_exact(skill, jd_text):
            target_skills.add(skill)
            
    # HEAD normalization safety fallback
    NORMALIZATION_MAP = {
        "rest": "REST API",
        "rest api": "REST API",
        "restful api": "REST API",
        "restful apis": "REST API",
        "ci": "CI/CD",
        "ci/cd": "CI/CD",
        "nlp models": "NLP",
        "nlp": "NLP",
        "vue": "Vue.js",
        "vue.js": "Vue.js",
        "react": "React",
        "react.js": "React",
        "reactjs": "React",
        "node": "Node.js",
        "node.js": "Node.js",
        "nodejs": "Node.js"
    }
    for var_name, norm_name in NORMALIZATION_MAP.items():
        if has_skill_exact(var_name, jd_text):
            if norm_name in master_skills or norm_name in domain_skills:
                target_skills.add(norm_name)
            
    return list(target_skills)

def match_cv_jd_hybrid(cv_text: str, jd_text: str, domain: str, precomputed_target_skills: List[str] = None) -> Tuple[List[str], List[str], Dict[str, float]]:
    """
    Hybrid semantic matching using batch encoding for significant performance improvements.
    Uses precomputed target skills to avoid extracting JD phrases for every candidate.
    """
    from app.core.domain_loader import load_domain_config
    
    config = load_domain_config(domain)
    domain_skills = config.get("skills", [])
    domain_skill_set = set(domain_skills)
    threshold_direct = config.get("threshold_direct_match", 0.75)
    threshold_master = config.get("threshold_master_match", 0.82)
    
    # 1. Determine target skills from JD (use precomputed if available)
    if precomputed_target_skills is not None:
        target_skills = precomputed_target_skills
    else:
        target_skills = extract_jd_target_skills(jd_text, domain)
        
    if not target_skills:
        return [], [], {}
        
    # 2. Extract phrases from CV
    cv_phrases = extract_phrases(cv_text)
    
    matched_with_scores = {}
    missing_skills_with_scores = {}
    semantic_check_skills = []
    
    # 3. Exact matching first
    for skill in target_skills:
        if has_skill_exact(skill, cv_text):
            matched_with_scores[skill] = 100.0
        else:
            semantic_check_skills.append(skill)
            
    # 4. Batch Semantic matching for missing skills against CV phrases
    if semantic_check_skills and cv_phrases:
        # Batch encode skills and CV phrases
        skill_embs = model.encode(semantic_check_skills, convert_to_tensor=True)
        cv_phrase_embs = model.encode(cv_phrases, convert_to_tensor=True)
        
        # Calculate cosine similarity for all combinations at once (Batching)
        # similarities shape: (len(semantic_check_skills), len(cv_phrases))
        similarities = util.cos_sim(skill_embs, cv_phrase_embs)
        
        # Get max similarity for each skill
        max_sims = similarities.max(dim=1).values.tolist()
        
        for i, skill in enumerate(semantic_check_skills):
            max_sim = max_sims[i]
            threshold = threshold_master if skill in domain_skills else threshold_direct
            
            if max_sim >= threshold:
                matched_with_scores[skill] = round(max_sim * 100, 2)
            else:
                missing_skills_with_scores[skill] = round(max_sim * 100, 2)
    else:
        # If no cv phrases extracted, all remaining skills are missing with 0 score
        for skill in semantic_check_skills:
            missing_skills_with_scores[skill] = 0.0
            
    # Sort matched_skills by score descending, exact matches (100.0) first
    matched_skills = sorted(matched_with_scores.keys(), key=lambda k: matched_with_scores[k], reverse=True)
    
    # Sort missing_skills by score descending (closest missing skills shown first)
    missing_skills = sorted(missing_skills_with_scores.keys(), key=lambda k: missing_skills_with_scores[k], reverse=True)
    
    # Apply deduplication
    matched_skills = deduplicate_skills(matched_skills, domain_skills)
    missing_skills = deduplicate_skills(missing_skills, domain_skills)
    
    # Limit output length
    matched_skills = matched_skills[:15]
    missing_skills = missing_skills[:15]
    
    # Combine scores for radar chart or analysis
    skill_scores = {**matched_with_scores, **missing_skills_with_scores}
    
    return matched_skills, missing_skills, skill_scores


def cluster_documents(texts: List[str], filenames: List[str], num_clusters: int = 3) -> List[Dict[str, Any]]:
    if not texts:
        return []
    if len(texts) < num_clusters:
        num_clusters = len(texts)
        
    embeddings = model.encode(texts)
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    kmeans.fit(embeddings)
    
    labels = kmeans.labels_
    
    clusters = {i: [] for i in range(num_clusters)}
    for idx, label in enumerate(labels):
        clusters[label].append({
            "filename": filenames[idx],
            "text": texts[idx]
        })
        
    result = []
    for cluster_id, items in clusters.items():
        combined_text = " ".join([item["text"] for item in items])
        cluster_phrases = extract_phrases(combined_text)
        
        if cluster_phrases:
            phrase_embs = model.encode(cluster_phrases[:50], convert_to_tensor=True)
            cluster_skills = []
            
            for skill_name, skill_emb in get_skill_embeddings_for_skills(domain_skills if 'domain_skills' in locals() else []).items():
                similarities = util.cos_sim(skill_emb, phrase_embs)[0]
                max_sim = similarities.max().item()
                if max_sim > 0.82:
                    cluster_skills.append(skill_name)
            
            suggested_label = " / ".join(cluster_skills[:3]) if cluster_skills else f"Cluster {cluster_id + 1}"
        else:
            suggested_label = f"Cluster {cluster_id + 1}"
        
        result.append({
            "cluster_id": cluster_id,
            "suggested_label": suggested_label,
            "candidates": [item["filename"] for item in items]
        })
        
    return result

