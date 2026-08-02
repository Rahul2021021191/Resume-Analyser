from pydantic import BaseModel
from typing import List, Optional


class ScoreBreakdown(BaseModel):
    skills_match: float
    experience_relevance: float
    education_match: float
    resume_quality: float


class FeedbackStep(BaseModel):
    title: str
    detail: str


class StudentAnalyzeResponse(BaseModel):
    total_score: float
    breakdown: ScoreBreakdown
    matched_skills: List[str]
    missing_skills: List[str]
    resume_years_experience: float
    jd_years_required: float
    quality_issues: List[str]
    semantic_similarity: float
    feedback_summary: str
    feedback_steps: List[FeedbackStep]


class RankedCandidate(BaseModel):
    filename: str
    total_score: float
    breakdown: ScoreBreakdown
    matched_skills: List[str]
    missing_skills: List[str]
    ats_readiness: float


class RecruiterRankResponse(BaseModel):
    jd_role_hint: Optional[str] = None
    candidates: List[RankedCandidate]
