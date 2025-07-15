import React from 'react';

interface DataItemProps {
  id: string;
  title: string;
  description?: string;
  status?: string;
  onClick: (id: string, data: any) => void;
  data: any;
  isSelected?: boolean;
}

export const DataItem: React.FC<DataItemProps> = ({
  id,
  title,
  description,
  status,
  onClick,
  data,
  isSelected = false,
}) => {
  const handleClick = () => {
    onClick(id, data);
  };

  return (
    <div
      className={`
        p-4 border rounded-lg cursor-pointer transition-all duration-200
        hover:shadow-md hover:border-primary-500
        ${isSelected 
          ? 'border-primary-500 bg-primary-50 shadow-md' 
          : 'border-neutral-200 bg-white hover:bg-neutral-50'
        }
      `}
      onClick={handleClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h4 className="font-medium text-neutral-900 mb-1">
            {title}
          </h4>
          {description && (
            <p className="text-sm text-neutral-600 mb-2 line-clamp-2">
              {description}
            </p>
          )}
          {status && (
            <span className={`
              inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
              ${status === 'active' 
                ? 'bg-success-100 text-success-800' 
                : status === 'completed'
                ? 'bg-primary-100 text-primary-800'
                : 'bg-neutral-100 text-neutral-800'
              }
            `}>
              {status}
            </span>
          )}
        </div>
        <div className="ml-3 flex-shrink-0">
          <div className={`
            w-5 h-5 rounded-full border-2 flex items-center justify-center
            ${isSelected 
              ? 'border-primary-500 bg-primary-500' 
              : 'border-neutral-300'
            }
          `}>
            {isSelected && (
              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

interface DataCategoryProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  itemCount?: number;
}

export const DataCategory: React.FC<DataCategoryProps> = ({
  title,
  description,
  children,
  itemCount,
}) => {
  return (
    <div className="mb-8">
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-neutral-900">
            {title}
          </h3>
          {itemCount !== undefined && (
            <span className="text-sm text-neutral-500">
              {itemCount} {itemCount === 1 ? 'item' : 'items'}
            </span>
          )}
        </div>
        {description && (
          <p className="text-sm text-neutral-600 mt-1">
            {description}
          </p>
        )}
      </div>
      <div className="space-y-3">
        {children}
      </div>
    </div>
  );
};