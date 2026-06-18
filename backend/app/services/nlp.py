import os
import re
from typing import Any, Dict, List, Tuple

from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import KMeans

from app.services.explainability import build_match_explanation

MODEL_MAIN = os.getenv("MODEL_MAIN", "paraphrase-multilingual-MiniLM-L12-v2")
MODEL_BI_ENCODER = os.getenv(
    "MODEL_BI_ENCODER", "paraphrase-multilingual-MiniLM-L12-v2"
)

# Fallback: if local model path doesn't exist, use base HuggingFace model
if (
    MODEL_BI_ENCODER
    and not os.path.exists(MODEL_BI_ENCODER)
    and "/" in MODEL_BI_ENCODER
    and not MODEL_BI_ENCODER.startswith("sentence-transformers")
):  # noqa: E501
    print(f"[NLP] Fine-tuned model not found at: {MODEL_BI_ENCODER}")
    print(f"[NLP] Falling back to: {MODEL_MAIN}")
    MODEL_BI_ENCODER = MODEL_MAIN
else:
    print(f"[NLP] Loading Bi-Encoder from: {MODEL_BI_ENCODER}")

model = SentenceTransformer(MODEL_BI_ENCODER)

MAX_SCORE_PERCENTAGE = 100.0
MIN_PHRASE_LENGTH = 2
MAX_PHRASE_WORDS = 4
MAX_PHRASE_CHAR_LENGTH = 50
MAX_OUTPUT_SKILLS = 15
CLUSTER_SIMILARITY_THRESHOLD = 0.82
CLUSTER_MAX_PHRASES = 50
DEFAULT_THRESHOLD_DIRECT = 0.75
DEFAULT_THRESHOLD_MASTER = 0.82

_SPLIT_CONJUNCTIONS = {
    "and",
    "or",
    "dan",
    "atau",
    "with",
    "using",
    "menggunakan",
    "dengan",
    "for",
    "untuk",
    "in",
    "di",
    "on",
    "pada",
    "from",
    "dari",
    "to",
    "ke",
    "by",
    "as",
    "including",
    "termasuk",
    "such as",
    "seperti",
    "maupun",
    "ataupun",
    "vs",
    "versus",
}

_CONJUNCTION_SPLIT_PATTERN = re.compile(
    r"\b(?:and|or|dan|atau|with|using|menggunakan|dengan|for|untuk"
    r"|in|di|on|pada|from|dari|to|ke|by|as|including|termasuk"
    r"|such as|seperti|maupun|ataupun|vs|versus)\b",
    re.IGNORECASE,
)

_PHRASE_SPLIT_PATTERN = re.compile(r"[\n,;\t•|.:()\[\]]")
_PUNCTUATION_STRIP_PATTERN = re.compile(r"^[^\w+#-]+|[^\w+#-]+$")
_TECH_TOKEN_PATTERN = re.compile(r"\b[a-zA-Z0-9+#.-]{2,20}\b")

_GENERIC_WORDS = frozenset(
    {
        "key",
        "interface",
        "integration",
        "integrations",
        "principle",
        "principles",
        "testable",
        "building",
        "designing",
        "documented",
        "maintaining",
        "robust",
    }
)

_ROLE_WORDS = frozenset(
    {
        "engineer",
        "engineers",
        "developer",
        "developers",
        "architect",
        "architects",
        "manager",
        "managers",
        "consultant",
        "consultants",
        "analyst",
        "analysts",
        "officer",
        "officers",
    }
)

_ACTION_WORDS = frozenset(
    {
        "collaborate",
        "collaborating",
        "implement",
        "implementing",
        "build",
        "building",
        "maintain",
        "maintaining",
        "design",
        "designing",
        "develop",
        "developing",
        "support",
        "supporting",
        "integrate",
        "integrating",
    }
)

_skills_embeddings_cache: Dict[str, Any] = {}


def get_skill_embeddings_for_skills(skills: List[str]):
    embeddings = {}
    for skill in skills:
        if skill not in _skills_embeddings_cache:
            _skills_embeddings_cache[skill] = model.encode(
                skill, convert_to_tensor=True
            )
        embeddings[skill] = _skills_embeddings_cache[skill]
    return embeddings


def get_similarity_score(text1: str, text2: str) -> float:
    from app.core.metrics import MODEL_INFERENCE_LATENCY

    with MODEL_INFERENCE_LATENCY.time():
        emb1 = model.encode(text1, convert_to_tensor=True)
        emb2 = model.encode(text2, convert_to_tensor=True)

    similarity = util.cos_sim(emb1, emb2).item()
    return round(max(0.0, min(1.0, similarity)) * MAX_SCORE_PERCENTAGE, 2)


