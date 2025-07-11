import React from 'react';

interface CoachIconProps {
  className?: string;
  size?: number;
}

export function CoachIcon({ className = "", size = 24 }: CoachIconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      {/* Head - larger and more prominent */}
      <circle cx="12" cy="8" r="4" fill="currentColor" stroke="none" />
      {/* Shoulders - wide and curved */}
      <path d="M6 16 C6 12, 8 12, 12 12 C16 12, 18 12, 18 16 C18 18, 16 20, 12 20 C8 20, 6 18, 6 16" fill="currentColor" stroke="none" />
    </svg>
  );
}