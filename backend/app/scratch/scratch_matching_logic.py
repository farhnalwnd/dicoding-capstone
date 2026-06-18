import os
import sys

from sentence_transformers import util

from app.services.nlp import match_cv_jd_hybrid, model

# Set path to backend folder so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Configure model environment variables to absolute local paths ONLY if not already set (e.g. by Docker)
if "MODEL_BI_ENCODER" not in os.environ or not os.environ["MODEL_BI_ENCODER"]:
    workspace_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )
    os.environ["MODEL_BI_ENCODER"] = os.path.join(
        workspace_root, "models", "bi-encoder-cv-matcher"
    )

print(f"MODEL_BI_ENCODER path: {os.environ.get('MODEL_BI_ENCODER')}")

print("Initializing NLP models...")

# Sample test inputs
cv_text = "I am a backend developer. Experieced in Python development, Docker, and PostgreSQL database. Also familiar with Vue."  # noqa: E501
jd_text = "Looking for a Python Developer. Requirements: Python, PostgreSQL, and Vue.js. Experience with Kubernetes is a plus."  # noqa: E501
domain = "it"

print("\n--- Running Similarity Score Test (MATCHING CASE) ---")
# Bi-Encoder Score
emb_cv = model.encode(cv_text, convert_to_tensor=True)
emb_jd = model.encode(jd_text, convert_to_tensor=True)
score_be = round(max(0.0, min(1.0, util.cos_sim(emb_cv, emb_jd).item())) * 100, 2)
print(f"Calculated Match Score (Bi-Encoder): {score_be}%")

cv_non_matching = "I am a creative graphic designer and artist. Experienced in Photoshop, Illustrator, Figma, and painting. I design flyers and posters."  # noqa: E501
print("\n--- Running Similarity Score Test (NON-MATCHING CASE) ---")
emb_cv_non = model.encode(cv_non_matching, convert_to_tensor=True)
score_non_be = round(
    max(0.0, min(1.0, util.cos_sim(emb_cv_non, emb_jd).item())) * 100, 2
)
print(f"Calculated Match Score (Non-matching Bi-Encoder): {score_non_be}%")

print("\n--- Running Hybrid Skills Matching Test (IT Domain) ---")
matched, missing, _ = match_cv_jd_hybrid(cv_text, jd_text, domain)
print(f"Matched Skills: {matched}")
print(f"Missing Skills: {missing}")

# Assertions/Checks to verify correctness
print("\n--- Verifying Results ---")
# 1. Exact matches: "Python" and "PostgreSQL" should be in matched
# 2. Semantic matches: "Vue.js" should be in matched because CV has "Vue" which is close to "Vue.js"
# 3. Missing matches: "Kubernetes" should be in missing
assert "Python" in matched, "Error: Python should be matched (exact)"
assert "PostgreSQL" in matched, "Error: PostgreSQL should be matched (exact)"
assert "Vue.js" in matched, "Error: Vue.js should be matched (semantic match of 'Vue')"
assert "Kubernetes" in missing, "Error: Kubernetes should be missing"
print("All assertions passed successfully! The matching logic works perfectly.")
