import React, { useEffect, useState } from 'react';

const MeanderingPathway: React.FC = () => {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    let ticking = false;

    const handleScroll = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          setScrollY(window.scrollY);
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Calculate transform based on scroll position
  // The pathway moves upward as user scrolls down, creating travel illusion
  const pathwayTransform = `translateY(${scrollY * 0.3}px)`;
  return (
    <div className="fixed inset-0 w-full h-full overflow-hidden pointer-events-none z-0">
      {/* Dark background overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 opacity-95" />
      
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 400 900"
        preserveAspectRatio="xMidYMid slice"
        className="absolute inset-0"
      >
        <defs>
          {/* Off-white brushstroke gradient */}
          <linearGradient id="brushstrokeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="oklch(0.96 0.015 60)" stopOpacity="0.85" />
            <stop offset="30%" stopColor="oklch(0.94 0.02 55)" stopOpacity="0.9" />
            <stop offset="70%" stopColor="oklch(0.92 0.025 50)" stopOpacity="0.9" />
            <stop offset="100%" stopColor="oklch(0.89 0.03 45)" stopOpacity="0.85" />
          </linearGradient>

          {/* Brushstroke texture pattern */}
          <pattern id="brushTexture" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
            <rect width="20" height="20" fill="none"/>
            <path d="M0,10 Q5,8 10,10 T20,10" stroke="oklch(0.98 0.01 50)" strokeWidth="0.5" opacity="0.3" fill="none"/>
            <path d="M0,15 Q7,13 14,15 T20,15" stroke="oklch(0.96 0.015 55)" strokeWidth="0.3" opacity="0.2" fill="none"/>
          </pattern>

          {/* Soft glow filter for brushstroke */}
          <filter id="brushGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
            <feMerge> 
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>

          {/* Inner texture filter */}
          <filter id="brushTexture" x="-20%" y="-20%" width="140%" height="140%">
            <feTurbulence baseFrequency="0.9" numOctaves="4" result="noise"/>
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="2"/>
          </filter>
        </defs>

        {/* Main brushstroke pathway - wide and organic like "The Way" */}
        <path
          d="M 200 -50 
             Q 170 10 150 70
             Q 130 130 170 190
             Q 210 250 150 310
             Q 90 370 130 430
             Q 170 490 210 550
             Q 250 610 190 670
             Q 130 730 170 790
             Q 210 850 190 910"
          fill="none"
          stroke="url(#brushstrokeGradient)"
          strokeWidth="80"
          strokeLinecap="round"
          strokeLinejoin="round"
          filter="url(#brushGlow)"
          className="opacity-75"
        />

        {/* Secondary brushstroke layer for texture */}
        <path
          d="M 200 -50 
             Q 175 15 155 75
             Q 135 135 175 195
             Q 215 255 155 315
             Q 95 375 135 435
             Q 175 495 215 555
             Q 255 615 195 675
             Q 135 735 175 795
             Q 215 855 195 915"
          fill="none"
          stroke="url(#brushTexture)"
          strokeWidth="70"
          strokeLinecap="round"
          strokeLinejoin="round"
          filter="url(#brushTexture)"
          className="opacity-60"
        />

        {/* Inner highlight brushstroke */}
        <path
          d="M 200 -50 
             Q 180 20 160 80
             Q 140 140 180 200
             Q 220 260 160 320
             Q 100 380 140 440
             Q 180 500 220 560
             Q 260 620 200 680
             Q 140 740 180 800
             Q 220 860 200 920"
          fill="none"
          stroke="oklch(0.98 0.005 50)"
          strokeWidth="35"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="opacity-50"
        />

        {/* Organic brushstroke edges - left side */}
        <path
          d="M 200 -50 
             Q 170 10 150 70
             Q 130 130 170 190
             Q 210 250 150 310
             Q 90 370 130 430
             Q 170 490 210 550
             Q 250 610 190 670
             Q 130 730 170 790
             Q 210 850 190 910"
          fill="none"
          stroke="oklch(0.99 0.005 50)"
          strokeWidth="12"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="opacity-40"
          transform="translate(-25, 0)"
        />

        {/* Organic brushstroke edges - right side */}
        <path
          d="M 200 -50 
             Q 170 10 150 70
             Q 130 130 170 190
             Q 210 250 150 310
             Q 90 370 130 430
             Q 170 490 210 550
             Q 250 610 190 670
             Q 130 730 170 790
             Q 210 850 190 910"
          fill="none"
          stroke="oklch(0.99 0.005 50)"
          strokeWidth="8"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="opacity-35"
          transform="translate(30, 0)"
        />

        {/* Scroll-responsive flowing elements along the brushstroke */}
        <g
          className="animate-pulse"
          style={{
            animationDuration: '5s',
            transform: `translateY(${scrollY * 0.1}px)`,
            opacity: Math.max(0.3, 1 - scrollY * 0.001)
          }}
        >
          <ellipse cx="150" cy="70" rx="4" ry="2" fill="oklch(0.96 0.015 60)" opacity="0.6" />
          <ellipse cx="170" cy="190" rx="3" ry="2.5" fill="oklch(0.94 0.02 55)" opacity="0.5" />
          <ellipse cx="150" cy="310" rx="4" ry="2" fill="oklch(0.96 0.015 60)" opacity="0.6" />
          <ellipse cx="130" cy="430" rx="2.5" ry="2" fill="oklch(0.92 0.025 50)" opacity="0.4" />
          <ellipse cx="210" cy="550" rx="4" ry="2.5" fill="oklch(0.96 0.015 60)" opacity="0.6" />
          <ellipse cx="190" cy="670" rx="3" ry="2" fill="oklch(0.94 0.02 55)" opacity="0.5" />
          <ellipse cx="170" cy="790" rx="4" ry="2" fill="oklch(0.96 0.015 60)" opacity="0.6" />
        </g>

        {/* Additional organic texture elements with scroll-based movement */}
        <g
          className="animate-pulse"
          style={{
            animationDuration: '7s',
            animationDelay: '2.5s',
            transform: `translateY(${scrollY * 0.15}px)`,
            opacity: Math.max(0.2, 0.8 - scrollY * 0.0008)
          }}
        >
          <ellipse cx="135" cy="135" rx="2" ry="1.5" fill="oklch(0.93 0.02 52)" opacity="0.4" />
          <ellipse cx="215" cy="255" rx="3" ry="2" fill="oklch(0.95 0.018 58)" opacity="0.5" />
          <ellipse cx="95" cy="375" rx="2" ry="1.5" fill="oklch(0.91 0.028 48)" opacity="0.3" />
          <ellipse cx="175" cy="495" rx="3" ry="2" fill="oklch(0.95 0.018 58)" opacity="0.5" />
          <ellipse cx="255" cy="615" rx="2.5" ry="1.5" fill="oklch(0.93 0.02 52)" opacity="0.4" />
          <ellipse cx="135" cy="735" rx="3" ry="2" fill="oklch(0.95 0.018 58)" opacity="0.5" />
        </g>

        {/* Scroll-triggered pathway highlights that appear as user progresses */}
        <g style={{ opacity: Math.min(1, scrollY * 0.002) }}>
          <circle cx="150" cy={70 + scrollY * 0.05} r="6" fill="none" stroke="oklch(0.98 0.01 50)" strokeWidth="1" opacity="0.4" />
          <circle cx="170" cy={190 + scrollY * 0.05} r="5" fill="none" stroke="oklch(0.96 0.015 55)" strokeWidth="1" opacity="0.3" />
          <circle cx="150" cy={310 + scrollY * 0.05} r="7" fill="none" stroke="oklch(0.98 0.01 50)" strokeWidth="1" opacity="0.4" />
        </g>
      </svg>
    </div>
  );
};

export default MeanderingPathway;