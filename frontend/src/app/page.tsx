"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import { useState, useEffect, useRef } from "react";

export default function Home() {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);

    const formData = new FormData(e.currentTarget);
    const data = {
      firstName: formData.get('firstName'),
      lastName: formData.get('lastName'),
      email: formData.get('email'),
      role: formData.get('role'),
      company: formData.get('company'),
      feedback: formData.get('feedback'),
      timestamp: new Date().toISOString()
    };

    try {
      // For now, we'll just log the data and show success
      // In the future, this could be sent to an API endpoint
      console.log('Form submission:', data);
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setIsSubmitted(true);
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };
  return (
    <div className="min-h-screen bg-moonlight-ivory">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-sm border-b border-cloud-grey/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-serif font-bold text-midnight-indigo">
                Arete
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <SignedOut>
                <SignInButton mode="modal">
                  <Button variant="outline" className="border-midnight-indigo text-midnight-indigo hover:bg-midnight-indigo hover:text-white">
                    Sign In
                  </Button>
                </SignInButton>
                <div className="relative" ref={dropdownRef}>
                  <Button
                    onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                    className="bg-[#1B1E3C] hover:bg-[#1B1E3C]/90 text-white font-medium"
                  >
                    Join Waitlist ▾
                  </Button>
                  <div className={`absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg transition-all duration-200 z-50 ${
                    isDropdownOpen ? 'opacity-100 visible' : 'opacity-0 invisible'
                  }`}>
                    <div className="py-1">
                      <Link
                        href="/waitlist/client"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        onClick={() => setIsDropdownOpen(false)}
                      >
                        Join as Client
                      </Link>
                      <Link
                        href="/waitlist/coach"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        onClick={() => setIsDropdownOpen(false)}
                      >
                        Join as Coach
                      </Link>
                    </div>
                  </div>
                </div>
              </SignedOut>
              <SignedIn>
                <Link href="/dashboard/connections">
                  <Button className="bg-[#1B1E3C] hover:bg-[#1B1E3C]/90 text-white font-medium">
                    Dashboard
                  </Button>
                </Link>
                <UserButton afterSignOutUrl="/" />
              </SignedIn>
            </div>
          </div>
        </div>
      </nav>
      {/* Hero Section */}
      <section className="relative py-14 lg:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-serif font-bold text-midnight-indigo mb-16">
              Your partner in
              <span className="block text-metis-gold">executive transformation</span>
            </h1>
            <p className="text-base md:text-lg text-owlet-teal mb-12 max-w-3xl mx-auto leading-loose text-left px-8">
              Excellence isn't perfection. It's the courage to become who you're truly meant to be. The ancient Greeks called this arete—your highest potential realized. That depth of courage deserves a guide who understands the journey.
              <br /><br />
              We believe coaching should be as normal for leaders as it is for athletes. Enter your human executive coach. Our role is simple: honor that sacred relationship by providing AI that gently amplifies the wisdom, never replacing the human connection that drives real growth.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="/waitlist/client">
                <Button size="lg" className="bg-[#1B1E3C] hover:bg-[#1B1E3C]/90 !text-white px-8 py-4 text-lg">
                  Join Client Waitlist
                </Button>
              </Link>
              <Link href="/waitlist/coach">
                <Button variant="outline" size="lg" className="border-owlet-teal text-owlet-teal hover:bg-owlet-teal hover:text-white px-8 py-4 text-lg">
                  Join Coach Waitlist
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Discovery Call Section - Commented out for launch, will add back tomorrow */}
      {/*
      <section className="py-12 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <h2 className="text-3xl md:text-4xl font-serif font-bold text-midnight-indigo mb-4">
              What's Top of Mind for You?
            </h2>
            <p className="text-xl text-owlet-teal max-w-3xl mx-auto leading-relaxed">
              We want to hear from you! Are you an executive coach, HR or people operations leader, or a leader who has had a transformative coaching experience? We're building the future of executive coaching, and that means we need to understand what truly matters to you. If you'd like to share your insights and help shape this vision, we'd love to chat.
            </p>
          </div>

          <Card className="border-cloud-grey/30 shadow-lg">
            <CardContent className="p-8">
              {isSubmitted ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <h3 className="text-2xl font-bold text-midnight-indigo mb-2">Thank You!</h3>
                  <p className="text-owlet-teal mb-6">
                    We've received your insights and will be in touch soon to schedule a conversation.
                  </p>
                  <Button
                    onClick={() => setIsSubmitted(false)}
                    variant="outline"
                    className="border-midnight-indigo text-midnight-indigo hover:bg-midnight-indigo hover:text-white"
                  >
                    Submit Another Response
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label htmlFor="firstName" className="block text-sm font-medium text-midnight-indigo">
                        First Name *
                      </label>
                      <input
                        id="firstName"
                        name="firstName"
                        type="text"
                        required
                        className="w-full px-3 py-2 border border-cloud-grey/30 rounded-md focus:outline-none focus:ring-2 focus:ring-owlet-teal focus:border-owlet-teal"
                      />
                    </div>
                    <div className="space-y-2">
                      <label htmlFor="lastName" className="block text-sm font-medium text-midnight-indigo">
                        Last Name *
                      </label>
                      <input
                        id="lastName"
                        name="lastName"
                        type="text"
                        required
                        className="w-full px-3 py-2 border border-cloud-grey/30 rounded-md focus:outline-none focus:ring-2 focus:ring-owlet-teal focus:border-owlet-teal"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="email" className="block text-sm font-medium text-midnight-indigo">
                      Email Address *
                    </label>
                    <input
                      id="email"
                      name="email"
                      type="email"
                      required
                      className="w-full px-3 py-2 border border-cloud-grey/30 rounded-md focus:outline-none focus:ring-2 focus:ring-owlet-teal focus:border-owlet-teal"
                    />
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="role" className="block text-sm font-medium text-midnight-indigo">
                      Role *
                    </label>
                    <select
                      id="role"
                      name="role"
                      required
                      className="w-full px-3 py-2 border border-cloud-grey/30 rounded-md focus:outline-none focus:ring-2 focus:ring-owlet-teal focus:border-owlet-teal"
                    >
                      <option value="">Select your role</option>
                      <option value="executive-coach">Executive Coach</option>
                      <option value="hr-leader">HR Leader</option>
                      <option value="people-ops-leader">People Ops Leader</option>
                      <option value="executive-with-coaching">Executive with Coaching Experience</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="company" className="block text-sm font-medium text-midnight-indigo">
                      Company/Organization
                    </label>
                    <input
                      id="company"
                      name="company"
                      type="text"
                      className="w-full px-3 py-2 border border-cloud-grey/30 rounded-md focus:outline-none focus:ring-2 focus:ring-owlet-teal focus:border-owlet-teal"
                    />
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="feedback" className="block text-sm font-medium text-midnight-indigo">
                      What's one thing about executive coaching that you wish worked better?
                    </label>
                    <textarea
                      id="feedback"
                      name="feedback"
                      rows={4}
                      className="w-full px-3 py-2 border border-cloud-grey/30 rounded-md focus:outline-none focus:ring-2 focus:ring-owlet-teal focus:border-owlet-teal"
                      placeholder="Share your thoughts..."
                    />
                  </div>

                  <div className="pt-4">
                    <Button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full bg-midnight-indigo hover:bg-midnight-indigo/90 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 text-lg"
                    >
                      {isSubmitting ? 'Submitting...' : 'Share Your Insights'}
                    </Button>
                  </div>
                </form>
              )}
            </CardContent>
          </Card>
        </div>
      </section>
      */}
    </div>
  );
}
