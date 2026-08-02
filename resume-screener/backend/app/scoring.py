"""
Computes the explainable 0-10 resume-vs-JD score.

Breakdown (mirrors what's shown to the student):
  - Skills Match          : 0-4 pts
  - Experience Relevance  : 0-2 pts
  - Education/Cert Match  : 0-2 pts
  - Resume Quality (ATS)  : 0-2 pts

Keeping this deterministic (no LLM here) means the number can always be
explained and reproduced - important for a viva. The LLM is only used later
to turn the gaps this module finds into natural-language coaching text.
"""
import re
from sentence_transformers import SentenceTransformer, util
from app.ner import extract_entities

_model = SentenceTransformer("all-MiniLM-L6-v2")


def semantic_similarity(text_a: str, text_b: str) -> float:
    emb_a = _model.encode(text_a, convert_to_tensor=True)
    emb_b = _model.encode(text_b, convert_to_tensor=True)
    return float(util.cos_sim(emb_a, emb_b).item())  # -1..1


def score_skills(resume_skills: set, jd_skills: set) -> tuple[float, set, set]:
    """Returns (points out of 4, matched skills, missing skills)."""
    if not jd_skills:
        return 4.0, resume_skills, set()
    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills
    ratio = len(matched) / len(jd_skills)
    return round(ratio * 4, 2), matched, missing


def score_experience(resume_years: float, jd_years_required: float) -> float:
    """Returns points out of 2."""
    if jd_years_required <= 0:
        return 2.0
    if resume_years >= jd_years_required:
        return 2.0
    ratio = resume_years / jd_years_required
    return round(ratio * 2, 2)


def score_education(resume_edu: set, jd_edu: set) -> float:
    """Returns points out of 2."""
    if not jd_edu:
        return 2.0
    return 2.0 if resume_edu & jd_edu else 0.5


def score_resume_quality(resume_text: str) -> tuple[float, list]:
    """
    Cheap heuristic ATS-friendliness check, out of 2 points.
    Flags issues so they can be surfaced to the student.
    """
    issues = []
    points = 2.0

    word_count = len(resume_text.split())
    if word_count < 150:
        issues.append("Resume looks very short - add more detail on projects/experience.")
        points -= 0.5

    if not re.search(r"\b\d+%|\b\d+x\b|\bincreased|\breduced|\bimproved", resume_text.lower()):
        issues.append("No quantified achievements found (e.g. 'reduced X by 30%'). Add measurable impact.")
        points -= 0.5

    if not re.search(r"project", resume_text.lower()):
        issues.append("No 'Projects' section detected - consider adding one.")
        points -= 0.5

    if not re.search(r"certificat", resume_text.lower()):
        issues.append("No certifications mentioned - add relevant ones if you have them.")
        points -= 0.25

    return max(points, 0), issues


def compute_score(resume_text: str, jd_text: str) -> dict:
    resume_entities = extract_entities(resume_text)
    jd_entities = extract_entities(jd_text)

    skills_pts, matched_skills, missing_skills = score_skills(
        resume_entities["skills"], jd_entities["skills"]
    )
    exp_pts = score_experience(
        resume_entities["years_experience"], jd_entities["years_experience"]
    )
    edu_pts = score_education(resume_entities["education"], jd_entities["education"])
    quality_pts, quality_issues = score_resume_quality(resume_text)

    total = round(skills_pts + exp_pts + edu_pts + quality_pts, 2)

    return {
        "total_score": total,
        "ats_readiness": round(
            ((skills_pts / 4) * 60 + (quality_pts / 2) * 40), 2
        ),
        "breakdown": {
            "skills_match": skills_pts,
            "experience_relevance": exp_pts,
            "education_match": edu_pts,
            "resume_quality": quality_pts,
        },
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "resume_years_experience": resume_entities["years_experience"],
        "jd_years_required": jd_entities["years_experience"],
        "quality_issues": quality_issues,
        "semantic_similarity": round(semantic_similarity(resume_text, jd_text), 3),
    }
