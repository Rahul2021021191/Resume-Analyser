import './ScoreGauge.css';

// Each segment's max points, matched to the backend's breakdown scale.
const SEGMENTS = [
  { key: 'skills_match', label: 'Skills', max: 4, color: 'var(--accent)' },
  { key: 'experience_relevance', label: 'Experience', max: 2, color: '#3E8E6B' },
  { key: 'education_match', label: 'Education', max: 2, color: '#6BAE8F' },
  { key: 'resume_quality', label: 'Resume Quality', max: 2, color: '#98CBB0' },
];

const RADIUS = 80;
const STROKE = 14;
const CIRC = 2 * Math.PI * RADIUS;
const GAP_DEG = 3; // small visual gap between segments

export default function ScoreGauge({ breakdown, totalScore }) {
  let cursor = 0; // degrees, starting at top (-90deg offset handled in transform)

  return (
    <div className="gauge-wrap">
      <svg viewBox="0 0 200 200" className="gauge-svg">
        <circle cx="100" cy="100" r={RADIUS} className="gauge-track" strokeWidth={STROKE} />
        {SEGMENTS.map((seg) => {
          const value = breakdown[seg.key] ?? 0;
          const fraction = Math.max(value, 0) / 10; // relative to total 10-point scale
          const segDeg = fraction * 360;
          const dashLength = (segDeg / 360) * CIRC - GAP_DEG;
          const dashOffset = -((cursor / 360) * CIRC);
          const rotation = cursor;
          cursor += segDeg;

          return (
            <circle
              key={seg.key}
              cx="100"
              cy="100"
              r={RADIUS}
              strokeWidth={STROKE}
              stroke={seg.color}
              strokeDasharray={`${Math.max(dashLength, 0)} ${CIRC}`}
              strokeDashoffset={dashOffset}
              strokeLinecap="round"
              className="gauge-segment"
              style={{ transform: `rotate(${rotation - 90}deg)`, transformOrigin: '100px 100px' }}
            />
          );
        })}
      </svg>
      <div className="gauge-center">
        <span className="gauge-score">{totalScore}</span>
        <span className="gauge-outof">/ 10</span>
      </div>
      <div className="gauge-legend">
        {SEGMENTS.map((seg) => (
          <div className="gauge-legend-item" key={seg.key}>
            <span className="legend-dot" style={{ background: seg.color }} />
            <span className="legend-label">{seg.label}</span>
            <span className="legend-value">{breakdown[seg.key]}/{seg.max}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
