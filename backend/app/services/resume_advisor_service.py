import json
import os
from typing import Dict, List

import fitz
import requests

# Gemini API Endpoint URL
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# PDF Layout Constants (A4: 595 x 842 points)
PDF_LEFT_MARGIN = 50
PDF_RIGHT_MARGIN = 545
PDF_TOP_MARGIN = 50
PDF_BOTTOM_MARGIN = 792

# Mock recommendation constants
MIN_IMPROVEMENT = 15.0
MAX_IMPROVEMENT = 30.0
IMPROVEMENT_FACTOR = 0.4
MAX_ESTIMATED_SCORE = 95.0
MISSING_SKILLS_PREVIEW_COUNT = 3

# Skills categories for career recommendations
ML_SKILLS = ["python", "machine learning", "nlp", "tensorflow", "pytorch"]
FRONTEND_SKILLS = ["vue", "react", "html", "css", "javascript"]

GEMINI_REQUEST_TIMEOUT = 15


def _build_gemini_prompt(
    match_score: float,
    matched_skills: List[str],
    missing_skills: List[str],
    recommendation: str,
    job_description: str,
) -> str:
    """Build the Gemini API prompt for resume advisor analysis."""
    return (
        "You are an expert AI Resume Advisor. Analyze the candidate's CV matching details against the job description:\n"  # noqa: E501
        f"Current Match Score: {match_score}%\n"
        f"Current Recommendation Level: {recommendation}\n"
        f"Matched Skills: {', '.join(matched_skills) if matched_skills else 'None'}\n"
        f"Missing Skills: {', '.join(missing_skills) if missing_skills else 'None'}\n"
        f"Job Description: {job_description}\n\n"
        "Provide your analysis in JSON format ONLY with the following keys. Do not include markdown code block syntax (like ```json ... ```) in the response:\n"  # noqa: E501
        "{\n"
        '  "estimated_score": <number, potential score after applying tips, e.g. 75.5>,\n'
        '  "missing_skills_summary": "<string, e.g. \'You are currently missing Docker, Kubernetes, and CI/CD experience.\'>",\n'  # noqa: E501
        '  "learning_plan": [\n'
        "    {\n"
        '      "duration": "<string, e.g. \'Week 1-2\'>",\n'
        '      "tasks": ["<string, task 1>", "<string, task 2>"]\n'
        "    }\n"
        "  ],\n"
        '  "resume_tips": ["<string, tip 1>", "<string, tip 2>"],\n'
        '  "interview_tips": ["<string, tip 1>", "<string, tip 2>"],\n'
        '  "career_suitability": "<string, explanation of suitability>",\n'
        '  "recommended_roles": ["<string, role 1>", "<string, role 2>"],\n'
        '  "recommended_technologies": ["<string, tech 1>", "<string, tech 2>"]\n'
        "}"
    )


def _parse_gemini_response(response_json: Dict, match_score: float) -> Dict:
    """Extract and parse JSON content from a Gemini API response."""
    text_content = response_json["candidates"][0]["content"]["parts"][0]["text"].strip()
    # Clean up potential markdown formatting wrapping JSON
    if text_content.startswith("```"):
        lines = text_content.split("\n")
        text_content = "\n".join(lines[1:-1])

    parsed_json = json.loads(text_content)
    parsed_json["current_score"] = match_score
    return parsed_json


def _call_gemini_api(api_key: str, prompt: str) -> Dict:
    """Send a prompt to the Gemini API and return the response JSON."""
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    response = requests.post(
        f"{GEMINI_API_URL}?key={api_key}",
        headers=headers,
        json=payload,
        timeout=GEMINI_REQUEST_TIMEOUT,
    )
    return response


