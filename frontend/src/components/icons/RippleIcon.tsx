import React from 'react';

interface RippleIconProps {
  className?: string;
}

export const RippleIcon: React.FC<RippleIconProps> = ({ className = "w-6 h-6" }) => {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
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