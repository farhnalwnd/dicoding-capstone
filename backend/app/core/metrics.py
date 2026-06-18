from prometheus_client import Counter, Histogram

# ====================================
# Model & AI Metrics
# ====================================

MODEL_INFERENCE_LATENCY = Histogram(
    "model_inference_latency_seconds", "Time spent running Bi-Encoder inference"
)

MATCH_SCORE_DISTRIBUTION = Histogram(
    "match_score_distribution",
    "Distribution of final match scores",
    buckets=(0, 20, 40, 60, 80, 100),
)

DOMAIN_CLASSIFICATION_COUNT = Counter(
    "domain_classification_total", "Counts of CVs categorized by domain", ["domain"]
)

# ====================================
# Request Counter
# ====================================

REQUEST_COUNT = Counter("cv_matcher_requests_total", "Total API Requests", ["endpoint"])

# ====================================
# Request Latency
# ====================================

REQUEST_LATENCY = Histogram(
    "cv_matcher_request_latency_seconds", "API Request Latency", ["endpoint"]
)

# ====================================
# Match Analysis Counter
# ====================================

MATCH_ANALYSIS_COUNT = Counter(
    "cv_matcher_analysis_total", "Total CV-JD Analysis Requests"
)

# ====================================
# Semantic Search Counter
# ====================================

SEMANTIC_SEARCH_COUNT = Counter(
    "semantic_search_total", "Total Semantic Search Requests"
)

# ====================================
# HR Ranking Counter
# ====================================

HR_RANKING_COUNT = Counter("hr_ranking_total", "Total HR Ranking Requests")

CLUSTERING_COUNT = Counter("cv_clustering_total", "Total CV Clustering Requests")

SCRAPE_RECOMMEND_COUNT = Counter(
    "scrape_recommend_total", "Total LinkedIn Scraping Requests"
)
