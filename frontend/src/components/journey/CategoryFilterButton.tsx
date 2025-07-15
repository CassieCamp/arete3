import { LEADERSHIP_CATEGORIES } from '../../config/leadershipCategories';

interface CategoryFilterButtonProps {
  category: typeof LEADERSHIP_CATEGORIES[0];
  count: number;
  isSelected: boolean;
  onClick: () => void;
}

const CategoryFilterButton = ({ category, count, isSelected, onClick }: CategoryFilterButtonProps) => {
  return (
    <button
      onClick={onClick}
      className={`
        relative p-4 rounded-lg border transition-all duration-200
        ${isSelected 
          ? 'border-primary bg-primary/5 ring-1 ring-primary/20' 
          : 'border-border bg-card hover:border-muted hover:bg-muted/5'
        }
      `}
    >
      <div className="text-center">
        <div className="text-2xl mb-2">{category.icon}</div>
        <div className="font-medium text-sm mb-1 text-foreground">{category.shortLabel}</div>
        <div className="text-xs text-muted-foreground mb-2 line-clamp-2">{category.description}</div>
        <div className={`
          inline-flex items-center justify-center px-2 py-1 rounded-full text-xs font-medium
          ${isSelected 
            ? 'bg-primary/10 text-primary border border-primary/20' 
            : 'bg-muted/20 text-muted-foreground border border-border'
          }
        `}>
          {count} insight{count !== 1 ? 's' : ''}
        </div>
      </div>
    </button>
  );
};

export default CategoryFilterButton;