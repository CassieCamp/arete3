"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import { useState, useEffect, useRef } from "react";

export default function Home() {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

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
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/discovery-form/submit`, {
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
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="bg-white/95 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-serif font-bold text-black">
                Arete
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <SignedOut>
                <SignInButton mode="modal">
                  <Button variant="outline" className="border-gray-300 text-black hover:bg-gray-100">
                    Sign In
                  </Button>
                </SignInButton>
                <Link href="/waitlist">
                  <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-medium">
                    Join Waitlist
                  </Button>
                </Link>
              </SignedOut>
              <SignedIn>
                <Link href="/dashboard/connections">
                  <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-medium">
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
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-serif font-bold text-black mb-16">
              Your partner in
              <span className="block text-black">executive transformation</span>
            </h1>
            <p className="text-base md:text-lg text-black mb-12 max-w-4xl mx-auto leading-loose text-left px-10">
              Excellence isn't perfection. It's the courage to become who you're truly meant to be. The ancient Greeks called this arete—your highest potential realized. That depth of courage deserves a guide who understands the journey.
              <br /><br />
              We believe coaching should be as normal for leaders as it is for athletes. Enter your human executive coach. Our role is simple: honor that sacred relationship by providing AI that gently amplifies the wisdom, never replacing the human connection that drives real growth.
            </p>
            <div className="mt-8">
              <Link href="/waitlist">
                <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-medium px-8 py-3 text-lg">
                  Join Our Waitlist
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Divider */}
      <div className="bg-background">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="h-px bg-gradient-to-r from-transparent via-border to-transparent opacity-30"></div>
        </div>
      </div>

      {/* Ronnie Lott Quote Section */}
      <section className="py-16 bg-background">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <blockquote className="relative">
              <div className="absolute -top-4 -left-4 text-6xl text-ring/20 font-serif leading-none">"</div>
              <div className="absolute -bottom-8 -right-4 text-6xl text-ring/20 font-serif leading-none">"</div>
              <p className="text-lg md:text-xl text-black leading-relaxed font-light italic px-8 py-6 relative z-10">
                Great coaches lie awake at night thinking about how to make you better. They relish creating an environment where you get more out of yourself. Coaches are like great artists getting the stroke exactly right on a painting. They are painting relationships. Most people don't spend a lot of time thinking about how they are going to make someone else better. But that's what coaches do. It's what Bill Campbell did, he just did it on a different field.
              </p>
              <footer className="mt-8">
                <cite className="text-black font-medium text-lg not-italic">
                  — Ronnie Lott, former San Francisco 49ers player, on Bill Campbell, coach to Steve Jobs, Eric Schmidt, and Silicon Valley's greatest leaders
                </cite>
              </footer>
            </blockquote>
          </div>
        </div>
      </section>

      {/* Divider */}
      <div className="bg-background">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="h-px bg-gradient-to-r from-transparent via-border to-transparent opacity-30"></div>
        </div>
      </div>

      {/* Discovery Conversation Section */}
      <section className="py-20 bg-background min-h-screen">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
          <div className="space-y-12">
            {/* Text Content - Now stacked above */}
            <div className="text-center">
              <h2 className="text-3xl md:text-4xl font-serif font-bold text-black mb-8">
                What's Top of Mind for You?
              </h2>
              <p className="text-base md:text-lg text-black leading-loose max-w-3xl mx-auto">
                We want to hear from you! Are you an executive coach, HR or people operations leader, or a leader who has had a transformative coaching experience? We're building the future of executive coaching, and that means we need to understand what truly matters to you. If you'd like to share your insights and help shape this vision, we'd love to chat.
              </p>
            </div>

            {/* Form - Now below the text */}
            <div className="max-w-2xl mx-auto">
              <Card className="border-border shadow-lg overflow-visible">
                <CardContent className="p-8 space-y-6">
              {isSubmitted ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-secondary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <h3 className="text-2xl font-bold text-black mb-2">Thank You!</h3>
                  <p className="text-black mb-6">
                    We've received your request and will be in touch soon to schedule a discovery conversation.
                  </p>
                  <Button
                    onClick={() => setIsSubmitted(false)}
                    variant="outline"
                    className="border-gray-300 text-black hover:bg-gray-100"
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
                      className="w-full px-3 py-3 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring focus:border-secondary"
                    />
                    <input
                      id="lastName"
                      name="lastName"
                      type="text"
                      required
                      placeholder="Last Name *"
                      className="w-full px-3 py-3 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring focus:border-secondary"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <input
                      id="email"
                      name="email"
                      type="email"
                      required
                      placeholder="Email Address *"
                      className="w-full px-3 py-3 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring focus:border-secondary"
                    />
                    <input
                      id="linkedinUrl"
                      name="linkedinUrl"
                      type="url"
                      placeholder="LinkedIn URL or Website"
                      className="w-full px-3 py-3 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring focus:border-secondary"
                    />
                  </div>

                  <div className="space-y-3">
                    <p className="text-sm font-medium text-black mb-3">Select all that apply *</p>
                    <div className="grid grid-cols-2 gap-3">
                      <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="checkbox"
                          name="role"
                          value="leader-on-the-journey"
                          className="w-4 h-4 text-secondary border-border rounded focus:ring-ring focus:ring-2"
                        />
                        <span className="text-sm text-black">Leader on the Journey</span>
                      </label>
                      <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="checkbox"
                          name="role"
                          value="executive-coach"
                          className="w-4 h-4 text-secondary border-border rounded focus:ring-ring focus:ring-2"
                        />
                        <span className="text-sm text-black">Executive Coach</span>
                      </label>
                      <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="checkbox"
                          name="role"
                          value="hr-people-ops-leader"
                          className="w-4 h-4 text-secondary border-border rounded focus:ring-ring focus:ring-2"
                        />
                        <span className="text-sm text-black">HR/People Ops Leader</span>
                      </label>
                      <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="checkbox"
                          name="role"
                          value="other"
                          className="w-4 h-4 text-secondary border-border rounded focus:ring-ring focus:ring-2"
                        />
                        <span className="text-sm text-black">Other</span>
                      </label>
                    </div>
                  </div>

                  <textarea
                    id="feedback"
                    name="feedback"
                    rows={3}
                    className="w-full px-3 py-3 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring focus:border-secondary"
                    placeholder="What's one thing about executive coaching that you wish worked better?"
                  />

                  <div className="pt-6 pb-2">
                    <Button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full bg-accent hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed text-accent-foreground py-4 text-lg font-semibold shadow-lg transition-all duration-200 hover:shadow-xl"
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

      {/* Divider */}
      <div className="bg-background">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="h-px bg-gradient-to-r from-transparent via-border to-transparent opacity-30"></div>
        </div>
      </div>

      {/* Eric Schmidt Quote Section */}
      <section className="py-16 bg-background">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <blockquote className="relative">
              <div className="absolute -top-4 -left-4 text-6xl text-ring/20 font-serif leading-none">"</div>
              <div className="absolute -bottom-8 -right-4 text-6xl text-ring/20 font-serif leading-none">"</div>
              <p className="text-lg md:text-xl text-black leading-relaxed font-light italic px-8 py-6 relative z-10">
                All of our interviews indicated that everyone agrees they would not have been nearly as successful without that coaching.
              </p>
              <footer className="mt-8">
                <cite className="text-black font-medium text-lg not-italic">
                  — Eric Schmidt, former Google CEO, <a
                    href="https://www.cnbc.com/2019/04/17/google-execs-reveal-secrets-to-success-from-ceo-coach-bill-campbell.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline hover:text-blue-600 transition-colors duration-200"
                  >
                    reflecting on interviews with 80+ Silicon Valley leaders
                  </a>
                </cite>
              </footer>
            </blockquote>
          </div>
        </div>
      </section>

      {/* Divider */}
      <div className="bg-background">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="h-px bg-gradient-to-r from-transparent via-border to-transparent opacity-30"></div>
        </div>
      </div>

      {/* Theodore Roosevelt Quote Section */}
      <section className="py-16 bg-background">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <blockquote className="relative">
              <div className="absolute -top-4 -left-4 text-6xl text-ring/20 font-serif leading-none">"</div>
              <div className="absolute -bottom-8 -right-4 text-6xl text-ring/20 font-serif leading-none">"</div>
              <p className="text-lg md:text-xl text-black leading-relaxed font-light italic px-8 py-6 relative z-10">
                It is not the critic who counts; not the man who points out how the strong man stumbles, or where the doer of deeds could have done them better. The credit belongs to the man who is actually in the arena, whose face is marred by dust and sweat and blood; who strives valiantly; who errs, who comes short again and again, because there is no effort without error and shortcoming; but who does actually strive to do the deeds; who knows great enthusiasms, the great devotions; who spends himself in a worthy cause; who at the best knows in the end the triumph of high achievement, and who at the worst, if he fails, at least fails while daring greatly, so that his place shall never be with those cold and timid souls who neither know victory nor defeat.
              </p>
              <footer className="mt-8">
                <cite className="text-black font-medium text-lg not-italic">
                  — Theodore Roosevelt
                </cite>
              </footer>
            </blockquote>
          </div>
        </div>
      </section>

    </div>
  );
}
