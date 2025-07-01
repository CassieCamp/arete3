"use client";

import { Waitlist } from "@clerk/nextjs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function ClientWaitlistPage() {
  return (
    <div className="min-h-screen bg-moonlight-ivory">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-sm border-b border-cloud-grey/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center space-x-2 text-midnight-indigo hover:text-owlet-teal">
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Homepage</span>
            </Link>
            <h1 className="text-xl font-medium text-midnight-indigo">
              Client Waitlist
            </h1>
          </div>
        </div>
      </nav>

      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-3xl md:text-4xl font-serif font-bold text-midnight-indigo mb-4">
            Transform Your Leadership Journey
          </h1>
        </div>

        <Card className="border-cloud-grey/30 shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-serif text-midnight-indigo">
              Join the Client Waitlist
            </CardTitle>
            <CardDescription className="text-owlet-teal">
              Be among the first to experience AI-enhanced executive coaching
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex justify-center">
              <Waitlist
                afterJoinWaitlistUrl="/waitlist/success"
                appearance={{
                  elements: {
                    formButtonPrimary: "bg-midnight-indigo hover:bg-midnight-indigo/90 text-white",
                    card: "shadow-none border-0",
                    headerTitle: "hidden",
                    headerSubtitle: "hidden",
                    socialButtonsBlockButton: "border-cloud-grey text-midnight-indigo hover:bg-midnight-indigo hover:text-white",
                    formFieldInput: "border-cloud-grey focus:border-midnight-indigo",
                    footerActionLink: "text-midnight-indigo hover:text-midnight-indigo/80"
                  }
                }}
              />
            </div>
            
            <div className="mt-6 pt-6 border-t border-cloud-grey/30">
              <p className="text-sm text-owlet-teal text-center">
                Already have an account?{' '}
                <Link href="/sign-in" className="text-midnight-indigo hover:underline">
                  Sign in here
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}