import React from 'react';

export const KeyIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    {/* Key shaft */}
    <path d="M12 8v12" />
    {/* Key head - decorative circles */}
    <circle cx="10" cy="6" r="2" />
    <circle cx="14" cy="6" r="2" />
    <circle cx="12" cy="4" r="2" />
    {/* Key teeth */}
    <path d="M16 16h2" />
    <path d="M16 18h3" />
    {/* Small dot at bottom */}
    <circle cx="12" cy="21" r="0.5" fill="currentColor" />
  </svg>
);