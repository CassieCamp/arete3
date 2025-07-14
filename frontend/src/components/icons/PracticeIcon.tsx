import React from 'react';

interface PracticeIconProps {
  className?: string;
  size?: number;
}

export function PracticeIcon({ className = "", size = 24 }: PracticeIconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      {/* Large square - top left */}
      <rect x="3" y="3" width="8" height="8" fill="currentColor" stroke="none" />
      
      {/* Medium square - top right */}
      <rect x="14" y="3" width="6" height="6" fill="currentColor" stroke="none" />
      
      {/* Small square - bottom left */}
      <rect x="3" y="16" width="4" height="4" fill="currentColor" stroke="none" />
      
      {/* Medium-small square - bottom right */}
      <rect x="13" y="14" width="7" height="7" fill="currentColor" stroke="none" />
    </svg>
  );
}