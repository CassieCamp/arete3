"use client";

import React from 'react';
import { SignInButton } from '@clerk/nextjs';
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
    <SignInButton mode="modal">
      <Button
        variant={variant}
        size={size}
        className={className}
      >
        Sign In
      </Button>
    </SignInButton>
  );
}