"use client";

import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

interface AuthDropdownProps {
  variant?: 'default' | 'ghost' | 'outline';
  size?: 'default' | 'sm' | 'lg';
  className?: string;
}

export function AuthDropdown({
  variant = 'ghost',
  size = 'default',
  className = ''
}: AuthDropdownProps) {
  return (
    <Link href="/sign-in">
      <Button
        variant={variant}
        size={size}
        className={className}
      >
        Sign In
      </Button>
    </Link>
  );
}