def _compute_domain_relevance(cv_text: str, domain_skills: List[str]) -> float:
    """Compute what fraction of the domain's skill list appears in the CV."""
    if not domain_skills:
        return 0.0
    cv_domain_hits = sum(1 for s in domain_skills if has_skill_exact(s, cv_text))
    return round((cv_domain_hits / len(domain_skills)) * MAX_SCORE_PERCENTAGE, 2)


def analyze_cv_jd(cv_text: str, jd_text: str, domain: str):
    """
    Complete explainable CV-JD analysis
    """
    from app.core.domain_loader import load_domain_config
    from app.core.metrics import DOMAIN_CLASSIFICATION_COUNT

    DOMAIN_CLASSIFICATION_COUNT.labels(domain=domain).inc()

    similarity_score = get_similarity_score(cv_text, jd_text)

    matched_skills, missing_skills, skill_scores = match_cv_jd_hybrid(
        cv_text=cv_text,
        jd_text=jd_text,
        domain=domain,
    )

    config = load_domain_config(domain)
    domain_relevance = _compute_domain_relevance(
        cv_text,
        config.get("skills", []),
    )

    explanation = build_match_explanation(
        similarity_score=similarity_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        domain_relevance=domain_relevance,
    )
    explanation["skill_scores"] = skill_scores
    return explanation


def _split_on_conjunctions(phrase: str) -> List[str]:
    """Split a phrase on conjunction words, returning non-empty parts."""
    p_lower = phrase.lower()
    if any(f" {w} " in f" {p_lower} " for w in _SPLIT_CONJUNCTIONS):
        return [
            part.strip()
            for part in _CONJUNCTION_SPLIT_PATTERN.split(phrase)
            if part.strip()
        ]
    return [phrase]


def _strip_edge_stopwords(words: List[str], stopwords: set) -> List[str]:
    """Iteratively strip stopwords from the beginning and end of a word list."""
    changed = True
    while changed and words:
        changed = False
        if words[0].lower() in stopwords:
            words = words[1:]
            changed = True
        if words and words[-1].lower() in stopwords:
            words = words[:-1]
            changed = True
    return words


def _clean_and_validate_subphrase(sub_p: str, stopwords: set) -> str | None:
    """Clean a sub-phrase and return it if valid, otherwise None."""
    sub_words = sub_p.split()
    if len(sub_words) > MAX_PHRASE_WORDS:
        return None
    if all(w.lower() in stopwords for w in sub_words):
        return None

    p_clean = _PUNCTUATION_STRIP_PATTERN.sub("", sub_p).strip()
    p_words = _strip_edge_stopwords(p_clean.split(), stopwords)
    p_clean = " ".join(p_words).strip()

    if len(p_clean) > MIN_PHRASE_LENGTH and p_clean.lower() not in stopwords:
        return p_clean
    return None


def _extract_tech_tokens(text: str, stopwords: set) -> List[str]:
    """Extract single-word tokens that look like technology names or acronyms."""
    results = []
    for w in _TECH_TOKEN_PATTERN.findall(text):
        if w.lower() in stopwords:
            continue
        is_tech_char = any(c in w for c in "+#.-")
        is_all_caps = w.isupper() and len(w) >= MIN_PHRASE_LENGTH
        if is_tech_char or is_all_caps:
            w_clean = _PUNCTUATION_STRIP_PATTERN.sub("", w)
            if len(w_clean) >= MIN_PHRASE_LENGTH and w_clean.lower() not in stopwords:
                results.append(w_clean)
    return results


def extract_phrases(text: str) -> List[str]:
    from app.services.parser import STOPWORDS

    phrases = _PHRASE_SPLIT_PATTERN.split(text)
    valid_phrases = []

    for p in phrases:
        p = p.strip()
        if not p or len(p) <= MIN_PHRASE_LENGTH:
            continue

        for sub_p in _split_on_conjunctions(p):
            cleaned = _clean_and_validate_subphrase(sub_p, STOPWORDS)
            if cleaned:
                valid_phrases.append(cleaned)

    valid_phrases.extend(_extract_tech_tokens(text, STOPWORDS))

    return list(
        set(
            p
            for p in valid_phrases
            if MIN_PHRASE_LENGTH <= len(p) < MAX_PHRASE_CHAR_LENGTH
        )
    )


def normalize_skill_name(name: str) -> str:
    """
    Normalize skill name by converting to lowercase and stripping common suffixes
    like .js, js, framework, library to allow flexible exact matching.
    """
    n = name.lower().strip()
    n = re.sub(r"(?:[\s.-]?js|[\s.-]?j\.s|[\s.-]?j-s)$", "", n)
    n = re.sub(r"(?:[\s.-]?framework|[\s.-]?library)$", "", n)
    return n.strip()


