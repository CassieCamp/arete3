"use client";

import { LucideIcon } from 'lucide-react';

interface PageHeaderProps {
  icon?: LucideIcon;
  title: string;
  subtitle?: string;
  className?: string;
}

export function PageHeader({ 
  icon: Icon, 
  title, 
  subtitle, 
  className = "" 
}: PageHeaderProps) {
  return (
    <div className={`mb-6 ${className}`}>
      <div className="flex items-center gap-3 mb-2">
        {Icon && <Icon className="h-6 w-6 text-muted-foreground" />}
        <h1 className="text-2xl font-bold text-foreground">{title}</h1>
      </div>
      {subtitle && (
        <p className="text-muted-foreground">{subtitle}</p>
      )}
    </div>
  );
}