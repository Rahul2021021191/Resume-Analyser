import { useState } from 'react';
import { rankCandidates } from '../services/api';

export default function RecruiterPage() {
  const [resumeFiles, setResumeFiles] = useState([]);
  const [jdText, setJdText] = useState('');
  const [roleHint, setRoleHint] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const canSubmit = resumeFiles.length > 0 && jdText.trim().length > 20 && !loading;

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await rankCandidates({ resumeFiles, jdText, roleHint });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function getAtsReadiness(candidate) {
    if (candidate.ats_readiness !== undefined) {
      return candidate.ats_readiness;
    }

    const skills = candidate.breakdown.skills_match / 4;
    const quality = candidate.breakdown.resume_quality / 2;
    return Math.round((skills * 60) + (quality * 40));
  }

  return (
    <div className="page">
      <div className="page-header">
        <span className="page-eyebrow">Recruiter Portal</span>
        <h1 className="page-title">Rank every candidate against the JD in seconds</h1>
        <p className="page-subtitle">
          Candidates are ranked using skills, experience, education, and ATS readiness.
        </p>
      </div>

      <div className="panel">
        <form className="form-grid" onSubmit={handleSubmit}>
          <div>
            <label className="field-label">
              Candidate resumes
              <span className="field-hint">select multiple files</span>
            </label>

            <label className="file-drop" htmlFor="resumes-upload">
              <span className="file-drop-title">
                {resumeFiles.length > 0
                  ? `${resumeFiles.length} file(s) selected`
                  : 'Click to choose files'}
              </span>
              <span className="file-drop-sub">PDF, DOCX or TXT — drag multiple here</span>
            </label>

            <input
              id="resumes-upload"
              type="file"
              accept=".pdf,.docx,.txt"
              multiple
              style={{ display: 'none' }}
              onChange={(e) => setResumeFiles(Array.from(e.target.files || []))}
            />

            {resumeFiles.length > 0 && (
              <div className="file-list">
                {resumeFiles.map((file) => (
                  <span className="file-chip" key={file.name}>
                    {file.name}
                  </span>
                ))}
              </div>
            )}
          </div>

          <div>
            <label className="field-label">
              Role title
              <span className="field-hint">optional</span>
            </label>

            <input
              type="text"
              placeholder="e.g. Data Analyst"
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
            {loading ? 'Ranking...' : 'Rank candidates'}
          </button>

          {loading && (
            <span className="loading-text">
              Parsing and scoring each resume — larger batches take a bit longer.
            </span>
          )}
        </form>
      </div>

      {result && (
        <div className="panel" style={{ marginTop: 32, overflowX: 'auto' }}>
          <div className="section-title">
            Ranked candidates ({result.candidates.length})
          </div>

          <table className="rank-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Candidate file</th>
                <th>Overall</th>
                <th>Skills</th>
                <th>Experience</th>
                <th>Education</th>
                <th>ATS readiness</th>
                <th>Matched skills</th>
                <th>Missing skills</th>
              </tr>
            </thead>

            <tbody>
              {result.candidates.map((candidate, index) => (
                <tr key={candidate.filename}>
                  <td className={`rank-position ${index === 0 ? 'top' : ''}`}>
                    {index + 1}
                  </td>

                  <td className="rank-filename">{candidate.filename}</td>
                  <td className="rank-score">{candidate.total_score}/10</td>
                  <td>{candidate.breakdown.skills_match}/4</td>
                  <td>{candidate.breakdown.experience_relevance}/2</td>
                  <td>{candidate.breakdown.education_match}/2</td>
                  <td>{getAtsReadiness(candidate)}%</td>

                  <td>
                    <div className="skill-chips">
                      {candidate.matched_skills.slice(0, 6).map((skill) => (
                        <span className="chip matched" key={skill}>
                          {skill}
                        </span>
                      ))}
                    </div>
                  </td>

                  <td>
                    <div className="skill-chips">
                      {candidate.missing_skills.slice(0, 6).map((skill) => (
                        <span className="chip missing" key={skill}>
                          {skill}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}