import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function Home() {
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
              <Link href="/role-selection">
                <Button variant="outline" className="border-midnight-indigo text-midnight-indigo hover:bg-midnight-indigo hover:text-white">
                  Sign In
                </Button>
              </Link>
              <Link href="/role-selection">
                <Button className="bg-midnight-indigo hover:bg-midnight-indigo/90 text-white">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-serif font-bold text-midnight-indigo mb-6">
              Your partner in
              <span className="block text-metis-gold">executive transformation</span>
            </h1>
            <p className="text-xl md:text-2xl text-owlet-teal mb-8 max-w-3xl mx-auto leading-relaxed">
              AI-enhanced coaching that accelerates leadership development and drives meaningful change in your professional journey.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="/role-selection">
                <Button size="lg" className="bg-midnight-indigo hover:bg-midnight-indigo/90 text-white px-8 py-4 text-lg">
                  Transform Your Leadership
                </Button>
              </Link>
              <Link href="#features">
                <Button variant="outline" size="lg" className="border-owlet-teal text-owlet-teal hover:bg-owlet-teal hover:text-white px-8 py-4 text-lg">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-serif font-bold text-midnight-indigo mb-4">
              The sidekick for your executive coaching experience
            </h2>
            <p className="text-xl text-owlet-teal max-w-3xl mx-auto">
              Combining human expertise with AI insights to unlock your leadership potential
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="border-cloud-grey/30 hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-metis-gold/20 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-metis-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <CardTitle className="text-midnight-indigo">Session Insights</CardTitle>
                <CardDescription className="text-owlet-teal">
                  AI-powered analysis of your coaching sessions reveals patterns, breakthroughs, and actionable next steps.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-cloud-grey/30 hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-owlet-teal/20 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-owlet-teal" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <CardTitle className="text-midnight-indigo">Growth Tracking</CardTitle>
                <CardDescription className="text-owlet-teal">
                  Visualize your transformation journey with comprehensive progress tracking and milestone celebrations.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-cloud-grey/30 hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-midnight-indigo/20 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-midnight-indigo" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <CardTitle className="text-midnight-indigo">Goal Management</CardTitle>
                <CardDescription className="text-owlet-teal">
                  Set, track, and achieve meaningful goals with AI-powered suggestions and progress monitoring.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Coach Partnership Section */}
      <section className="py-20 bg-midnight-indigo text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-serif font-bold mb-4">
              Built with executive coaches and leaders
            </h2>
            <p className="text-xl text-cloud-grey max-w-3xl mx-auto">
              Arete enhances the coaching relationship with AI insights while preserving the human connection that drives transformation.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-2xl font-serif font-bold mb-6 text-metis-gold">
                For Executive Coaches
              </h3>
              <ul className="space-y-4 text-cloud-grey">
                <li className="flex items-start">
                  <svg className="w-6 h-6 text-metis-gold mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Gain deeper insights into client patterns and breakthroughs
                </li>
                <li className="flex items-start">
                  <svg className="w-6 h-6 text-metis-gold mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Track client progress across multiple sessions
                </li>
                <li className="flex items-start">
                  <svg className="w-6 h-6 text-metis-gold mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Enhance your coaching methodology with AI-powered insights
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-2xl font-serif font-bold mb-6 text-metis-gold">
                For Leaders & Executives
              </h3>
              <ul className="space-y-4 text-cloud-grey">
                <li className="flex items-start">
                  <svg className="w-6 h-6 text-metis-gold mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Accelerate your leadership development journey
                </li>
                <li className="flex items-start">
                  <svg className="w-6 h-6 text-metis-gold mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Visualize your growth and celebrate milestones
                </li>
                <li className="flex items-start">
                  <svg className="w-6 h-6 text-metis-gold mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Gain clarity on your transformation patterns
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Waitlist Sections */}
      <section className="py-20 bg-moonlight-ivory">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12">
            {/* Client Waitlist */}
            <Card className="border-cloud-grey/30 p-8">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl font-serif text-midnight-indigo mb-4">
                  Ready to transform your leadership?
                </CardTitle>
                <CardDescription className="text-owlet-teal text-lg">
                  Join our waitlist to be among the first to experience AI-enhanced executive coaching.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input 
                  type="email" 
                  placeholder="Enter your email address"
                  className="border-cloud-grey focus:border-midnight-indigo"
                />
                <Button className="w-full bg-midnight-indigo hover:bg-midnight-indigo/90 text-white">
                  Join Client Waitlist
                </Button>
                <p className="text-sm text-owlet-teal text-center">
                  Be the first to know when we launch
                </p>
              </CardContent>
            </Card>

            {/* Coach Waitlist */}
            <Card className="border-cloud-grey/30 p-8">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl font-serif text-midnight-indigo mb-4">
                  Are you an executive coach?
                </CardTitle>
                <CardDescription className="text-owlet-teal text-lg">
                  Partner with us to enhance your coaching practice with AI-powered insights.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input 
                  type="email" 
                  placeholder="Enter your email address"
                  className="border-cloud-grey focus:border-owlet-teal"
                />
                <Button className="w-full bg-owlet-teal hover:bg-owlet-teal/90 text-white">
                  Join Coach Waitlist
                </Button>
                <p className="text-sm text-owlet-teal text-center">
                  Get early access to our coaching platform
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-midnight-indigo text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-serif font-bold text-metis-gold mb-4">
              Arete
            </h3>
            <p className="text-cloud-grey mb-6">
              Excellence in executive coaching, enhanced by AI
            </p>
            <div className="flex justify-center space-x-6">
              <Link href="/role-selection" className="text-cloud-grey hover:text-metis-gold transition-colors">
                Get Started
              </Link>
              <Link href="#features" className="text-cloud-grey hover:text-metis-gold transition-colors">
                Features
              </Link>
              <Link href="mailto:hello@arete.coach" className="text-cloud-grey hover:text-metis-gold transition-colors">
                Contact
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
