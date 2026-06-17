from pathlib import Path
import pandas as pd
import random

random.seed(42)

# =====================================================
# OUTPUT
# =====================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

OUTPUT_DIR = (
    ROOT_DIR
    / "data"
    / "evaluation"
    / "v2"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =====================================================
# ROLE DEFINITIONS
# =====================================================

ROLES = {
    "Backend Developer": {
        "skills": [
            "Python",
            "FastAPI",
            "Docker",
            "PostgreSQL",
            "AWS",
            "REST API",
            "Microservices",
            "CI/CD"
        ]
    },

    "Senior Backend Developer": {
        "skills": [
            "Python",
            "FastAPI",
            "Docker",
            "AWS",
            "Kubernetes",
            "Microservices",
            "System Design",
            "CI/CD"
        ]
    },

    "Frontend Developer": {
        "skills": [
            "Vue.js",
            "JavaScript",
            "HTML",
            "CSS",
            "Vite",
            "TypeScript"
        ]
    },

    "Full Stack Developer": {
        "skills": [
            "Python",
            "FastAPI",
            "Vue.js",
            "Docker",
            "PostgreSQL",
            "JavaScript"
        ]
    },

    "Data Analyst": {
        "skills": [
            "SQL",
            "Excel",
            "Power BI",
            "Python",
            "Data Visualization"
        ]
    },

    "Data Scientist": {
        "skills": [
            "Python",
            "Pandas",
            "Machine Learning",
            "Statistics",
            "TensorFlow",
            "SQL"
        ]
    },

    "Data Engineer": {
        "skills": [
            "Python",
            "SQL",
            "Docker",
            "Airflow",
            "AWS",
            "ETL"
        ]
    },

    "ML Engineer": {
        "skills": [
            "Python",
            "TensorFlow",
            "PyTorch",
            "Docker",
            "ML Ops",
            "AWS"
        ]
    },

    "DevOps Engineer": {
        "skills": [
            "Docker",
            "Kubernetes",
            "AWS",
            "CI/CD",
            "Linux",
            "Terraform"
        ]
    },

    "UI/UX Designer": {
        "skills": [
            "Figma",
            "Wireframing",
            "Prototyping",
            "User Research",
            "Design System"
        ]
    },

    "HR Specialist": {
        "skills": [
            "Recruitment",
            "Interviewing",
            "HRIS",
            "Onboarding",
            "Talent Acquisition"
        ]
    },

    "Recruiter": {
        "skills": [
            "Recruitment",
            "Talent Sourcing",
            "Interviewing",
            "Screening",
            "Employer Branding"
        ]
    },

    "Finance Analyst": {
        "skills": [
            "Financial Analysis",
            "Excel",
            "Budgeting",
            "Forecasting",
            "Accounting"
        ]
    },

    "Sales Executive": {
        "skills": [
            "Sales",
            "CRM",
            "Negotiation",
            "Lead Generation",
            "Communication"
        ]
    },

    "Customer Success": {
        "skills": [
            "Customer Support",
            "CRM",
            "Communication",
            "Retention",
            "Problem Solving"
        ]
    }
}

# =====================================================
# SENIORITY
# =====================================================

SENIORITY = {
    "Junior": (1, 2),
    "Mid": (3, 5),
    "Senior": (6, 10)
}

# =====================================================
# JD GENERATION
# =====================================================

jobs = []

for idx, (role, config) in enumerate(
    ROLES.items(),
    start=1
):

    skills = ", ".join(config["skills"])

    jobs.append({
        "jd_id": f"JD{idx:03d}",
        "title": role,
        "jd_text":
        (
            f"We are looking for a {role} "
            f"with experience in "
            f"{skills}. "
            f"The candidate should be able "
            f"to work collaboratively and "
            f"deliver high-quality solutions."
        )
    })

jobs_df = pd.DataFrame(jobs)

# =====================================================
# CV GENERATION
# =====================================================

cv_distribution = {
    "Backend Developer": 15,
    "Senior Backend Developer": 10,
    "Frontend Developer": 15,
    "Full Stack Developer": 15,
    "Data Analyst": 15,
    "Data Scientist": 15,
    "Data Engineer": 15,
    "ML Engineer": 10,
    "DevOps Engineer": 10,
    "UI/UX Designer": 15,
    "HR Specialist": 15,
    "Recruiter": 10,
    "Finance Analyst": 15,
    "Sales Executive": 15,
    "Customer Success": 10
}

cvs = []

counter = 1

for role, total in cv_distribution.items():

    role_skills = ROLES[role]["skills"]

    for _ in range(total):

        seniority = random.choice(
            list(SENIORITY.keys())
        )

        years = random.randint(
            SENIORITY[seniority][0],
            SENIORITY[seniority][1]
        )

        selected_skills = random.sample(
            role_skills,
            min(
                len(role_skills),
                random.randint(
                    max(3, len(role_skills)//2),
                    len(role_skills)
                )
            )
        )

        cv_text = (
            f"{seniority} {role} with "
            f"{years} years of experience. "
            f"Experienced in "
            f"{', '.join(selected_skills)}. "
            f"Strong collaboration and "
            f"problem solving skills."
        )

        cvs.append({
            "cv_id": f"CV{counter:04d}",
            "target_role": role,
            "seniority": seniority,
            "experience_years": years,
            "cv_text": cv_text
        })

        counter += 1

cvs_df = pd.DataFrame(cvs)

# =====================================================
# LABELING
# =====================================================

def calculate_relevance(
    cv_role,
    cv_seniority,
    jd_role
):

    if cv_role == jd_role:

        if cv_seniority == "Senior":
            return 3

        if cv_seniority == "Mid":
            return 2

        return 2

    overlap_map = {

        "Backend Developer": [
            "Full Stack Developer",
            "Data Engineer",
            "DevOps Engineer"
        ],

        "Senior Backend Developer": [
            "Backend Developer",
            "Full Stack Developer",
            "DevOps Engineer"
        ],

        "Data Scientist": [
            "Data Analyst",
            "ML Engineer"
        ],

        "Data Analyst": [
            "Data Scientist"
        ],

        "HR Specialist": [
            "Recruiter"
        ],

        "Recruiter": [
            "HR Specialist"
        ],

        "Sales Executive": [
            "Customer Success"
        ],

        "Customer Success": [
            "Sales Executive"
        ],

        "Frontend Developer": [
            "Full Stack Developer",
            "UI/UX Designer"
        ],

        "UI/UX Designer": [
            "Frontend Developer"
        ]
    }

    related = overlap_map.get(
        jd_role,
        []
    )

    if cv_role in related:
        return 1

    return 0

labels = []

for _, cv in cvs_df.iterrows():

    for _, jd in jobs_df.iterrows():

        labels.append({
            "cv_id": cv["cv_id"],
            "jd_id": jd["jd_id"],
            "relevance": calculate_relevance(
                cv["target_role"],
                cv["seniority"],
                jd["title"]
            )
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

print("=" * 60)
print("DATASET V2 GENERATED")
print("=" * 60)

print(
    f"CVs: {len(cvs_df)}"
)

print(
    f"Jobs: {len(jobs_df)}"
)

print(
    f"Labels: {len(labels_df)}"
)

print(
    f"Saved to: {OUTPUT_DIR}"
)