import os
import json
import time
import requests
import fitz
from typing import List, Dict

# Gemini API Endpoint URL
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def generate_advisor_recommendations(
    match_score: float,
    matched_skills: List[str],
    missing_skills: List[str],
    recommendation: str,
    job_description: str
) -> Dict:
    """
    Generate actionable resume improvement recommendations using Gemini API.
    If GEMINI_API_KEY is not configured, fallback to dynamic mock generation.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        try:
            # Build prompt requesting specific JSON output
            prompt = (
                "You are an expert AI Resume Advisor. Analyze the candidate's CV matching details against the job description:\n"
                f"Current Match Score: {match_score}%\n"
                f"Current Recommendation Level: {recommendation}\n"
                f"Matched Skills: {', '.join(matched_skills) if matched_skills else 'None'}\n"
                f"Missing Skills: {', '.join(missing_skills) if missing_skills else 'None'}\n"
                f"Job Description: {job_description}\n\n"
                "Provide your analysis in JSON format ONLY with the following keys. Do not include markdown code block syntax (like ```json ... ```) in the response:\n"
                "{\n"
                "  \"estimated_score\": <number, potential score after applying tips, e.g. 75.5>,\n"
                "  \"missing_skills_summary\": \"<string, e.g. 'You are currently missing Docker, Kubernetes, and CI/CD experience.'>\",\n"
                "  \"learning_plan\": [\n"
                "    {\n"
                "      \"duration\": \"<string, e.g. 'Week 1-2'>\",\n"
                "      \"tasks\": [\"<string, task 1>\", \"<string, task 2>\"]\n"
                "    }\n"
                "  ],\n"
                "  \"resume_tips\": [\"<string, tip 1>\", \"<string, tip 2>\"],\n"
                "  \"interview_tips\": [\"<string, tip 1>\", \"<string, tip 2>\"],\n"
                "  \"career_suitability\": \"<string, explanation of suitability>\",\n"
                "  \"recommended_roles\": [\"<string, role 1>\", \"<string, role 2>\"],\n"
                "  \"recommended_technologies\": [\"<string, tech 1>\", \"<string, tech 2>\"]\n"
                "}"
            )
            
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "responseMimeType": "application/json"
                }
            }
            
            response = requests.post(
                f"{GEMINI_API_URL}?key={api_key}",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                res_data = response.json()
                text_content = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                # Clean up potential markdown formatting wrapping JSON
                if text_content.startswith("```"):
                    lines = text_content.split("\n")
                    if lines[0].startswith("```json"):
                        text_content = "\n".join(lines[1:-1])
                    else:
                        text_content = "\n".join(lines[1:-1])
                
                parsed_json = json.loads(text_content)
                # Enforce structure
                parsed_json["current_score"] = match_score
                return parsed_json
                
        except Exception as e:
            print(f"Error calling Gemini API: {str(e)}. Falling back to mock generator.")
            
    # Mock fallback recommendations if API key is not present or calls fail
    return generate_mock_recommendations(match_score, matched_skills, missing_skills, job_description)

def generate_mock_recommendations(
    match_score: float,
    matched_skills: List[str],
    missing_skills: List[str],
    job_description: str
) -> Dict:
    """
    Dynamically generates mock recommendations based on the candidate's actual CV-JD analysis variables.
    """
    # Potential match score goes up between 15-30% capped at 95%
    improvement = min(30.0, max(15.0, (100.0 - match_score) * 0.4))
    estimated_score = min(95.0, round(match_score + improvement, 2))
    
    # Missing skills summary
    if missing_skills:
        skills_str = ", ".join(missing_skills[:3]) + ("..." if len(missing_skills) > 3 else "")
        summary = f"You are currently missing {skills_str} experience specified in the job requirements."
    else:
        summary = "Great job! You match all the key skills listed in this job description."
        
    # Learning plan
    learning_plan = []
    if missing_skills:
        # Week 1-2
        tasks1 = [f"Learn fundamentals of {missing_skills[0]}"]
        if len(missing_skills) > 1:
            tasks1.append(f"Explore tutorial projects on {missing_skills[1]}")
        learning_plan.append({
            "duration": "Week 1-2",
            "tasks": tasks1
        })
        # Week 3-4
        if len(missing_skills) > 2:
            learning_plan.append({
                "duration": "Week 3-4",
                "tasks": [
                    f"Get hands-on experience with {missing_skills[2]}",
                    "Build a sample application integrating learned techniques"
                ]
            })
        else:
            learning_plan.append({
                "duration": "Week 3-4",
                "tasks": [
                    "Implement advanced patterns and optimization techniques",
                    "Create a GitHub repository demonstrating your skills"
                ]
            })
        # Week 5
        learning_plan.append({
            "duration": "Week 5",
            "tasks": [
                "Deploy your personal portfolio projects",
                "Refactor resume to emphasize your newly acquired skills"
            ]
        })
    else:
        learning_plan.append({
            "duration": "Week 1-2",
            "tasks": [
                "Review advanced architectural patterns in your field",
                "Practice system design interviews or domain-specific deep dives"
            ]
        })
        learning_plan.append({
            "duration": "Week 3-4",
            "tasks": [
                "Contribute to open-source libraries related to your matched stack",
                "Prepare advanced portfolio demonstrations"
            ]
        })
        
    # Resume Tips
    resume_tips = []
    if missing_skills:
        resume_tips.append(f"Add quantified achievements or projects highlighting any exposure to {missing_skills[0]}.")
        resume_tips.append("Format work achievements using the STAR method (Situation, Task, Action, Result) focusing on efficiency gains.")
        resume_tips.append("Highlight your capability with relevant modern technologies in your technical skills grid.")
    else:
        resume_tips.append("Add quantified achievements detailing scale, team size, and impact of your contributions.")
        resume_tips.append("Create a dedicated 'Key Highlights' section at the top of your resume showing core credentials.")
        
    # Interview Tips
    interview_tips = []
    if missing_skills:
        interview_tips.append(f"Prepare to answer basic conceptual questions regarding {missing_skills[0]}.")
        interview_tips.append("Draft short explanations of how you would adapt to and learn new cloud-native/deployment pipelines.")
        if len(missing_skills) > 1:
            interview_tips.append(f"Review practical usage scenarios for {missing_skills[1]}.")
    else:
        interview_tips.append("Prepare stories about resolving technical friction, architecture scaling, or cross-functional coordination.")
        interview_tips.append("Review domain system design questions to showcase top-tier engineering insights.")
        
    # Career Recommendations
    suitability = "Your profile is aligned with modern technical roles, but acquiring additional infrastructure or platform experience will greatly increase your eligibility."
    rec_roles = ["Senior Engineer", "DevOps Specialist", "Full Stack Developer"]
    rec_techs = ["Docker", "Kubernetes", "FastAPI", "GitHub Actions"]
    
    if matched_skills:
        if any(s.lower() in ["python", "machine learning", "nlp", "tensorflow", "pytorch"] for s in matched_skills):
            suitability = "You possess strong machine learning and data science fundamentals. Transitioning to platform AI engineering is highly recommended."
            rec_roles = ["AI Engineer", "MLOps Engineer", "NLP Scientist"]
            rec_techs = ["PyTorch", "Hugging Face", "MLflow", "Kubeflow"]
        elif any(s.lower() in ["vue", "react", "html", "css", "javascript"] for s in matched_skills):
            suitability = "Your skills point toward interactive user interfaces. Adding backend frameworks will make you an excellent full-stack candidate."
            rec_roles = ["Frontend Architect", "Full Stack Engineer", "UI Developer"]
            rec_techs = ["TypeScript", "Next.js", "Tailwind CSS", "GraphQL"]
            
    return {
        "current_score": match_score,
        "estimated_score": estimated_score,
        "missing_skills_summary": summary,
        "learning_plan": learning_plan,
        "resume_tips": resume_tips,
        "interview_tips": interview_tips,
        "career_recommendations": {
            "career_suitability": suitability,
            "recommended_roles": rec_roles,
            "recommended_technologies": rec_techs
        }
    }

def generate_advisor_pdf(rec: Dict) -> bytes:
    """
    Draw a clean, well-formatted PDF report from Advisor recommendations using PyMuPDF (fitz).
    Returns PDF content in bytes.
    """
    doc = fitz.open()
    page = doc.new_page() # standard width 595, height 842 (A4)
    
    # Margin settings
    left_margin = 50
    right_margin = 545
    top_margin = 50
    bottom_margin = 792
    
    y = top_margin
    
    def add_page_if_needed(current_y, size=50):
        nonlocal page, y
        if current_y > bottom_margin - size:
            page = doc.new_page()
            y = top_margin
            return True
        return False
        
    def draw_text_wrapped(text, start_x, start_y, font_size=10, font_name="helv", color=(0.1, 0.1, 0.1), is_bold=False):
        nonlocal page
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
        if font_name == "helv":
            font_style = "helvb" if is_bold else "helv"
        else:
            font_style = font_name
        
        for line in lines:
            add_page_if_needed(y_pos, font_size * 2)
            page.insert_text((start_x, y_pos), line, fontsize=font_size, fontname=font_style, color=color)
            y_pos += font_size * 1.45
            
        return y_pos
        
    # Title Header
    page.insert_text((left_margin, y), "AI RESUME ADVISOR REPORT", fontsize=18, fontname="helvb", color=(0.02, 0.35, 0.52))
    y += 26
    
    # Subtitle
    page.insert_text((left_margin, y), "Personalized Career Analysis and Skills Roadmap", fontsize=10, fontname="helvi", color=(0.4, 0.4, 0.4))
    y += 15
    
    # Divider line
    page.draw_line((left_margin, y), (right_margin, y), color=(0.02, 0.35, 0.52), width=1.5)
    y += 25
    
    # Section 1: Overview Summary
    page.insert_text((left_margin, y), "1. Analysis Overview", fontsize=12, fontname="helvb", color=(0.02, 0.35, 0.52))
    y += 18
    
    cur_score = rec.get("current_score", 0)
    est_score = rec.get("estimated_score", 0)
    
    y = draw_text_wrapped(f"Current Match Score: {cur_score}%", left_margin + 15, y, font_size=10, is_bold=True)
    y = draw_text_wrapped(f"Estimated Potential Score: {est_score}% (After implementing advice)", left_margin + 15, y, font_size=10, is_bold=True, color=(0.08, 0.6, 0.3))
    y += 5
    
    # Section 2: Missing Skills Summary
    add_page_if_needed(y, 60)
    page.insert_text((left_margin, y), "2. Skills Assessment", fontsize=12, fontname="helvb", color=(0.02, 0.35, 0.52))
    y += 18
    summary = rec.get("missing_skills_summary", "Assessments completed.")
    y = draw_text_wrapped(summary, left_margin + 15, y, font_size=10)
    y += 15
    
    # Section 3: Learning Roadmap
    add_page_if_needed(y, 60)
    page.insert_text((left_margin, y), "3. Week-by-Week Learning Roadmap", fontsize=12, fontname="helvb", color=(0.02, 0.35, 0.52))
    y += 18
    
    learning_plan = rec.get("learning_plan", [])
    if not learning_plan:
        y = draw_text_wrapped("No immediate learning tasks required.", left_margin + 15, y, font_size=10)
    else:
        for plan in learning_plan:
            duration = plan.get("duration", "Phase")
            y = draw_text_wrapped(f"- {duration}:", left_margin + 15, y, font_size=10, is_bold=True, color=(0.4, 0.2, 0.7))
            for task in plan.get("tasks", []):
                y = draw_text_wrapped(f"  • {task}", left_margin + 25, y, font_size=9.5)
            y += 5
    y += 10
    
    # Section 4: Resume Tips & Interview Preparation
    add_page_if_needed(y, 60)
    page.insert_text((left_margin, y), "4. Actionable Improvements & Interview Tips", fontsize=12, fontname="helvb", color=(0.02, 0.35, 0.52))
    y += 18
    
    # Resume Tips
    y = draw_text_wrapped("Resume Optimizations:", left_margin + 15, y, font_size=10.5, is_bold=True)
    resume_tips = rec.get("resume_tips", [])
    for tip in resume_tips:
        y = draw_text_wrapped(f"  - {tip}", left_margin + 20, y, font_size=9.5)
    y += 8
    
    # Interview Tips
    add_page_if_needed(y, 40)
    y = draw_text_wrapped("Interview Practice Focus:", left_margin + 15, y, font_size=10.5, is_bold=True)
    interview_tips = rec.get("interview_tips", [])
    for tip in interview_tips:
        y = draw_text_wrapped(f"  - {tip}", left_margin + 20, y, font_size=9.5)
    y += 15
    
    # Section 5: Career Recommendations
    add_page_if_needed(y, 60)
    page.insert_text((left_margin, y), "5. AI Career Insights", fontsize=12, fontname="helvb", color=(0.02, 0.35, 0.52))
    y += 18
    
    career = rec.get("career_recommendations", {})
    suitability = career.get("career_suitability", "Suitable for modern engineering tracks.")
    y = draw_text_wrapped(suitability, left_margin + 15, y, font_size=10)
    y += 5
    
    roles = career.get("recommended_roles", [])
    if roles:
        y = draw_text_wrapped(f"Recommended Roles: {', '.join(roles)}", left_margin + 15, y, font_size=10, is_bold=True)
        
    techs = career.get("recommended_technologies", [])
    if techs:
        y = draw_text_wrapped(f"Recommended Technologies: {', '.join(techs)}", left_margin + 15, y, font_size=10, is_bold=True, color=(0.02, 0.35, 0.52))
        
    return doc.write()
