'use client';

import React, { useState, useCallback, useMemo } from 'react';
import { AdvancedInsightsFilters } from '@/hooks/journey/useAdvancedInsights';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Search, 
  Filter, 
  X, 
  ChevronDown, 
  Calendar,
  Star,
  Target,
  Tag,
  SortAsc,
  SortDesc
} from 'lucide-react';

interface FilterSuggestion {
  type: 'category' | 'tag';
  label: string;
  count: number;
  filter: Partial<AdvancedInsightsFilters>;
}

interface SmartFilterBarProps {
  filters: AdvancedInsightsFilters;
  onFiltersChange: (filters: AdvancedInsightsFilters) => void;
  suggestions: FilterSuggestion[];
  facets?: {
    categories: { [key: string]: number };
    tags: { [key: string]: number };
    review_statuses: { [key: string]: number };
    processing_statuses: { [key: string]: number };
  };
  totalCount: number;
  isLoading?: boolean;
}

export function SmartFilterBar({
  filters,
  onFiltersChange,
  suggestions,
  facets,
  totalCount,
  isLoading = false
}: SmartFilterBarProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [searchInput, setSearchInput] = useState(filters.searchQuery || '');

  // Handle search input with debouncing
  const handleSearchChange = useCallback((value: string) => {
    setSearchInput(value);
    // Simple debouncing - in a real app, you'd use a proper debounce hook
    const timeoutId = setTimeout(() => {
      onFiltersChange({
        ...filters,
        searchQuery: value.trim() || undefined
      });
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [filters, onFiltersChange]);

  // Handle filter updates
  const updateFilter = useCallback((key: keyof AdvancedInsightsFilters, value: any) => {
    onFiltersChange({
      ...filters,
      [key]: value
    });
  }, [filters, onFiltersChange]);

  // Handle array filter updates (categories, tags, etc.)
  const updateArrayFilter = useCallback((key: keyof AdvancedInsightsFilters, item: string, add: boolean) => {
    const currentArray = (filters[key] as string[]) || [];
    const newArray = add 
      ? [...currentArray, item]
      : currentArray.filter(i => i !== item);
    
    updateFilter(key, newArray.length > 0 ? newArray : undefined);
  }, [filters, updateFilter]);

  // Apply suggestion
  const applySuggestion = useCallback((suggestion: FilterSuggestion) => {
    onFiltersChange({
      ...filters,
      ...suggestion.filter
    });
  }, [filters, onFiltersChange]);

  // Clear all filters
  const clearAllFilters = useCallback(() => {
    setSearchInput('');
    onFiltersChange({});
  }, [onFiltersChange]);

  // Remove specific filter
  const removeFilter = useCallback((key: keyof AdvancedInsightsFilters, value?: string) => {
    if (value && Array.isArray(filters[key])) {
      updateArrayFilter(key, value, false);
    } else {
      updateFilter(key, undefined);
    }
  }, [filters, updateFilter, updateArrayFilter]);

  // Count active filters
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.searchQuery) count++;
    if (filters.categories?.length) count += filters.categories.length;
    if (filters.tags?.length) count += filters.tags.length;
    if (filters.reviewStatus?.length) count += filters.reviewStatus.length;
    if (filters.processingStatus?.length) count += filters.processingStatus.length;
    if (filters.itemTypes?.length) count += filters.itemTypes.length;
    if (filters.isFavorite !== undefined) count++;
    if (filters.isActionable !== undefined) count++;
    if (filters.minConfidence !== undefined) count++;
    if (filters.timeRange?.start || filters.timeRange?.end) count++;
    return count;
  }, [filters]);

  // Sort options
  const sortOptions = [
    { value: 'created_at:desc', label: 'Newest first' },
    { value: 'created_at:asc', label: 'Oldest first' },
    { value: 'updated_at:desc', label: 'Recently updated' },
    { value: 'confidence_score:desc', label: 'Highest confidence' },
    { value: 'user_rating:desc', label: 'Highest rated' },
    { value: 'view_count:desc', label: 'Most viewed' }
  ];

  const currentSort = `${filters.sortBy || 'created_at'}:${filters.sortOrder || 'desc'}`;

  return (
    <div className="space-y-4">
      {/* Main Filter Row */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Search Input */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search insights..."
            value={searchInput}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="pl-10 pr-4"
            disabled={isLoading}
          />
        </div>

        {/* Sort Dropdown */}
        <Select
          value={currentSort}
          onValueChange={(value) => {
            const [sortBy, sortOrder] = value.split(':');
            updateFilter('sortBy', sortBy as any);
            updateFilter('sortOrder', sortOrder as 'asc' | 'desc');
          }}
        >
          <option value="">Sort by...</option>
          {sortOptions.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Select>

        {/* Advanced Filters Toggle */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center gap-2"
        >
          <Filter className="w-4 h-4" />
          Filters
          {activeFilterCount > 0 && (
            <Badge variant="secondary" className="ml-1 px-1.5 py-0.5 text-xs">
              {activeFilterCount}
            </Badge>
          )}
          <ChevronDown className={`w-4 h-4 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
        </Button>

        {/* Clear All */}
        {activeFilterCount > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearAllFilters}
            className="text-muted-foreground hover:text-foreground"
          >
            Clear all
          </Button>
        )}
      </div>

      {/* Active Filters */}
      {activeFilterCount > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm text-muted-foreground">Active filters:</span>
          
          {filters.searchQuery && (
            <Badge variant="outline" className="flex items-center gap-1">
              <Search className="w-3 h-3" />
              "{filters.searchQuery}"
              <button
                onClick={() => removeFilter('searchQuery')}
                className="ml-1 hover:text-destructive"
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}

          {filters.categories?.map(category => (
            <Badge key={category} variant="outline" className="flex items-center gap-1">
              <Tag className="w-3 h-3" />
              {category}
              <button
                onClick={() => removeFilter('categories', category)}
                className="ml-1 hover:text-destructive"
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          ))}

          {filters.tags?.map(tag => (
            <Badge key={tag} variant="outline" className="flex items-center gap-1">
              <Tag className="w-3 h-3" />
              #{tag}
              <button
                onClick={() => removeFilter('tags', tag)}
                className="ml-1 hover:text-destructive"
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          ))}

          {filters.isFavorite && (
            <Badge variant="outline" className="flex items-center gap-1">
              <Star className="w-3 h-3" />
              Favorites
              <button
                onClick={() => removeFilter('isFavorite')}
                className="ml-1 hover:text-destructive"
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}

          {filters.isActionable && (
            <Badge variant="outline" className="flex items-center gap-1">
              <Target className="w-3 h-3" />
              Actionable
              <button
                onClick={() => removeFilter('isActionable')}
                className="ml-1 hover:text-destructive"
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}
        </div>
      )}

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="space-y-2">
          <span className="text-sm text-muted-foreground">Suggested filters:</span>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion, index) => (
              <Button
                key={`${suggestion.type}-${suggestion.label}-${index}`}
                variant="ghost"
                size="sm"
                onClick={() => applySuggestion(suggestion)}
                className="h-auto py-1 px-2 text-xs border border-dashed border-muted-foreground/30 hover:border-primary hover:bg-primary/5"
              >
                {suggestion.type === 'category' ? <Tag className="w-3 h-3 mr-1" /> : <Tag className="w-3 h-3 mr-1" />}
                {suggestion.label}
                <span className="ml-1 text-muted-foreground">({suggestion.count})</span>
              </Button>
            ))}
          </div>
        </div>
      )}

      {/* Advanced Filters Panel */}
      {showAdvanced && (
        <div className="border border-border rounded-lg p-4 bg-card space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Item Types */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Content Type</label>
              <div className="space-y-2">
                {['insight', 'reflection'].map(type => (
                  <div key={type} className="flex items-center space-x-2">
                    <Checkbox
                      id={`type-${type}`}
                      checked={filters.itemTypes?.includes(type as any) || false}
                      onCheckedChange={(checked) => 
                        updateArrayFilter('itemTypes', type, !!checked)
                      }
                    />
                    <label htmlFor={`type-${type}`} className="text-sm capitalize">
                      {type}s
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Filters */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Quick Filters</label>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="favorites"
                    checked={filters.isFavorite || false}
                    onCheckedChange={(checked) => 
                      updateFilter('isFavorite', checked ? true : undefined)
                    }
                  />
                  <label htmlFor="favorites" className="text-sm flex items-center gap-1">
                    <Star className="w-3 h-3" />
                    Favorites only
                  </label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="actionable"
                    checked={filters.isActionable || false}
                    onCheckedChange={(checked) => 
                      updateFilter('isActionable', checked ? true : undefined)
                    }
                  />
                  <label htmlFor="actionable" className="text-sm flex items-center gap-1">
                    <Target className="w-3 h-3" />
                    Actionable only
                  </label>
                </div>
              </div>
            </div>

            {/* Confidence Score */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Minimum Confidence</label>
              <Input
                type="number"
                min="0"
                max="1"
                step="0.1"
                placeholder="0.0 - 1.0"
                value={filters.minConfidence || ''}
                onChange={(e) => 
                  updateFilter('minConfidence', e.target.value ? parseFloat(e.target.value) : undefined)
                }
              />
            </div>
          </div>
        </div>
      )}

      {/* Results Summary */}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          {isLoading ? 'Loading...' : `${totalCount} insights found`}
        </span>
        {activeFilterCount > 0 && (
          <span>{activeFilterCount} filter{activeFilterCount !== 1 ? 's' : ''} applied</span>
        )}
      </div>
    </div>
  );
}