"use client";

import { Waitlist, useClerk } from "@clerk/nextjs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function WaitlistPage() {
  const { redirectToSignIn } = useClerk();
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
              Join Our Waitlist
            </h1>
          </div>
        </div>
      </nav>

      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-3xl md:text-4xl font-serif font-bold text-foreground mb-4">
            Join the Future of Executive Coaching
          </h1>
        </div>

        <Card className="border-border/30 shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-serif text-foreground">
              Join Our Waitlist
            </CardTitle>
            <CardDescription className="text-muted-foreground">
              Be among the first to experience AI-enhanced executive coaching
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex justify-center">
              <Waitlist
                afterJoinWaitlistUrl="/waitlist/success"
                appearance={{
                  elements: {
                    formButtonPrimary: "bg-primary hover:bg-primary/90 text-primary-foreground",
                    card: "shadow-none border-0",
                    headerTitle: "hidden",
                    headerSubtitle: "hidden",
                    socialButtonsBlockButton: "border-border text-foreground hover:bg-accent",
                    formFieldInput: "border-border focus:border-primary",
                    footerActionLink: "text-primary hover:text-primary/80"
                  }
                }}
              />
            </div>
            
            <div className="mt-6 pt-6 border-t border-border/30">
              <p className="text-sm text-muted-foreground text-center">
                Already have an account?{' '}
                <button
                  onClick={() => redirectToSignIn()}
                  className="text-primary hover:underline cursor-pointer"
                >
                  Sign in here
                </button>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}