def generate_advisor_recommendations(
    match_score: float,
    matched_skills: List[str],
    missing_skills: List[str],
    recommendation: str,
    job_description: str,
) -> Dict:
    """
    Generate actionable resume improvement recommendations using Gemini API.
    If GEMINI_API_KEY is not configured, fallback to dynamic mock generation.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            prompt = _build_gemini_prompt(
                match_score,
                matched_skills,
                missing_skills,
                recommendation,
                job_description,
            )
            response = _call_gemini_api(api_key, prompt)

            if response.status_code == 200:
                return _parse_gemini_response(response.json(), match_score)

        except Exception as e:
            print(
                f"Error calling Gemini API: {str(e)}. Falling back to mock generator."
            )

    # Mock fallback recommendations if API key is not present or calls fail
    return generate_mock_recommendations(
        match_score, matched_skills, missing_skills, job_description
    )


def _build_missing_skills_summary(missing_skills: List[str]) -> str:
    """Build a human-readable summary of missing skills."""
    if missing_skills:
        skills_str = ", ".join(missing_skills[:MISSING_SKILLS_PREVIEW_COUNT])
        if len(missing_skills) > MISSING_SKILLS_PREVIEW_COUNT:
            skills_str += "..."
        return f"You are currently missing {skills_str} experience specified in the job requirements."
    return "Great job! You match all the key skills listed in this job description."


def _build_learning_plan(missing_skills: List[str]) -> List[Dict]:
    """Build a week-by-week learning plan based on missing skills."""
    if not missing_skills:
        return [
            {
                "duration": "Week 1-2",
                "tasks": [
                    "Review advanced architectural patterns in your field",
                    "Practice system design interviews or domain-specific deep dives",
                ],
            },
            {
                "duration": "Week 3-4",
                "tasks": [
                    "Contribute to open-source libraries related to your matched stack",
                    "Prepare advanced portfolio demonstrations",
                ],
            },
        ]

    plan = []
    # Week 1-2
    tasks1 = [f"Learn fundamentals of {missing_skills[0]}"]
    if len(missing_skills) > 1:
        tasks1.append(f"Explore tutorial projects on {missing_skills[1]}")
    plan.append({"duration": "Week 1-2", "tasks": tasks1})

    # Week 3-4
    if len(missing_skills) > 2:
        plan.append(
            {
                "duration": "Week 3-4",
                "tasks": [
                    f"Get hands-on experience with {missing_skills[2]}",
                    "Build a sample application integrating learned techniques",
                ],
            }
        )
    else:
        plan.append(
            {
                "duration": "Week 3-4",
                "tasks": [
                    "Implement advanced patterns and optimization techniques",
                    "Create a GitHub repository demonstrating your skills",
                ],
            }
        )

    # Week 5
    plan.append(
        {
            "duration": "Week 5",
            "tasks": [
                "Deploy your personal portfolio projects",
                "Refactor resume to emphasize your newly acquired skills",
            ],
        }
    )
    return plan


def _build_resume_tips(missing_skills: List[str]) -> List[str]:
    """Build resume optimization tips based on missing skills."""
    if missing_skills:
        return [
            f"Add quantified achievements or projects highlighting any exposure to {missing_skills[0]}.",
            "Format work achievements using the STAR method (Situation, Task, Action, Result) focusing on efficiency gains.",  # noqa: E501
            "Highlight your capability with relevant modern technologies in your technical skills grid.",
        ]
    return [
        "Add quantified achievements detailing scale, team size, and impact of your contributions.",
        "Create a dedicated 'Key Highlights' section at the top of your resume showing core credentials.",
    ]


def _build_interview_tips(missing_skills: List[str]) -> List[str]:
    """Build interview preparation tips based on missing skills."""
    if not missing_skills:
        return [
            "Prepare stories about resolving technical friction, architecture scaling, or cross-functional coordination.",  # noqa: E501
            "Review domain system design questions to showcase top-tier engineering insights.",
        ]
    tips = [
        f"Prepare to answer basic conceptual questions regarding {missing_skills[0]}.",
        "Draft short explanations of how you would adapt to and learn new cloud-native/deployment pipelines.",
    ]
    if len(missing_skills) > 1:
        tips.append(f"Review practical usage scenarios for {missing_skills[1]}.")
    return tips


def _build_career_recommendations(matched_skills: List[str]) -> Dict:
    """Build career suitability analysis and role/tech recommendations."""
    suitability = (
        "Your profile is aligned with modern technical roles, but acquiring additional "
        "infrastructure or platform experience will greatly increase your eligibility."
    )
    rec_roles = ["Senior Engineer", "DevOps Specialist", "Full Stack Developer"]
    rec_techs = ["Docker", "Kubernetes", "FastAPI", "GitHub Actions"]

    if matched_skills:
        lowered = [s.lower() for s in matched_skills]
        if any(s in ML_SKILLS for s in lowered):
            suitability = (
                "You possess strong machine learning and data science fundamentals. "
                "Transitioning to platform AI engineering is highly recommended."
            )
            rec_roles = ["AI Engineer", "MLOps Engineer", "NLP Scientist"]
            rec_techs = ["PyTorch", "Hugging Face", "MLflow", "Kubeflow"]
        elif any(s in FRONTEND_SKILLS for s in lowered):
            suitability = (
                "Your skills point toward interactive user interfaces. Adding backend "
                "frameworks will make you an excellent full-stack candidate."
            )
            rec_roles = ["Frontend Architect", "Full Stack Engineer", "UI Developer"]
            rec_techs = ["TypeScript", "Next.js", "Tailwind CSS", "GraphQL"]

    return {
        "career_suitability": suitability,
        "recommended_roles": rec_roles,
        "recommended_technologies": rec_techs,
    }


def generate_mock_recommendations(
    match_score: float,
    matched_skills: List[str],
    missing_skills: List[str],
    job_description: str,
) -> Dict:
    """
    Dynamically generates mock recommendations based on the candidate's actual CV-JD analysis variables.
    """
    # Potential match score goes up between 15-30% capped at 95%
    improvement = min(
        MAX_IMPROVEMENT,
        max(MIN_IMPROVEMENT, (100.0 - match_score) * IMPROVEMENT_FACTOR),
    )
    estimated_score = min(MAX_ESTIMATED_SCORE, round(match_score + improvement, 2))

    return {
        "current_score": match_score,
        "estimated_score": estimated_score,
        "missing_skills_summary": _build_missing_skills_summary(missing_skills),
        "learning_plan": _build_learning_plan(missing_skills),
        "resume_tips": _build_resume_tips(missing_skills),
        "interview_tips": _build_interview_tips(missing_skills),
        "career_recommendations": _build_career_recommendations(matched_skills),
    }


def generate_advisor_pdf(rec: Dict) -> bytes:
    """
    Draw a clean, well-formatted PDF report from Advisor recommendations using PyMuPDF (fitz).
    Returns PDF content in bytes.
    """
    doc = fitz.open()
    page = doc.new_page()  # A4: 595 x 842 points

    left_margin = PDF_LEFT_MARGIN
    right_margin = PDF_RIGHT_MARGIN
    top_margin = PDF_TOP_MARGIN
    bottom_margin = PDF_BOTTOM_MARGIN

    y = top_margin

    def add_page_if_needed(current_y, size=50):
        nonlocal page, y
        if current_y > bottom_margin - size:
            page = doc.new_page()
            y = top_margin
            return True
        return False

    # Parameters: text, start_x, start_y, font_size, font_name, color, is_bold (grouped as content + style)
    def draw_text_wrapped(
        text,
        start_x,
        start_y,
        font_size=10,
        font_name="helv",
        color=(0.1, 0.1, 0.1),
        is_bold=False,
    ):
        words = text.split(" ")
        lines = []
        current_line = []
        max_chars = int((right_margin - start_x) / (0.52 * font_size))

        for word in words:
            current_len = sum(len(w) + 1 for w in current_line) + len(word)
            if current_len > max_chars:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        if current_line:
            lines.append(" ".join(current_line))

        y_pos = start_y
        font_style = "helv"

        for line in lines:
            add_page_if_needed(y_pos, font_size * 2)
            page.insert_text(
                (start_x, y_pos),
                line,
                fontsize=font_size,
                fontname=font_style,
                color=color,
            )
            y_pos += font_size * 1.45

        return y_pos

    # Title Header
    page.insert_text(
        (left_margin, y),
        "AI RESUME ADVISOR REPORT",
        fontsize=18,
        fontname="helv",
        color=(0.02, 0.35, 0.52),
    )
    y += 15
    page.insert_text(
        (left_margin, y),
        "Personalized Career Analysis and Skills Roadmap",
        fontsize=10,
        fontname="helv",
        color=(0.4, 0.4, 0.4),
    )
    y += 40

    # Section 1: Overview
    page.draw_rect(
        fitz.Rect(left_margin, y - 12, right_margin, y + 5),
        color=(0.9, 0.9, 0.9),
        fill=(0.9, 0.9, 0.9),
    )
    page.insert_text(
        (left_margin, y),
        "1. Analysis Overview",
        fontsize=12,
        fontname="helv",
        color=(0.02, 0.35, 0.52),
    )
    y += 20
    score_text = f"Current Match Score: {rec.get('current_score', 0):.1f}%"
    y = draw_text_wrapped(score_text, left_margin, y, 10, "helv")

    target_score = min(rec.get("current_score", 0) + 15.0, 100)
    target_text = f"Potential Score After Improvements: ~{target_score:.1f}%"
    y = draw_text_wrapped(target_text, left_margin, y, 10, "helv")
    y += 20

    # Section 2: Skills
    page.draw_rect(
        fitz.Rect(left_margin, y - 12, right_margin, y + 5),
        color=(0.9, 0.9, 0.9),
        fill=(0.9, 0.9, 0.9),
    )
    page.insert_text(
        (left_margin, y),
        "2. Skills Assessment",
        fontsize=12,
        fontname="helv",
        color=(0.02, 0.35, 0.52),
    )
    y += 20
    summary = rec.get("missing_skills_summary", "Assessments completed.")
    y = draw_text_wrapped(summary, left_margin, y, 10, "helv")
    y += 20

    # Section 3: Roadmap
    add_page_if_needed(y, 60)
    page.draw_rect(
        fitz.Rect(left_margin, y - 12, right_margin, y + 5),
        color=(0.9, 0.9, 0.9),
        fill=(0.9, 0.9, 0.9),
    )
    page.insert_text(
        (left_margin, y),
        "3. Week-by-Week Learning Roadmap",
        fontsize=12,
        fontname="helv",
        color=(0.02, 0.35, 0.52),
    )
    y += 20

    for plan in rec.get("learning_plan", []):
        add_page_if_needed(y, 60)
        y = draw_text_wrapped(
            f"- {plan.get('duration', 'Phase')}:", left_margin, y, 10, "helv"
        )
        for task in plan.get("tasks", []):
            y = draw_text_wrapped(f"  • {task}", left_margin + 10, y, 9.5, "helv")
        y += 10

    # Section 4: Tips
    add_page_if_needed(y, 60)
    page.draw_rect(
        fitz.Rect(left_margin, y - 12, right_margin, y + 5),
        color=(0.9, 0.9, 0.9),
        fill=(0.9, 0.9, 0.9),
    )
    page.insert_text(
        (left_margin, y),
        "4. Actionable Improvements & Interview Tips",
        fontsize=12,
        fontname="helv",
        color=(0.02, 0.35, 0.52),
    )
    y += 20

    y = draw_text_wrapped("Resume Optimizations:", left_margin, y, 10.5, "helv")
    for tip in rec.get("resume_tips", []):
        y = draw_text_wrapped(f"  • {tip}", left_margin + 10, y, 9.5, "helv")
    y += 10

    y = draw_text_wrapped("Interview Practice Focus:", left_margin, y, 10.5, "helv")
    for tip in rec.get("interview_tips", []):
        y = draw_text_wrapped(f"  • {tip}", left_margin + 10, y, 9.5, "helv")
    y += 20

    # Section 5: Recommendations
    add_page_if_needed(y, 60)
    page.draw_rect(
        fitz.Rect(left_margin, y - 12, right_margin, y + 5),
        color=(0.9, 0.9, 0.9),
        fill=(0.9, 0.9, 0.9),
    )
    page.insert_text(
        (left_margin, y),
        "5. AI Career Insights",
        fontsize=12,
        fontname="helv",
        color=(0.02, 0.35, 0.52),
    )
    y += 18

    career = rec.get("career_recommendations", {})
    suitability = career.get(
        "career_suitability", "Suitable for modern engineering tracks."
    )
    y = draw_text_wrapped(suitability, left_margin, y, 10, "helv")
    y += 5

    roles = career.get("recommended_roles", [])
    if roles:
        y = draw_text_wrapped(
            f"Recommended Roles: {', '.join(roles)}",
            left_margin + 15,
            y,
            font_size=10,
            is_bold=True,
        )

    techs = career.get("recommended_technologies", [])
    if techs:
        y = draw_text_wrapped(
            f"Recommended Technologies: {', '.join(techs)}",
            left_margin + 15,
            y,
            font_size=10,
            is_bold=True,
            color=(0.02, 0.35, 0.52),
        )

    return doc.write()
