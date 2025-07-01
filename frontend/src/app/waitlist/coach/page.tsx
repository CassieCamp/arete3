"use client";

import { Waitlist } from "@clerk/nextjs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Users, Lightbulb, TrendingUp } from 'lucide-react';
import Link from 'next/link';

export default function CoachWaitlistPage() {
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
            <h1 className="text-xl font-serif font-bold text-midnight-indigo">
              Arete Coach Waitlist
            </h1>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Left Column - Information */}
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-serif font-bold text-midnight-indigo mb-4">
                Partner with Arete as an Executive Coach
              </h1>
              <p className="text-xl text-owlet-teal leading-relaxed">
                Join our exclusive network of executive coaches and enhance your practice with AI-powered insights.
              </p>
            </div>

            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-metis-gold/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Lightbulb className="w-6 h-6 text-metis-gold" />
                </div>
                <div>
                  <h3 className="font-semibold text-midnight-indigo mb-2">AI-Enhanced Insights</h3>
                  <p className="text-owlet-teal">
                    Generate deeper insights from coaching sessions with our AI analysis tools, helping you identify patterns and breakthroughs faster.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-owlet-teal/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Users className="w-6 h-6 text-owlet-teal" />
                </div>
                <div>
                  <h3 className="font-semibold text-midnight-indigo mb-2">Client Management</h3>
                  <p className="text-owlet-teal">
                    Streamline your coaching practice with integrated client management, progress tracking, and goal setting tools.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-midnight-indigo/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <TrendingUp className="w-6 h-6 text-midnight-indigo" />
                </div>
                <div>
                  <h3 className="font-semibold text-midnight-indigo mb-2">Growth Analytics</h3>
                  <p className="text-owlet-teal">
                    Track client progress with comprehensive analytics and visualizations that demonstrate coaching impact.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-metis-gold/10 p-6 rounded-lg">
              <h3 className="font-semibold text-midnight-indigo mb-3">What We're Looking For</h3>
              <ul className="space-y-2 text-owlet-teal">
                <li>• Certified executive coaches with 3+ years of experience</li>
                <li>• Experience working with C-level executives and senior leaders</li>
                <li>• Interest in integrating AI tools into coaching practice</li>
                <li>• Commitment to continuous learning and development</li>
              </ul>
            </div>
          </div>

          {/* Right Column - Waitlist Form */}
          <div className="lg:sticky lg:top-8">
            <Card className="border-cloud-grey/30 shadow-lg">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl font-serif text-midnight-indigo">
                  Join the Coach Waitlist
                </CardTitle>
                <CardDescription className="text-owlet-teal">
                  Be among the first coaches to access our AI-enhanced platform
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex justify-center pt-16">
                  <Waitlist
                    afterJoinWaitlistUrl="/waitlist/success"
                    appearance={{
                      elements: {
                        formButtonPrimary: "bg-metis-gold hover:bg-metis-gold/90 text-white",
                        card: "shadow-none border-0",
                        headerTitle: "hidden",
                        headerSubtitle: "hidden",
                        socialButtonsBlockButton: "border-cloud-grey text-midnight-indigo hover:bg-midnight-indigo hover:text-white",
                        formFieldInput: "border-cloud-grey focus:border-metis-gold",
                        footerActionLink: "text-metis-gold hover:text-metis-gold/80"
                      }
                    }}
                  />
                </div>
                
                <div className="mt-6 pt-6 border-t border-cloud-grey/30">
                  <p className="text-sm text-owlet-teal text-center">
                    Already have an account?{' '}
                    <Link href="/sign-in" className="text-metis-gold hover:underline">
                      Sign in here
                    </Link>
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}