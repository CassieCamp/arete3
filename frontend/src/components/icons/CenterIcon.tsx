import React from 'react';

interface CenterIconProps {
  className?: string;
}

export const CenterIcon: React.FC<CenterIconProps> = ({ className = "w-12 h-12 text-muted-foreground" }) => {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      {/* Center dot (stone) */}
      <circle cx="12" cy="12" r="1" fill="currentColor" />
      
      {/* First ripple */}
      <circle cx="12" cy="12" r="4" />
      
      {/* Second ripple */}
      <circle cx="12" cy="12" r="7" />
      
      {/* Third ripple */}
      <circle cx="12" cy="12" r="10" />
    </svg>
  );
};