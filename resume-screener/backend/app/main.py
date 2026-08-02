from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from app.parser import extract_text, clean_text
from app.scoring import compute_score
from app.LLM_feedback import generate_feedback
from app.models import StudentAnalyzeResponse, RecruiterRankResponse, RankedCandidate

app = FastAPI(title="Resume Screening & Ranking API")

# Allow the React dev server to call this API. Tighten this before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _read_and_clean(upload: UploadFile) -> str:
    raw_bytes = await upload.read()
    try:
        text = extract_text(upload.filename, raw_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return clean_text(text)


@app.post("/api/student/analyze", response_model=StudentAnalyzeResponse)
async def student_analyze(
    resume: UploadFile = File(...),
    jd_text: str = Form(...),
    role_hint: Optional[str] = Form(None),
):
    """
    Student flow: upload one resume + paste JD text.
    Returns score out of 10 + step-by-step improvement feedback.
    """
    resume_text = await _read_and_clean(resume)
    score_data = compute_score(resume_text, jd_text)
    feedback = generate_feedback(score_data, jd_role_hint=role_hint or "")

    return StudentAnalyzeResponse(
        total_score=score_data["total_score"],
        breakdown=score_data["breakdown"],
        matched_skills=score_data["matched_skills"],
        missing_skills=score_data["missing_skills"],
        resume_years_experience=score_data["resume_years_experience"],
        jd_years_required=score_data["jd_years_required"],
        quality_issues=score_data["quality_issues"],
        semantic_similarity=score_data["semantic_similarity"],
        feedback_summary=feedback["summary"],
        feedback_steps=feedback["steps"],
    )


@app.post("/api/recruiter/rank", response_model=RecruiterRankResponse)
async def recruiter_rank(
    resumes: List[UploadFile] = File(...),
    jd_text: str = Form(...),
    role_hint: Optional[str] = Form(None),
):
    """
    Recruiter flow: upload JD + many resumes.
    Returns candidates ranked by score, highest first.
    """
    candidates = []
    for resume in resumes:
        resume_text = await _read_and_clean(resume)
        score_data = compute_score(resume_text, jd_text)
        candidates.append(
            RankedCandidate(
                ats_readiness=score_data["ats_readiness"],
                filename=resume.filename,
                total_score=score_data["total_score"],
                breakdown=score_data["breakdown"],
                matched_skills=score_data["matched_skills"],
                missing_skills=score_data["missing_skills"],
            )
        )

    candidates.sort(key=lambda c: c.total_score, reverse=True)
    return RecruiterRankResponse(jd_role_hint=role_hint, candidates=candidates)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
