"""
Entity extraction from resume/JD text.

Approach: spaCy PhraseMatcher against a curated skills gazetteer (fast, no
training data needed) + regex rules for years-of-experience and education
degree detection. This is the "rule-based NER" route - solid for a minor
project and easy to explain/defend in a viva.

To make this a stronger technical project, this can later be swapped for a
fine-tuned spaCy NER model trained on a labeled resume dataset - the
extract_entities() function is the single integration point, so the rest of
the app doesn't need to change.
"""
import re
import spacy
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")

# Curated skill gazetteer - extend this list as needed for your domain.
SKILLS = [
    "python", "java", "c++", "c", "javascript", "typescript", "sql", "nosql",
    "html", "css", "react", "node.js", "django", "flask", "fastapi",
    "power bi", "dax", "power query", "excel", "tableau", "looker",
    "machine learning", "deep learning", "nlp", "computer vision",
    "pytorch", "tensorflow", "keras", "scikit-learn", "pandas", "numpy",
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "github",
    "data analysis", "data visualization", "data cleaning", "etl",
    "spark", "hadoop", "airflow", "mongodb", "postgresql", "mysql",
    "rest api", "graphql", "linux", "bash", "communication", "leadership",
    "project management", "google ads", "meta ads", "seo", "sem",
    "digital marketing", "google analytics", "ga4", "figma",
]

DEGREE_PATTERNS = [
    r"\bb\.?tech\b", r"\bm\.?tech\b", r"\bbca\b", r"\bmca\b", r"\bb\.?sc\b",
    r"\bm\.?sc\b", r"\bmba\b", r"\bbba\b", r"\bphd\b", r"\bbachelor'?s?\b",
    r"\bmaster'?s?\b", r"\bdiploma\b",
]

_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
_matcher.add("SKILL", [nlp.make_doc(skill) for skill in SKILLS])


def extract_skills(text: str) -> set:
    doc = nlp(text)
    matches = _matcher(doc)
    found = set()
    for match_id, start, end in matches:
        span = doc[start:end]
        found.add(span.text.lower())
    return found


def extract_years_experience(text: str) -> float:
    """Look for patterns like '2 years', '3+ years of experience'."""
    matches = re.findall(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)\b", text.lower())
    if not matches:
        return 0.0
    return max(float(m) for m in matches)


def extract_education(text: str) -> set:
    found = set()
    lower = text.lower()
    for pattern in DEGREE_PATTERNS:
        if re.search(pattern, lower):
            found.add(pattern.strip("\\b").replace("\\.?", "."))
    return found


def extract_entities(text: str) -> dict:
    """Single entry point used by the rest of the app."""
    return {
        "skills": extract_skills(text),
        "years_experience": extract_years_experience(text),
        "education": extract_education(text),
    }
