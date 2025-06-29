"use client";

import { usePathname } from 'next/navigation';
import { useNavigation } from './NavigationProvider';
import { getNavigationItem } from '@/config/navigation';

export function useCurrentNavigation() {
  const pathname = usePathname();
  const { navigation } = useNavigation();

  // Find current navigation item
  const currentItem = navigation
    .flatMap(section => section.items)
    .find(item => item.href === pathname);

  // Find breadcrumb trail
  const breadcrumbs = [];
  if (currentItem) {
    // Add section title
    const section = navigation.find(s => s.items.includes(currentItem));
    if (section && section.title !== 'Main') {
      breadcrumbs.push({ title: section.title, href: '#' });
    }
    breadcrumbs.push({ title: currentItem.title, href: currentItem.href });
  }

  return {
    currentItem,
    breadcrumbs,
    pageTitle: currentItem?.title || 'Dashboard'
  };
}

export function NavigationBreadcrumb() {
  const { breadcrumbs } = useCurrentNavigation();

  if (breadcrumbs.length <= 1) return null;

  return (
    <nav className="flex mb-4" aria-label="Breadcrumb">
      <ol className="flex items-center space-x-2 text-sm text-muted-foreground">
        {breadcrumbs.map((crumb, index) => (
          <li key={crumb.href} className="flex items-center">
            {index > 0 && <span className="mx-2">/</span>}
            <span className={index === breadcrumbs.length - 1 ? 'text-foreground font-medium' : ''}>
              {crumb.title}
            </span>
          </li>
        ))}
      </ol>
    </nav>
  );
}

export function PageHeader() {
  const { currentItem, pageTitle } = useCurrentNavigation();

  return (
    <div className="mb-6">
      <NavigationBreadcrumb />
      <div className="flex items-center gap-3">
        {currentItem?.icon && <currentItem.icon className="h-6 w-6 text-muted-foreground" />}
        <h1 className="text-2xl font-bold text-foreground">{pageTitle}</h1>
      </div>
      {currentItem?.description && (
        <p className="mt-2 text-muted-foreground">{currentItem.description}</p>
      )}
    </div>
  );
}