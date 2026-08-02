import { useState } from 'react';
import { analyzeResume } from '../services/api';
import ScoreGauge from '../components/ScoreGauge';

export default function StudentPage() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jdText, setJdText] = useState('');
  const [roleHint, setRoleHint] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const canSubmit = resumeFile && jdText.trim().length > 20 && !loading;

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeResume({ resumeFile, jdText, roleHint });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <span className="page-eyebrow">Student Portal</span>
        <h1 className="page-title">See your resume the way a recruiter does</h1>
        <p className="page-subtitle">
          Upload your resume and paste the job description. Get a score out of 10 and
          a specific, step-by-step plan to close the gap — before you hit apply.
        </p>
      </div>

      <div className="panel">
        <form className="form-grid" onSubmit={handleSubmit}>
          <div>
            <label className="field-label">Your resume<span className="field-hint">PDF, DOCX or TXT</span></label>
            <label className="file-drop" htmlFor="resume-upload">
              <span className="file-drop-title">
                {resumeFile ? resumeFile.name : 'Click to choose a file'}
              </span>
              <span className="file-drop-sub">or drag it here</span>
            </label>
            <input
              id="resume-upload"
              type="file"
              accept=".pdf,.docx,.txt"
              style={{ display: 'none' }}
              onChange={(e) => setResumeFile(e.target.files[0] || null)}
            />
          </div>

          <div>
            <label className="field-label">Role you're applying for<span className="field-hint">optional, helps tailor feedback</span></label>
            <input
              type="text"
              placeholder="e.g. Business Analyst, MIS Executive"
              value={roleHint}
              onChange={(e) => setRoleHint(e.target.value)}
            />
          </div>

          <div>
            <label className="field-label">Job description</label>
            <textarea
              rows={8}
              placeholder="Paste the full job description here..."
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
            />
          </div>

          {error && <div className="error-banner">{error}</div>}

          <button className="submit-btn" type="submit" disabled={!canSubmit}>
            {loading ? 'Analyzing...' : 'Score my resume'}
          </button>
          {loading && <span className="loading-text">Extracting skills and generating personalized feedback — this can take a few seconds.</span>}
        </form>
      </div>

      {result && (
        <div className="results-grid">
          <div className="result-panel">
            <ScoreGauge breakdown={result.breakdown} totalScore={result.total_score} />
          </div>

          <div className="panel">
            <div className="feedback-summary">{result.feedback_summary}</div>

            <div className="section-title">Matched skills ({result.matched_skills.length})</div>
            <div className="skill-chips">
              {result.matched_skills.length === 0 && <span className="loading-text">None detected</span>}
              {result.matched_skills.map((s) => (
                <span className="chip matched" key={s}>{s}</span>
              ))}
            </div>

            <div className="section-title">Missing skills ({result.missing_skills.length})</div>
            <div className="skill-chips">
              {result.missing_skills.length === 0 && <span className="loading-text">None — great match!</span>}
              {result.missing_skills.map((s) => (
                <span className="chip missing" key={s}>{s}</span>
              ))}
            </div>

            <div className="section-title">Step-by-step improvement plan</div>
            <div className="feedback-steps">
              {result.feedback_steps.map((step, i) => (
                <div className="feedback-step" key={i}>
                  <span className="step-number">{String(i + 1).padStart(2, '0')}</span>
                  <div>
                    <div className="step-title">{step.title}</div>
                    <div className="step-detail">{step.detail}</div>
                  </div>
                </div>
              ))}
            </div>

            {result.quality_issues.length > 0 && (
              <div className="quality-issues">
                <div className="section-title">Formatting / ATS notes</div>
                {result.quality_issues.map((issue, i) => (
                  <div className="quality-issue" key={i}>{issue}</div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
