"use client";

import { SignUp } from '@clerk/nextjs';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function SignUpPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="bg-card/80 backdrop-blur-sm border-b border-border/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center space-x-2 text-foreground hover:text-muted-foreground">
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Homepage</span>
            </Link>
            <h1 className="text-xl font-medium text-foreground">
              Sign Up
            </h1>
          </div>
        </div>
      </nav>

      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-serif font-bold text-foreground mb-2">
              Join Arete
            </h1>
            <p className="text-muted-foreground">
              Start your transformation journey today
            </p>
          </div>
          
          <SignUp
            appearance={{
              elements: {
                formButtonPrimary: "bg-primary hover:bg-primary/90 text-primary-foreground",
                card: "shadow-lg border border-border",
                headerTitle: "hidden",
                headerSubtitle: "hidden",
                socialButtonsBlockButton: "border-border text-foreground hover:bg-accent",
                formFieldInput: "border-border focus:border-primary",
                footerActionLink: "text-primary hover:text-primary/80"
              }
            }}
            signInUrl="/sign-in"
            fallbackRedirectUrl="/profile/create/client"
          />
        </div>
      </div>
    </div>
  );
}