"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import { useState, useEffect, useRef } from "react";

export default function Home() {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
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
    const roles = formData.getAll('role');
    const data = {
      firstName: formData.get('firstName'),
      lastName: formData.get('lastName'),
      email: formData.get('email'),
      linkedinUrl: formData.get('linkedinUrl'),
      roles: roles,
      feedback: formData.get('feedback'),
      timestamp: new Date().toISOString()
    };

    try {
      // Submit to backend API
      const response = await fetch('http://localhost:8000/api/v1/discovery-form/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Discovery form submitted successfully:', result);
      
      setIsSubmitted(true);
    } catch (error) {
      console.error('Form submission error:', error);
      // Still show success to user even if API fails
      setIsSubmitted(true);
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
            <p className="text-base md:text-lg text-owlet-teal mb-12 max-w-4xl mx-auto leading-loose text-left px-10">
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

      {/* Discovery Conversation Section */}
      <section className="py-16 bg-white min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-start">
            {/* Left Column - Text Content */}
            <div className="lg:pr-8">
              <h2 className="text-3xl md:text-4xl font-serif font-bold text-midnight-indigo mb-8">
                What's Top of Mind for You?
              </h2>
              <p className="text-base md:text-lg text-owlet-teal leading-loose">
                We want to hear from you! Are you an executive coach, HR or people operations leader, or a leader who has had a transformative coaching experience? We're building the future of executive coaching, and that means we need to understand what truly matters to you. If you'd like to share your insights and help shape this vision, we'd love to chat.
              </p>
            </div>

            {/* Right Column - Form */}
            <div className="lg:pl-8">
              <Card className="border-cloud-grey/30 shadow-lg overflow-visible">
                <CardContent className="p-8 space-y-6">
              {isSubmitted ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <h3 className="text-2xl font-bold text-midnight-indigo mb-2">Thank You!</h3>
                  <p className="text-owlet-teal mb-6">
                    We've received your request and will be in touch soon to schedule a discovery conversation.
                  </p>
                  <Button
                    onClick={() => setIsSubmitted(false)}
                    variant="outline"
                    className="border-midnight-indigo text-midnight-indigo hover:bg-midnight-indigo hover:text-white"
                  >
                    Submit Another Request
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <input
                      id="firstName"
                      name="firstName"
                      type="text"
                      required
                      placeholder="First Name *"
                      className="w-full px-3 py-3 border border-cloud-grey/30 rounded-md focus:outline-none focus:ring-2 focus:ring-owlet-teal focus:border-owlet-teal"
                    />
                    <input
                      id="lastName"
                      name="lastName"
                      type="text"
                      required
                      placeholder="Last Name *"
                      className="w-full px-3 py-3 border border-cloud-grey/30 rounded-md focus:outline-none focus:ring-2 focus:ring-owlet-teal focus:border-owlet-teal"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <input
                      id="email"
                      name="email"
                      type="email"
                      required
                      placeholder="Email Address *"
                      className="w-full px-3 py-3 border border-cloud-grey/30 rounded-md focus:outline-none focus:ring-2 focus:ring-owlet-teal focus:border-owlet-teal"
                    />
                    <input
                      id="linkedinUrl"
                      name="linkedinUrl"
                      type="url"
                      placeholder="LinkedIn URL or Website"
                      className="w-full px-3 py-3 border border-cloud-grey/30 rounded-md focus:outline-none focus:ring-2 focus:ring-owlet-teal focus:border-owlet-teal"
                    />
                  </div>

                  <div className="space-y-3">
                    <p className="text-sm font-medium text-midnight-indigo mb-3">Select all that apply *</p>
                    <div className="grid grid-cols-2 gap-3">
                      <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="checkbox"
                          name="role"
                          value="leader-on-the-journey"
                          className="w-4 h-4 text-owlet-teal border-cloud-grey/30 rounded focus:ring-owlet-teal focus:ring-2"
                        />
                        <span className="text-sm text-midnight-indigo">Leader on the Journey</span>
                      </label>
                      <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="checkbox"
                          name="role"
                          value="executive-coach"
                          className="w-4 h-4 text-owlet-teal border-cloud-grey/30 rounded focus:ring-owlet-teal focus:ring-2"
                        />
                        <span className="text-sm text-midnight-indigo">Executive Coach</span>
                      </label>
                      <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="checkbox"
                          name="role"
                          value="hr-people-ops-leader"
                          className="w-4 h-4 text-owlet-teal border-cloud-grey/30 rounded focus:ring-owlet-teal focus:ring-2"
                        />
                        <span className="text-sm text-midnight-indigo">HR/People Ops Leader</span>
                      </label>
                      <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="checkbox"
                          name="role"
                          value="other"
                          className="w-4 h-4 text-owlet-teal border-cloud-grey/30 rounded focus:ring-owlet-teal focus:ring-2"
                        />
                        <span className="text-sm text-midnight-indigo">Other</span>
                      </label>
                    </div>
                  </div>

                  <textarea
                    id="feedback"
                    name="feedback"
                    rows={3}
                    className="w-full px-3 py-3 border border-cloud-grey/30 rounded-md focus:outline-none focus:ring-2 focus:ring-owlet-teal focus:border-owlet-teal"
                    placeholder="What's one thing about executive coaching that you wish worked better?"
                  />

                  <div className="pt-6 pb-2">
                    <Button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full bg-[#D6B370] hover:bg-[#D6B370]/90 disabled:opacity-50 disabled:cursor-not-allowed text-[#1B1E3C] py-4 text-lg font-semibold shadow-lg transition-all duration-200 hover:shadow-xl"
                    >
                      {isSubmitting ? 'Submitting...' : "Let's Connect"}
                    </Button>
                  </div>
                </form>
              )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
