from prometheus_client import Counter
from prometheus_client import Histogram

# ====================================
# Request Counter
# ====================================

REQUEST_COUNT = Counter(
    "cv_matcher_requests_total",
    "Total API Requests",
    ["endpoint"]
)

# ====================================
# Request Latency
# ====================================

REQUEST_LATENCY = Histogram(
    "cv_matcher_request_latency_seconds",
    "API Request Latency",
    ["endpoint"]
)

# ====================================
# Match Analysis Counter
# ====================================

MATCH_ANALYSIS_COUNT = Counter(
    "cv_matcher_analysis_total",
    "Total CV-JD Analysis Requests"
)

# ====================================
# Semantic Search Counter
# ====================================

SEMANTIC_SEARCH_COUNT = Counter(
    "semantic_search_total",
    "Total Semantic Search Requests"
)

# ====================================
# HR Ranking Counter
# ====================================

HR_RANKING_COUNT = Counter(
    "hr_ranking_total",
    "Total HR Ranking Requests"
)

CLUSTERING_COUNT = Counter(
    "cv_clustering_total",
    "Total CV Clustering Requests"
)

SCRAPE_RECOMMEND_COUNT = Counter(
    "scrape_recommend_total",
    "Total LinkedIn Scraping Requests"
)