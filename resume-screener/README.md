# ResumeMatch — Resume Screening & Ranking Platform

A two-portal web app:
- **Student Portal** — upload your resume + a JD, get a score out of 10 and a
  step-by-step improvement plan.
- **Recruiter Portal** — upload a JD + many resumes, get candidates ranked
  highest-match-first.

## Architecture

```
Resume/JD text
      │
      ▼
┌─────────────────┐     ┌──────────────────────┐
│  Parsing        │────▶│  Entity Extraction    │  spaCy PhraseMatcher
│  (pdfplumber/   │     │  (skills, years exp,  │  + regex rules
│   python-docx)  │     │   education)          │
└─────────────────┘     └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │  Deterministic Scoring│  sentence-transformers
                         │  (0-10, 4 sub-scores) │  cosine similarity +
                         └──────────┬───────────┘  rule-based sub-scores
                                    ▼
                         ┌──────────────────────┐
                         │  Claude API           │  turns score + gaps into
                         │  (feedback generation)│  natural-language coaching
                         └──────────────────────┘
```

**Why the score and the feedback are generated separately:** the 0–10 score is
100% deterministic (spaCy + sentence-transformers + rules), so it's always
reproducible and defensible in a viva ("here's exactly why you got 6.5, run it
again and you get the same number"). The Claude API is only used to turn that
structured breakdown into natural, specific coaching text — which is something
rule-based templates are bad at, but LLMs are good at.

## Project structure

```
resume-screener/
├── backend/
│   ├── app/
│   │   ├── main.py            FastAPI app + endpoints
│   │   ├── parser.py          PDF/DOCX/TXT text extraction
│   │   ├── ner.py             Skill/education/experience extraction
│   │   ├── scoring.py         Deterministic 0-10 scoring logic
│   │   ├── claude_feedback.py Claude API call for coaching text
│   │   └── models.py          Pydantic response schemas
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── pages/StudentPage.jsx
    │   ├── pages/RecruiterPage.jsx
    │   ├── components/ScoreGauge.jsx   segmented score meter (signature UI)
    │   ├── services/api.js
    │   └── App.jsx
    └── package.json
```

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

cp .env.example .env
# edit .env and add your ANTHROPIC_API_KEY

uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`. Interactive API docs at
`http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

## Extending this for a stronger evaluation

1. **Swap rule-based NER for a fine-tuned spaCy NER model** trained on a
   labeled resume dataset (public ones exist on HuggingFace/Kaggle) — the
   `extract_entities()` function in `ner.py` is the single integration point,
   so nothing else needs to change.
2. **Add a SQLite/Postgres layer** to store past analyses so the recruiter
   portal can show a candidate database over time, not just one-off batches.
3. **Add authentication** (student vs recruiter login) if the evaluators want
   to see role-based access control.
4. **Test on real data**: run your own resume against real JDs from your job
   tracker for a live, believable demo instead of synthetic data.

## Notes on the skills gazetteer

`ner.py` uses a curated list of ~60 common skills. Extend `SKILLS` in that
file for your domain (e.g. add more data-analytics or marketing-specific
terms) — no retraining needed, it's just a list.
