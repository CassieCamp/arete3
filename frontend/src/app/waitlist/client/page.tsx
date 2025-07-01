"use client";

import { Waitlist } from "@clerk/nextjs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Target, Brain, BarChart3 } from 'lucide-react';
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
            <h1 className="text-xl font-serif font-bold text-midnight-indigo">
              Arete Client Waitlist
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
                Transform Your Leadership Journey
              </h1>
              <p className="text-xl text-owlet-teal leading-relaxed">
                Join the waitlist for AI-enhanced executive coaching that accelerates your professional development.
              </p>
            </div>

            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-midnight-indigo/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Target className="w-6 h-6 text-midnight-indigo" />
                </div>
                <div>
                  <h3 className="font-semibold text-midnight-indigo mb-2">Personalized Goal Setting</h3>
                  <p className="text-owlet-teal">
                    Set and track meaningful leadership goals with AI-powered insights that help you identify the most impactful areas for growth.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-metis-gold/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Brain className="w-6 h-6 text-metis-gold" />
                </div>
                <div>
                  <h3 className="font-semibold text-midnight-indigo mb-2">Session Insights</h3>
                  <p className="text-owlet-teal">
                    Receive AI-generated insights from your coaching sessions that reveal patterns, breakthroughs, and actionable next steps.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-owlet-teal/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <BarChart3 className="w-6 h-6 text-owlet-teal" />
                </div>
                <div>
                  <h3 className="font-semibold text-midnight-indigo mb-2">Progress Visualization</h3>
                  <p className="text-owlet-teal">
                    Track your transformation journey with comprehensive analytics that show your growth over time and celebrate milestones.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-blue-50 p-6 rounded-lg">
              <h3 className="font-semibold text-midnight-indigo mb-3">Perfect for Leaders Who Want To:</h3>
              <ul className="space-y-2 text-owlet-teal">
                <li>• Accelerate their leadership development with data-driven insights</li>
                <li>• Gain clarity on their transformation patterns and blind spots</li>
                <li>• Work with experienced executive coaches enhanced by AI</li>
                <li>• Track and visualize their professional growth journey</li>
              </ul>
            </div>

            <div className="bg-metis-gold/10 p-6 rounded-lg">
              <h3 className="font-semibold text-midnight-indigo mb-2">Early Access Benefits</h3>
              <p className="text-owlet-teal text-sm mb-3">
                As an early user, you'll receive:
              </p>
              <ul className="text-sm text-owlet-teal space-y-1">
                <li>• Priority matching with our top executive coaches</li>
                <li>• Complimentary baseline assessment and goal-setting session</li>
                <li>• Access to exclusive features and beta testing opportunities</li>
                <li>• Special pricing for your first coaching engagement</li>
              </ul>
            </div>
          </div>

          {/* Right Column - Waitlist Form */}
          <div className="lg:sticky lg:top-8">
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
                <div className="flex justify-center pt-16">
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
      </div>
    </div>
  );
}