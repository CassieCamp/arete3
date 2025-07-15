import { LEADERSHIP_CATEGORIES } from '../../config/leadershipCategories';
import CategoryFilterButton from './CategoryFilterButton';
import { X } from 'lucide-react';

interface CategoryFiltersProps {
  categoryCounts: Record<string, number>;
  selectedCategories: string[];
  onCategoryToggle: (category: string) => void;
  totalInsights: number;
}

const CategoryFilters = ({ categoryCounts, selectedCategories, onCategoryToggle, totalInsights }: CategoryFiltersProps) => {
  // Only show categories that have content
  const availableCategories = LEADERSHIP_CATEGORIES.filter(cat => 
    categoryCounts[cat.key] > 0
  );
  
  if (availableCategories.length === 0) return null;

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-foreground">
          Leadership Development Areas
        </h3>
        <span className="text-sm text-muted-foreground">
          {selectedCategories.length === 0 ? `${totalInsights} insights` : 'Filtered insights'}
        </span>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {availableCategories.map(category => (
          <CategoryFilterButton
            key={category.key}
            category={category}
            count={categoryCounts[category.key]}
            isSelected={selectedCategories.includes(category.key)}
            onClick={() => onCategoryToggle(category.key)}
          />
        ))}
      </div>
      
      {selectedCategories.length > 0 && (
        <div className="mt-4 flex items-center gap-2 flex-wrap">
          <span className="text-sm text-muted-foreground">Active filters:</span>
          {selectedCategories.map(catKey => {
            const category = LEADERSHIP_CATEGORIES.find(c => c.key === catKey);
            return (
              <button
                key={catKey}
                onClick={() => onCategoryToggle(catKey)}
                className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-muted/30 text-muted-foreground rounded-full hover:bg-muted/50 transition-colors"
              >
                <span>{category?.icon}</span>
                <span>{category?.shortLabel}</span>
                <X className="w-3 h-3" />
              </button>
            );
          })}
          <button
            onClick={() => selectedCategories.forEach(onCategoryToggle)}
            className="text-xs text-muted-foreground hover:text-foreground underline transition-colors"
          >
            Clear all
          </button>
        </div>
      )}
    </div>
  );
};

export default CategoryFilters;