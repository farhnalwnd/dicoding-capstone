from pathlib import Path
import random
import pandas as pd

# =====================================================
# CONFIG
# =====================================================

NUM_CVS = 300
NUM_JOBS = 20

ROOT_DIR = Path(__file__).resolve().parents[1]

OUTPUT_DIR = (
    ROOT_DIR
    / "data"
    / "evaluation"
    / "v3"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =====================================================
# DOMAINS
# =====================================================

DOMAIN_SKILLS = {
    "Backend": [
        "Python",
        "FastAPI",
        "Django",
        "PostgreSQL",
        "Docker",
        "REST API"
    ],
    "Frontend": [
        "React",
        "Vue",
        "JavaScript",
        "TypeScript",
        "Tailwind",
        "HTML"
    ],
    "Data": [
        "Python",
        "Pandas",
        "NumPy",
        "SQL",
        "Machine Learning",
        "TensorFlow"
    ],
    "Mobile": [
        "Flutter",
        "Dart",
        "Android",
        "Kotlin",
        "Firebase",
        "Mobile UI"
    ],
    "DevOps": [
        "Docker",
        "Kubernetes",
        "Linux",
        "AWS",
        "CI/CD",
        "Terraform"
    ]
}

# =====================================================
# CREATE JOBS
# =====================================================

jobs = []

for i in range(NUM_JOBS):

    domain = random.choice(
        list(DOMAIN_SKILLS.keys())
    )

    skills = random.sample(
        DOMAIN_SKILLS[domain],
        4
    )

    jobs.append({
        "jd_id": f"JD{i+1:03}",
        "title": f"{domain} Engineer",
        "required_skills": ", ".join(skills),
        "jd_text":
            f"Looking for a {domain} Engineer "
            f"with experience in "
            f"{', '.join(skills)}."
    })

jobs_df = pd.DataFrame(jobs)

# =====================================================
# CREATE CVS
# =====================================================

cvs = []

for i in range(NUM_CVS):

    domain = random.choice(
        list(DOMAIN_SKILLS.keys())
    )

    skills = random.sample(
        DOMAIN_SKILLS[domain],
        4
    )

    cvs.append({
        "cv_id": f"CV{i+1:03}",
        "target_role": f"{domain} Developer",
        "skills": ", ".join(skills),
        "cv_text":
            f"{domain} Developer with experience in "
            f"{', '.join(skills)}."
    })

cvs_df = pd.DataFrame(cvs)

# =====================================================
# LABEL GENERATION
# =====================================================

labels = []

for _, cv in cvs_df.iterrows():

    cv_skills = set(
        skill.strip()
        for skill in cv["skills"].split(",")
    )

    cv_domain = cv["target_role"].split()[0]

    for _, jd in jobs_df.iterrows():

        jd_skills = set(
            skill.strip()
            for skill in jd["required_skills"].split(",")
        )

        jd_domain = jd["title"].split()[0]

        overlap = len(
            cv_skills.intersection(jd_skills)
        )

        # Strong Match
        if (
            cv_domain == jd_domain
            and overlap >= 3
        ):
            relevance = 3

        # Good Match
        elif (
            cv_domain == jd_domain
            and overlap >= 2
        ):
            relevance = 2

        # Moderate Match
        elif overlap >= 1:
            relevance = 1

        # Hard Negative / Irrelevant
        else:
            relevance = 0

        labels.append({
            "cv_id": cv["cv_id"],
            "jd_id": jd["jd_id"],
            "relevance": relevance
        })

labels_df = pd.DataFrame(labels)

# =====================================================
# SAVE
# =====================================================

cvs_df.to_csv(
    OUTPUT_DIR / "cvs.csv",
    index=False
)

jobs_df.to_csv(
    OUTPUT_DIR / "jobs.csv",
    index=False
)

labels_df.to_csv(
    OUTPUT_DIR / "cv_jd_labeled.csv",
    index=False
)

# =====================================================
# SUMMARY
# =====================================================

print("=" * 60)
print("DATASET V3 GENERATED")
print("=" * 60)

print(f"CVs      : {len(cvs_df)}")
print(f"Jobs     : {len(jobs_df)}")
print(f"Labels   : {len(labels_df)}")

print("\nLabel Distribution:")

print(
    labels_df["relevance"]
    .value_counts()
    .sort_index()
)

print(f"\nSaved to:")
print(OUTPUT_DIR)