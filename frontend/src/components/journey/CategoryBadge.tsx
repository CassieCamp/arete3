import { LEADERSHIP_CATEGORIES } from '../../config/leadershipCategories';
import React from 'react';

interface CategoryBadgeProps {
  category: typeof LEADERSHIP_CATEGORIES[0];
  size?: 'sm' | 'md';
  onClick?: (e: React.MouseEvent) => void;
}

const CategoryBadge = ({ category, size = 'md', onClick }: CategoryBadgeProps) => {
  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5'
  };

  return (
    <button
      onClick={onClick}
      className={`
        inline-flex items-center gap-1 rounded-full border border-border
        bg-muted/10 text-muted-foreground hover:bg-muted/20 font-medium
        transition-colors duration-200
        ${sizeClasses[size]}
        ${onClick ? 'cursor-pointer' : 'cursor-default'}
      `}
      title={`Filter by ${category.label}`}
    >
      <span>{category.icon}</span>
      <span>{category.shortLabel}</span>
    </button>
  );
};

export default CategoryBadge;