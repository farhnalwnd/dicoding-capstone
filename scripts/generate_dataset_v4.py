import random
import pandas as pd
from pathlib import Path

OUTPUT_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "evaluation"
    / "v4"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =====================================================
# ROLE CLUSTERS
# =====================================================

ROLE_CLUSTERS = {

    "backend_python": {
        "skills": [
            "Python",
            "FastAPI",
            "Django",
            "PostgreSQL",
            "Docker"
        ]
    },

    "backend_java": {
        "skills": [
            "Java",
            "Spring Boot",
            "Hibernate",
            "MySQL",
            "Docker"
        ]
    },

    "backend_node": {
        "skills": [
            "NodeJS",
            "Express",
            "MongoDB",
            "Docker"
        ]
    },

    "backend_golang": {
        "skills": [
            "Golang",
            "Gin",
            "PostgreSQL",
            "Redis"
        ]
    },

    "devops": {
        "skills": [
            "AWS",
            "Terraform",
            "Docker",
            "Kubernetes"
        ]
    },

    "data_engineer": {
        "skills": [
            "Spark",
            "Airflow",
            "Python",
            "ETL"
        ]
    },

    "data_scientist": {
        "skills": [
            "Python",
            "Pandas",
            "Machine Learning",
            "NLP"
        ]
    },

    "frontend_react": {
        "skills": [
            "React",
            "TypeScript",
            "Redux",
            "CSS"
        ]
    },

    "frontend_vue": {
        "skills": [
            "Vue",
            "Pinia",
            "JavaScript",
            "CSS"
        ]
    },

    "fullstack": {
        "skills": [
            "React",
            "NodeJS",
            "PostgreSQL",
            "Docker"
        ]
    },

    "hr": {
        "skills": [
            "Recruitment",
            "Talent Acquisition",
            "Interview"
        ]
    },

    "finance": {
        "skills": [
            "Accounting",
            "Budgeting",
            "Excel"
        ]
    }
}

# =====================================================
# RELEVANCE RULE
# =====================================================

RELATED = {

    "backend_python": [
        "backend_java",
        "backend_node",
        "backend_golang"
    ],

    "backend_java": [
        "backend_python",
        "backend_node",
        "backend_golang"
    ],

    "backend_node": [
        "backend_python",
        "backend_java",
        "backend_golang"
    ],

    "backend_golang": [
        "backend_python",
        "backend_java",
        "backend_node"
    ],

    "devops": [
        "backend_python",
        "data_engineer"
    ],

    "data_engineer": [
        "devops",
        "data_scientist"
    ],

    "frontend_react": [
        "frontend_vue",
        "fullstack"
    ],

    "frontend_vue": [
        "frontend_react",
        "fullstack"
    ],

    "fullstack": [
        "frontend_react",
        "backend_python"
    ]
}

# =====================================================
# GENERATE CVS
# =====================================================

cvs = []

for i in range(300):

    role = random.choice(
        list(ROLE_CLUSTERS.keys())
    )

    skills = ROLE_CLUSTERS[role]["skills"]

    cvs.append({

        "cv_id": f"CV{i+1:03}",

        "role": role,

        "cv_text":
            f"Experienced {role} with expertise in "
            + ", ".join(skills)

    })

cvs_df = pd.DataFrame(cvs)

# =====================================================
# GENERATE JD
# =====================================================

jobs = []

for i in range(20):

    role = random.choice(
        list(ROLE_CLUSTERS.keys())
    )

    skills = ROLE_CLUSTERS[role]["skills"]

    jobs.append({

        "jd_id": f"JD{i+1:03}",

        "role": role,

        "jd_text":
            f"Hiring {role} with skills in "
            + ", ".join(skills)

    })

jobs_df = pd.DataFrame(jobs)

# =====================================================
# LABELING
# =====================================================

labels = []

for _, cv in cvs_df.iterrows():

    for _, jd in jobs_df.iterrows():

        cv_role = cv["role"]
        jd_role = jd["role"]

        if cv_role == jd_role:

            relevance = 3

        elif jd_role in RELATED.get(
            cv_role,
            []
        ):

            relevance = 2

        elif (
            "backend" in cv_role
            and "backend" in jd_role
        ):

            relevance = 1

        elif (
            "frontend" in cv_role
            and "frontend" in jd_role
        ):

            relevance = 1

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

print("Dataset V4 generated")

print(
    f"CVs: {len(cvs_df)}"
)

print(
    f"Jobs: {len(jobs_df)}"
)

print(
    f"Labels: {len(labels_df)}"
)