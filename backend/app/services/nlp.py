import re
import os
from sentence_transformers import SentenceTransformer, util, CrossEncoder
from sklearn.cluster import KMeans
from typing import List, Dict, Any, Tuple
import numpy as np

MODEL_MAIN = os.getenv("MODEL_MAIN", "paraphrase-multilingual-MiniLM-L12-v2")
MODEL_BI_ENCODER = os.getenv("MODEL_BI_ENCODER")
MODEL_CROSS_ENCODER = os.getenv("MODEL_CROSS_ENCODER")

print(f"[NLP] Loading Bi-Encoder from: {MODEL_BI_ENCODER}")
model = SentenceTransformer(MODEL_BI_ENCODER)

cross_encoder = None
if MODEL_CROSS_ENCODER:
    try:
        print(f"[NLP] Loading Cross-Encoder from: {MODEL_CROSS_ENCODER}")
        cross_encoder = CrossEncoder(MODEL_CROSS_ENCODER)
    except Exception as e:
        print(f"[NLP] Warning: Could not load Cross-Encoder: {e}")

_skills_embeddings_cache = {}

def get_skill_embeddings_for_skills(skills: List[str]):
    embeddings = {}
    for skill in skills:
        if skill not in _skills_embeddings_cache:
            _skills_embeddings_cache[skill] = model.encode(skill, convert_to_tensor=True)
        embeddings[skill] = _skills_embeddings_cache[skill]
    return embeddings


def get_similarity_score(text1: str, text2: str) -> float:
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    similarity = util.cos_sim(emb1, emb2).item()
    return round(max(0.0, min(1.0, similarity)) * 100, 2)

def extract_phrases(text: str) -> List[str]:
    from app.services.parser import STOPWORDS
    
    phrases = re.split(r'[\n,;\t•|]', text)
    valid_phrases = []
    
    for p in phrases:
        p = p.strip()
        if not p or len(p) <= 3:
            continue
            
        words = p.lower().split()
        if all(w in STOPWORDS for w in words):
            continue
            
        valid_phrases.append(p)
    
    words = re.findall(r'\b[a-zA-Z0-9+#.-]{3,20}\b', text)
    for w in words:
        if w.lower() not in STOPWORDS:
            if w[0].isupper() or any(c in w for c in '+#.'):
                valid_phrases.append(w)
            
    valid_phrases = list(set([p for p in valid_phrases if 3 < len(p) < 100]))
    return valid_phrases

def rerank_with_cross_encoder(cv_text: str, candidates: List[Dict]) -> List[Dict]:
    """Re-rank candidates using Cross-Encoder for higher precision"""
    if not cross_encoder or not candidates:
        return candidates
    
    try:
        pairs = [[cv_text, candidate.get('job_description', candidate.get('description', ''))] 
                 for candidate in candidates]
        scores = cross_encoder.predict(pairs)
        
        for i, candidate in enumerate(candidates):
            candidate['cross_encoder_score'] = round(float(scores[i][0]) * 100, 2)
        
        return sorted(candidates, key=lambda x: x['cross_encoder_score'], reverse=True)
    except Exception as e:
        print(f"[NLP] Cross-Encoder re-ranking failed: {e}")
        return candidates

def match_cv_jd_hybrid(cv_text: str, jd_text: str, domain: str) -> Tuple[List[str], List[str]]:
    """
    Hybrid semantic matching with 2 stages:
    - Stage 1 (80%): Direct CV phrases vs JD phrases comparison
    - Stage 2 (20%): CV phrases vs Master Skills comparison
    """
    from app.core.domain_loader import load_domain_config
    
    config = load_domain_config(domain)
    domain_skills = config.get("skills", [])
    threshold_direct = config.get("threshold_direct_match", 0.75)
    threshold_master = config.get("threshold_master_match", 0.82)
    
    cv_phrases = extract_phrases(cv_text)
    jd_phrases = extract_phrases(jd_text)
    
    if not cv_phrases or not jd_phrases:
        return [], []
    
    cv_embeddings = model.encode(cv_phrases, convert_to_tensor=True)
    jd_embeddings = model.encode(jd_phrases, convert_to_tensor=True)
    
    matched_from_jd = {}
    missing_from_jd = {}
    
    for jd_idx, jd_phrase in enumerate(jd_phrases):
        jd_emb = jd_embeddings[jd_idx]
        similarities = util.cos_sim(jd_emb, cv_embeddings)[0]
        max_sim = similarities.max().item()
        
        if max_sim > threshold_direct:
            matched_from_jd[jd_phrase] = max_sim * 0.8
        else:
            missing_from_jd[jd_phrase] = max_sim * 0.8
    
    matched_from_master = {}
    domain_skill_embeddings = get_skill_embeddings_for_skills(domain_skills)
    
    for skill_name, skill_emb in domain_skill_embeddings.items():
        cv_similarities = util.cos_sim(skill_emb, cv_embeddings)[0]
        cv_max_sim = cv_similarities.max().item()
        
        jd_similarities = util.cos_sim(skill_emb, jd_embeddings)[0]
        jd_max_sim = jd_similarities.max().item()
        
        if cv_max_sim > threshold_master and jd_max_sim > threshold_master:
            matched_from_master[skill_name] = min(cv_max_sim, jd_max_sim) * 0.2
        elif jd_max_sim > threshold_master and cv_max_sim <= threshold_master:
            missing_from_jd[skill_name] = jd_max_sim * 0.2
    
    all_matched = {**matched_from_jd, **matched_from_master}
    
    matched_skills = sorted(all_matched.keys(), key=lambda k: all_matched[k], reverse=True)[:15]
    missing_skills = sorted(missing_from_jd.keys(), key=lambda k: missing_from_jd[k], reverse=True)[:15]
    
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

