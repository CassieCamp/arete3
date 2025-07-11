"use client";

import React, { useState } from 'react';
import { SignIn, SignUp } from '@clerk/nextjs';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { ChevronDown } from 'lucide-react';

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
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin');

  const handleModeSwitch = (mode: 'signin' | 'signup') => {
    setAuthMode(mode);
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant={variant}
          size={size}
          className={`flex items-center gap-2 ${className}`}
        >
          Sign In
          <ChevronDown className="w-4 h-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        className="w-96 p-0 border-border bg-background"
        align="end"
      >
        <div className="p-4">
          {/* Mode Toggle */}
          <div className="flex mb-4 bg-muted rounded-lg p-1">
            <button
              onClick={() => handleModeSwitch('signin')}
              className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors ${
                authMode === 'signin'
                  ? 'bg-background text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => handleModeSwitch('signup')}
              className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors ${
                authMode === 'signup'
                  ? 'bg-background text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Sign Up
            </button>
          </div>

          {/* Clerk Auth Component */}
          <div className="clerk-auth-container">
            {authMode === 'signin' ? (
              <SignIn
                appearance={{
                  elements: {
                    rootBox: "w-full",
                    card: "shadow-none border-0 bg-transparent p-0",
                    headerTitle: "hidden",
                    headerSubtitle: "hidden",
                    socialButtonsBlockButton: "w-full justify-center",
                    formButtonPrimary: "w-full bg-primary hover:bg-primary/90",
                    footerAction: "hidden",
                    identityPreviewText: "text-sm",
                    formFieldInput: "border-input",
                  },
                  layout: {
                    socialButtonsPlacement: "top",
                    showOptionalFields: false,
                  }
                }}
                redirectUrl="/journey"
                signUpUrl="#"
                afterSignInUrl="/journey"
              />
            ) : (
              <SignUp
                appearance={{
                  elements: {
                    rootBox: "w-full",
                    card: "shadow-none border-0 bg-transparent p-0",
                    headerTitle: "hidden",
                    headerSubtitle: "hidden",
                    socialButtonsBlockButton: "w-full justify-center",
                    formButtonPrimary: "w-full bg-primary hover:bg-primary/90",
                    footerAction: "hidden",
                    identityPreviewText: "text-sm",
                    formFieldInput: "border-input",
                  },
                  layout: {
                    socialButtonsPlacement: "top",
                    showOptionalFields: false,
                  }
                }}
                redirectUrl="/profile/create/client"
                signInUrl="#"
                afterSignUpUrl="/profile/create/client"
              />
            )}
          </div>

          {/* Mode Switch Links */}
          <div className="mt-4 text-center text-sm text-muted-foreground">
            {authMode === 'signin' ? (
              <span>
                Don't have an account?{' '}
                <button
                  onClick={() => handleModeSwitch('signup')}
                  className="text-primary hover:underline font-medium"
                >
                  Sign up
                </button>
              </span>
            ) : (
              <span>
                Already have an account?{' '}
                <button
                  onClick={() => handleModeSwitch('signin')}
                  className="text-primary hover:underline font-medium"
                >
                  Sign in
                </button>
              </span>
            )}
          </div>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}