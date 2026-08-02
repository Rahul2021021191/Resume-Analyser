const API_BASE = 'http://localhost:8000';

export async function analyzeResume({ resumeFile, jdText, roleHint }) {
  const formData = new FormData();
  formData.append('resume', resumeFile);
  formData.append('jd_text', jdText);
  if (roleHint) formData.append('role_hint', roleHint);

  const res = await fetch(`${API_BASE}/api/student/analyze`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to analyze resume');
  }
  return res.json();
}

export async function rankCandidates({ resumeFiles, jdText, roleHint }) {
  const formData = new FormData();
  resumeFiles.forEach((file) => formData.append('resumes', file));
  formData.append('jd_text', jdText);
  if (roleHint) formData.append('role_hint', roleHint);

  const res = await fetch(`${API_BASE}/api/recruiter/rank`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to rank candidates');
  }
  return res.json();
}
