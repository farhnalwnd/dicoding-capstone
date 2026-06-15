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

    similarity_score = get_similarity_score(
        cv_text,
        jd_text
    )

    matched_skills, missing_skills = (
        match_cv_jd_hybrid(
            cv_text=cv_text,
            jd_text=jd_text,
            domain=domain
        )
    )

    return build_match_explanation(
        similarity_score=similarity_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills
    )

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


def match_cv_jd_hybrid(cv_text: str, jd_text: str, domain: str) -> Tuple[List[str], List[str]]:
    """
    Hybrid semantic matching:
    - Target list of skills: Union of phrases extracted from JD and domain skills present in JD.
    - Check match against CV using soft exact matching first, with semantic matching as fallback.
    """
    from app.core.domain_loader import load_domain_config
    
    config = load_domain_config(domain)
    domain_skills = config.get("skills", [])
    threshold_direct = config.get("threshold_direct_match", 0.75)
    threshold_master = config.get("threshold_master_match", 0.82)
    
    # Extract phrases from JD and CV
    jd_phrases = extract_phrases(jd_text)
    cv_phrases = extract_phrases(cv_text)
    
    # Target skills/phrases to match (all required by JD)
    # Kita hanya masukkan jd_phrases jika dia lolos filter stopwords ATAU mirip/merupakan bagian dari domain_skills
    target_skills = set()
    
    # Pre-encode domain skills if available to match with extracted jd_phrases
    domain_embeddings = None
    if domain_skills and jd_phrases:
        try:
            domain_embeddings = model.encode(domain_skills, convert_to_tensor=True)
        except Exception:
            pass
            
    for phrase in jd_phrases:
        # Jika frasa ada langsung di domain skills, masukkan
        if phrase in domain_skills:
            target_skills.add(phrase)
            continue
            
        # Jika frasa mirip dengan salah satu domain skills, kita anggap itu valid skill
        if domain_embeddings is not None:
            try:
                phrase_emb = model.encode(phrase, convert_to_tensor=True)
                similarities = util.cos_sim(phrase_emb, domain_embeddings)[0]
                if similarities.max().item() >= 0.75:
                    target_skills.add(phrase)
                    continue
            except Exception:
                pass
                
        # Jika panjang kata <= 2 dan lolos stopword, boleh masuk sebagai fallback (contoh: 'SQL', 'Git')
        if len(phrase.split()) <= 2:
            target_skills.add(phrase)
            
    # Selalu masukkan skill dari domain config yang tertulis jelas (exact match) di dalam JD
    for skill in domain_skills:
        if has_skill_exact(skill, jd_text):
            target_skills.add(skill)
            
    if not target_skills:
        return [], []
        
    matched_with_scores = {}
    missing_skills_with_scores = {}
    
    # Pre-encode CV phrases if available for semantic fallback
    cv_phrase_embeddings = None
    if cv_phrases:
        cv_phrase_embeddings = model.encode(cv_phrases, convert_to_tensor=True)
        
    for skill in target_skills:
        # 1. Soft Exact Match check in CV
        if has_skill_exact(skill, cv_text):
            matched_with_scores[skill] = 100.0
            continue
            
        # 2. Semantic Fallback check
        threshold = threshold_master if skill in domain_skills else threshold_direct
        
        if cv_phrase_embeddings is not None and cv_phrases:
            skill_emb = model.encode(skill, convert_to_tensor=True)
            similarities = util.cos_sim(skill_emb, cv_phrase_embeddings)[0]
            max_sim = similarities.max().item()
            
            if max_sim >= threshold:
                matched_with_scores[skill] = round(max_sim * 100, 2)
            else:
                missing_skills_with_scores[skill] = round(max_sim * 100, 2)
        else:
            missing_skills_with_scores[skill] = 0.0
            
    # Sort matched_skills by score descending, exact matches (100.0) first
    matched_skills = sorted(matched_with_scores.keys(), key=lambda k: matched_with_scores[k], reverse=True)[:15]
    
    # Sort missing_skills by score descending (closest missing skills shown first)
    missing_skills = sorted(missing_skills_with_scores.keys(), key=lambda k: missing_skills_with_scores[k], reverse=True)[:15]
    
    return matched_skills, missing_skills

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