def has_skill_exact(skill: str, text: str) -> bool:
    """
    Check if a skill is present in text as an exact word match (case-insensitive).
    Handles special characters like C++, C#, .NET, etc. safely.
    Also performs soft exact matching for variations like Vue.js vs Vue, ReactJS vs React.
    """
    skill_norm = normalize_skill_name(skill)

    # 1. Soft matching by tokenizing and normalizing each token in the text
    tokens = re.findall(r"\b[a-zA-Z0-9+#.-]+\b", text)
    for token in tokens:
        if normalize_skill_name(token) == skill_norm:
            return True

    # 2. Fallback to standard exact regex matching (for multi-word skills like "Machine Learning")
    skill_lower = skill.lower().strip()
    text_lower = text.lower()
    escaped = re.escape(skill_lower)

    pattern = ""
    if re.match(r"^\w", skill_lower):
        pattern += r"\b"
    pattern += escaped
    if re.search(r"\w$", skill_lower):
        pattern += r"\b"

    return bool(re.search(pattern, text_lower))


def clean_skill_phrase(skill: str) -> str:
    # Remove bullet symbols and formatting characters from start and end
    s = re.sub(r"^[-\*•\s]+", "", skill)
    s = re.sub(r"[-\*•\s]+$", "", s)
    return s.strip()


def _is_blacklisted_phrase(phrase_lower: str, words: List[str]) -> bool:
    """Return True if the phrase or its words hit any blacklist."""
    if (
        phrase_lower in _GENERIC_WORDS
        or phrase_lower in _ROLE_WORDS
        or phrase_lower in _ACTION_WORDS
    ):
        return True
    if any(w in _ROLE_WORDS for w in words):
        return True
    if any(w in _GENERIC_WORDS for w in words):
        return True
    if words[0] in _ACTION_WORDS:
        return True
    return False


def is_valid_skill(phrase: str, domain_skills: set[str]) -> bool:
    clean_phrase = clean_skill_phrase(phrase)

    if len(clean_phrase) < MIN_PHRASE_LENGTH:
        return False

    phrase_lower = clean_phrase.lower()

    domain_skills_lower = {s.lower() for s in domain_skills} if domain_skills else set()
    if phrase_lower in domain_skills_lower:
        return True

    from app.services.parser import STOPWORDS

    words = phrase_lower.split()
    if not words:
        return False

    if _is_blacklisted_phrase(phrase_lower, words):
        return False

    if all(
        w in STOPWORDS or w in _GENERIC_WORDS or w in _ROLE_WORDS or w in _ACTION_WORDS
        for w in words
    ):
        return False

    return True


def _get_tokens(s: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9]+", s.lower())


def _is_sublist(sub: List[str], lst: List[str]) -> bool:
    n, m = len(sub), len(lst)
    for i in range(m - n + 1):
        if lst[i : i + n] == sub:  # noqa: E203
            return True
    return False


def _resolve_sublist_conflict(
    idx_short: int,
    idx_long: int,
    skill_short: str,
    skill_long: str,
    ds_lower: set,
) -> int:
    """Decide which index to remove when one skill's tokens are a sublist of another's."""
    s_lower = skill_short.lower()
    l_lower = skill_long.lower()
    if s_lower in ds_lower and l_lower not in ds_lower:
        return idx_long
    if l_lower in ds_lower and s_lower not in ds_lower:
        return idx_short
    return idx_short


def deduplicate_skills(skills: List[str], domain_skills: List[str] = None) -> List[str]:
    if not skills:
        return []

    ds_lower = {s.lower() for s in domain_skills} if domain_skills else set()
    to_remove: set[int] = set()
    n = len(skills)

    token_cache = [_get_tokens(s) for s in skills]

    for i in range(n):
        if i in to_remove:
            continue
        for j in range(n):
            if i == j or j in to_remove or i in to_remove:
                continue
            t1, t2 = token_cache[i], token_cache[j]
            if not t1 or not t2:
                continue
            if len(t1) < len(t2) and _is_sublist(t1, t2):
                victim = _resolve_sublist_conflict(i, j, skills[i], skills[j], ds_lower)
                to_remove.add(victim)

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
        "nodejs": "Node.js",
    }
    for var_name, norm_name in NORMALIZATION_MAP.items():
        if has_skill_exact(var_name, jd_text):
            if norm_name in master_skills or norm_name in domain_skills:
                target_skills.add(norm_name)

    return list(target_skills)


def _exact_match_skills(
    target_skills: List[str],
    cv_text: str,
) -> Tuple[Dict[str, float], List[str]]:
    """Split target skills into exact-matched (with score) and remaining for semantic check."""
    matched: Dict[str, float] = {}
    remaining: List[str] = []
    for skill in target_skills:
        if has_skill_exact(skill, cv_text):
            matched[skill] = MAX_SCORE_PERCENTAGE
        else:
            remaining.append(skill)
    return matched, remaining


