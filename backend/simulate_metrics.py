import sys
import os

# Add the app directory to sys.path
sys.path.append("/app")

from app.services.nlp import analyze_cv_jd

cv = "I am a skilled software engineer with 5 years of Python, Docker, and Kubernetes experience."
jd = "Looking for a Python Backend Developer with Docker and cloud experience."
domain = "it"

# Run it 5 times to populate metrics
for _ in range(5):
    res = analyze_cv_jd(cv, jd, domain)
    print(f"Score: {res['match_score']}, Domain: {domain}")

print("Metrics generated!")
