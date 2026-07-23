export function MetricasIcon({ className, ...props }) {
  return (
    <svg width="24" height="24" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg" className={className} {...props}>
      <rect x="4" y="4" width="42" height="42" rx="4" ry="4" stroke="currentColor" strokeWidth="1.5" fill="none" />
      <g>
        <path d="M 10 10 L 13 7 L 16 10" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
        <rect x="10" y="10" width="6" height="6" stroke="currentColor" strokeWidth="1.5" fill="none" />
        <rect x="11.5" y="12" width="1.5" height="2.5" fill="currentColor" />
      </g>
      <g>
        <line x1="18" y1="32" x2="38" y2="32" stroke="currentColor" strokeWidth="1.2" />
        <line x1="18" y1="18" x2="18" y2="32" stroke="currentColor" strokeWidth="1.2" />
        <rect x="21" y="28" width="2.5" height="4" fill="currentColor" />
        <rect x="25.5" y="24" width="2.5" height="8" fill="currentColor" />
        <rect x="30" y="20" width="2.5" height="12" fill="currentColor" />
        <rect x="34.5" y="18" width="2.5" height="14" fill="currentColor" />
      </g>
      <line x1="19" y1="36" x2="30" y2="36" stroke="currentColor" strokeWidth="1" />
      <line x1="19" y1="39" x2="26" y2="39" stroke="currentColor" strokeWidth="1" />
      <g>
        <circle cx="39" cy="39" r="5" stroke="currentColor" strokeWidth="1.2" fill="none" />
        <circle cx="39" cy="39" r="3" stroke="currentColor" strokeWidth="1" fill="none" />
        <circle cx="39" cy="39" r="1.2" fill="currentColor" />
        <g>
          <line x1="41.5" y1="34.5" x2="43" y2="32" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
          <path d="M 43 32 L 42.2 33 L 43.2 33.5" fill="currentColor" stroke="currentColor" strokeWidth="0.8" strokeLinejoin="round" />
        </g>
      </g>
    </svg>
  );
}