def _semantic_match_skills(
    semantic_check_skills: List[str],
    cv_phrases: List[str],
    domain_skills: List[str],
    threshold_direct: float,
    threshold_master: float,
) -> Tuple[Dict[str, float], Dict[str, float]]:
    """Batch-encode and score remaining skills against CV phrases."""
    matched: Dict[str, float] = {}
    missing: Dict[str, float] = {}

    if not semantic_check_skills or not cv_phrases:
        for skill in semantic_check_skills:
            missing[skill] = 0.0
        return matched, missing

    skill_embs = model.encode(semantic_check_skills, convert_to_tensor=True)
    cv_phrase_embs = model.encode(cv_phrases, convert_to_tensor=True)
    similarities = util.cos_sim(skill_embs, cv_phrase_embs)
    max_sims = similarities.max(dim=1).values.tolist()

    domain_skill_set = set(domain_skills)
    for i, skill in enumerate(semantic_check_skills):
        max_sim = max_sims[i]
        threshold = threshold_master if skill in domain_skill_set else threshold_direct
        if max_sim >= threshold:
            matched[skill] = round(max_sim * MAX_SCORE_PERCENTAGE, 2)
        else:
            missing[skill] = round(max_sim * MAX_SCORE_PERCENTAGE, 2)

    return matched, missing


def match_cv_jd_hybrid(
    cv_text: str, jd_text: str, domain: str, precomputed_target_skills: List[str] = None
) -> Tuple[List[str], List[str], Dict[str, float]]:  # noqa: E501
    """
    Hybrid semantic matching using batch encoding for significant performance improvements.
    Uses precomputed target skills to avoid extracting JD phrases for every candidate.
    """
    from app.core.domain_loader import load_domain_config

    config = load_domain_config(domain)
    domain_skills = config.get("skills", [])
    threshold_direct = config.get("threshold_direct_match", DEFAULT_THRESHOLD_DIRECT)
    threshold_master = config.get("threshold_master_match", DEFAULT_THRESHOLD_MASTER)

    target_skills = (
        precomputed_target_skills
        if precomputed_target_skills is not None
        else extract_jd_target_skills(jd_text, domain)
    )
    if not target_skills:
        return [], [], {}

    cv_phrases = extract_phrases(cv_text)

    matched_with_scores, semantic_check_skills = _exact_match_skills(
        target_skills, cv_text
    )

    sem_matched, sem_missing = _semantic_match_skills(
        semantic_check_skills,
        cv_phrases,
        domain_skills,
        threshold_direct,
        threshold_master,
    )
    matched_with_scores.update(sem_matched)

    matched_skills = sorted(
        matched_with_scores, key=matched_with_scores.get, reverse=True
    )
    missing_skills = sorted(sem_missing, key=sem_missing.get, reverse=True)

    matched_skills = deduplicate_skills(matched_skills, domain_skills)[
        :MAX_OUTPUT_SKILLS
    ]
    missing_skills = deduplicate_skills(missing_skills, domain_skills)[
        :MAX_OUTPUT_SKILLS
    ]

    skill_scores = {**matched_with_scores, **sem_missing}
    return matched_skills, missing_skills, skill_scores


def cluster_documents(
    texts: List[str], filenames: List[str], num_clusters: int = 3
) -> List[Dict[str, Any]]:
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
        clusters[label].append({"filename": filenames[idx], "text": texts[idx]})

    result = []
    for cluster_id, items in clusters.items():
        combined_text = " ".join([item["text"] for item in items])
        cluster_phrases = extract_phrases(combined_text)

        if cluster_phrases:
            phrase_embs = model.encode(
                cluster_phrases[:CLUSTER_MAX_PHRASES], convert_to_tensor=True
            )
            cluster_skills = []

            for skill_name, skill_emb in get_skill_embeddings_for_skills(
                []
            ).items():  # noqa: E501
                similarities = util.cos_sim(skill_emb, phrase_embs)[0]
                max_sim = similarities.max().item()
                if max_sim > CLUSTER_SIMILARITY_THRESHOLD:
                    cluster_skills.append(skill_name)

            suggested_label = (
                " / ".join(cluster_skills[:3])
                if cluster_skills
                else f"Cluster {cluster_id + 1}"
            )
        else:
            suggested_label = f"Cluster {cluster_id + 1}"

        result.append(
            {
                "cluster_id": cluster_id,
                "suggested_label": suggested_label,
                "candidates": [item["filename"] for item in items],
            }
        )

    return result
