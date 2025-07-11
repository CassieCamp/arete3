import React from 'react';

interface CaveIconProps {
  className?: string;
  size?: number;
}

export function CaveIcon({ className = "", size = 24 }: CaveIconProps) {
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
      {/* Cave/shelter arc - wider curved line matching Journey icon stroke width */}
      <path d="M2 21 C2 9, 6 2, 12 2 C18 2, 22 9, 22 21" fill="none" />
      {/* Person represented as a larger filled circle, off-center but not touching edge */}
      <circle cx="15" cy="15" r="4" fill="currentColor" stroke="none" />
    </svg>
  );
}