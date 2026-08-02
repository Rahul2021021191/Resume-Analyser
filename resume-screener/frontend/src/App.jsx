import { useState } from 'react';
import StudentPage from './pages/StudentPage';
import RecruiterPage from './pages/RecruiterPage';
import './App.css';

export default function App() {
  const [tab, setTab] = useState('student');

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">ResumeMatch</span>
          <span className="brand-tag">SCORE · RANK · IMPROVE</span>
        </div>
        <div className="tab-switch">
          <button
            className={`tab-btn ${tab === 'student' ? 'active' : ''}`}
            onClick={() => setTab('student')}
          >
            Student
          </button>
          <button
            className={`tab-btn ${tab === 'recruiter' ? 'active' : ''}`}
            onClick={() => setTab('recruiter')}
          >
            Recruiter
          </button>
        </div>
      </header>

      {tab === 'student' ? <StudentPage /> : <RecruiterPage />}
    </div>
  );
}
