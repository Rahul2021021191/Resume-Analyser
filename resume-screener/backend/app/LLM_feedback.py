import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY is missing from backend/.env")

client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """
You are an expert ATS resume coach. Give specific, actionable feedback based only
on the supplied resume score, skills, experience, and quality issues. Prioritize
the highest-impact changes and explain exactly how to improve each issue.
"""

FEEDBACK_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "detail": {"type": "string"},
                },
                "required": ["title", "detail"],
            },
        },
    },
    "required": ["summary", "steps"],
}


def fallback_feedback(score_data: dict) -> dict:
    matched = ", ".join(score_data["matched_skills"]) or "no matching skills detected"
    missing = ", ".join(score_data["missing_skills"]) or "no critical skills detected"
    issues = score_data["quality_issues"]

    keyword_score = score_data["breakdown"]["skills_match"] / 4
    quality_score = score_data["breakdown"]["resume_quality"] / 2
    ats_readiness = round(keyword_score * 60 + quality_score * 40)

    return {
        "summary": (
            f"Job-match score: {score_data['total_score']}/10. "
            f"Estimated ATS readiness: {ats_readiness}/100. "
            "The ATS estimate is based on keyword coverage and resume-quality checks."
        ),
        "steps": [
            {
                "title": "Close the keyword gap",
                "detail": (
                    f"Your resume matches: {matched}. Add proof of these missing skills: "
                    f"{missing}. Include them naturally in Skills, Projects, and Experience."
                ),
            },
            {
                "title": "Add measurable achievements",
                "detail": (
                    "Rewrite bullets as: Action + tool/skill + result. Example: "
                    "'Created a Power BI dashboard that reduced reporting time by 30%.'"
                ),
            },
            {
                "title": "Strengthen relevant experience",
                "detail": (
                    f"The role requests about {score_data['jd_years_required']} years, while "
                    f"your resume shows {score_data['resume_years_experience']} years. Highlight "
                    "internships, freelance work, projects, and responsibilities relevant to this role."
                ),
            },
            {
                "title": "Improve ATS formatting",
                "detail": (
                    "Use standard headings: Summary, Skills, Experience, Projects, Education, "
                    "and Certifications. Avoid tables, columns, icons, graphics, and text boxes."
                ),
            },
            {
                "title": "Add a targeted summary",
                "detail": (
                    "Add a 2–3 line summary with the target job title, key relevant skills, "
                    "and one measurable achievement."
                ),
            },
            {
                "title": "Fix detected quality issues",
                "detail": " | ".join(issues) if issues else (
                    "No major quality issues were detected. Focus on tailoring your keywords "
                    "and quantified achievements."
                ),
            },
        ],
    }


def generate_feedback(score_data: dict, jd_role_hint: str = "") -> dict:
    prompt = f"""Role: {jd_role_hint or "Not specified"}

Score: {score_data["total_score"]}/10
Skills match: {score_data["breakdown"]["skills_match"]}/4
Experience relevance: {score_data["breakdown"]["experience_relevance"]}/2
Education match: {score_data["breakdown"]["education_match"]}/2
Resume quality: {score_data["breakdown"]["resume_quality"]}/2

Matched skills: {", ".join(score_data["matched_skills"]) or "None"}
Missing skills: {", ".join(score_data["missing_skills"]) or "None"}
Resume experience: {score_data["resume_years_experience"]} years
Required experience: {score_data["jd_years_required"]} years
Quality issues: {", ".join(score_data["quality_issues"]) or "None"}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_json_schema=FEEDBACK_SCHEMA,
                max_output_tokens=1000,
            ),
        )

        if response.parsed:
            return response.parsed

        return json.loads(response.text)

    except Exception:
        return fallback_feedback(score_data)