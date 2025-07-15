// frontend/src/components/journey/BackgroundShape.tsx
import React from 'react';

const BackgroundShape = ({ isExpanded, position }: { isExpanded: boolean, position: 'list' | 'detail' }) => {
  return (
    <div 
      className={`absolute transition-all duration-300 ${
        isExpanded ? 'inset-4' : 'inset-2'
      }`}
      style={{
        backgroundColor: 'oklch(0.9583 0.0111 89.7230)', // Hard-coded light cream
        borderRadius: '12px',
        zIndex: 1, // Behind cards but above dark background
        opacity: 0.95
      }}
    />
  );
};

export default BackgroundShape;