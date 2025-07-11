"use client";

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { useClerk, useUser, UserButton } from '@clerk/nextjs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AuthDropdown } from '@/components/auth/AuthDropdown';
import { Check } from 'lucide-react';

export default function HomePage() {
  const { user } = useAuth();
  const router = useRouter();
  const { redirectToSignIn } = useClerk();
  const { isSignedIn } = useUser();
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    linkedinUrl: '',
    roles: [] as string[],
    insights: ''
  });

  const pricingTiers = [
    {
      id: "growth-essentials",
      name: "Client Growth Essentials",
      price: "FREE",
      popular: false,
      features: [
        "Basic journey tracking",
        "1 AI session summary/month",
        "Up to 3 active goals",
        "Solo player mode without a coach",
        "Get $50 credit for any client referral that signs up and makes their first payment and $100 for any coach that signs up and makes their first payment"
      ],
      cta: "Start Free",
      ctaVariant: "outline" as const
    },
    {
      id: "client-solo",
      name: "Client Growth Enhanced",
      price: "$79/month",
      popular: true,
      features: [
        "Unlimited AI session analysis",
        "Progress tracking & highlights",
        "One lifelong journey across all coaches*",
        "Covers coaching costs for coaches not on the Pro plan**"
      ],
      cta: "Start 14-Day Trial",
      ctaVariant: "default" as const,
      smallPrint: "* Between active coaching periods, hibernation mode available at $5/month to preserve your journey data.\n** If your coach upgrades to the Coach Professional plan, you'll receive a credit for one quarter ($237)."
    },
    {
      id: "coach-professional",
      name: "Coach Professional",
      price: "$199/month",
      popular: false,
      features: [
        "Leverage AI to amplify your impact",
        "Manage multiple clients",
        "Get out of Google Docs and WhatsApp",
        "Queue feedback moments for efficient workflow",
        "Simplify scheduling and billing",
        "$100 credit for every client added"
      ],
      cta: "Start 14-Day Trial",
      ctaVariant: "default" as const
    }
  ];

  const handleRoleChange = (role: string, checked: boolean) => {
    setFormData(prev => ({
      ...prev,
      roles: checked 
        ? [...prev.roles, role]
        : prev.roles.filter(r => r !== role)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission - could integrate with backend API
    console.log('Form submitted:', formData);
    // For now, redirect to waitlist success or show confirmation
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-card/95 backdrop-blur-sm border-b border-border">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="text-2xl font-bold font-serif text-foreground">
            Arete
          </div>
          <div className="flex gap-4 items-center">
            {isSignedIn ? (
              <>
                <Button
                  variant="ghost"
                  onClick={() => router.push('/journey')}
                >
                  My Arete
                </Button>
                <UserButton
                  appearance={{
                    elements: {
                      avatarBox: "w-8 h-8"
                    }
                  }}
                />
              </>
            ) : (
              <>
                <AuthDropdown variant="ghost" />
                <Button
                  onClick={() => router.push('/waitlist')}
                >
                  Join Waitlist
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto max-w-4xl text-center">
          <h1 className="text-5xl md:text-6xl font-bold font-serif text-foreground mb-8 leading-tight">
            Your partner in<br />
            executive transformation
          </h1>
          
          <div className="max-w-2xl mx-auto space-y-6 text-lg text-muted-foreground mb-12">
            <p>
              Excellence isn't perfection. It's the courage to become who you're truly meant to be. The 
              ancient Greeks called this arete—your highest potential realized. That depth of courage 
              deserves a guide who understands the journey.
            </p>
            
            <p>
              We believe coaching should be as normal for leaders as it is for athletes. Enter your human 
              executive coach. Our role is simple: honor that sacred relationship by providing AI that gently 
              amplifies the wisdom, never replacing the human connection that drives real growth.
            </p>
          </div>

          <div className="flex justify-center">
            <Button
              size="lg"
              className="px-8 py-3 text-lg"
              onClick={() => router.push('/waitlist')}
            >
              Join Waitlist
            </Button>
          </div>
        </div>
      </section>

      {/* Discovery Form Section */}
      <section className="py-16 px-4 bg-background">
        <div className="container mx-auto max-w-4xl">
          <div className="space-y-12">
            {/* Description */}
            <div className="text-center">
              <h2 className="text-4xl font-bold font-serif text-foreground mb-6">
                What's Top of Mind for You?
              </h2>
              <div className="text-lg text-muted-foreground space-y-4 max-w-3xl mx-auto">
                <p>
                  We want to hear from you! Are you an executive coach, HR or people operations leader, or a leader
                  who has had a transformative coaching experience?
                </p>
                <p>
                  We're building the future of executive coaching, and that means we need to understand what truly matters
                  to you. If you'd like to share your insights and help shape this vision, we'd love to chat.
                </p>
              </div>
            </div>

            {/* Form */}
            <Card className="border-border max-w-2xl mx-auto">
              <CardContent className="p-8">
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <Input
                      placeholder="First Name *"
                      value={formData.firstName}
                      onChange={(e) => setFormData(prev => ({ ...prev, firstName: e.target.value }))}
                      required
                      className="border-input"
                    />
                    <Input
                      placeholder="Last Name *"
                      value={formData.lastName}
                      onChange={(e) => setFormData(prev => ({ ...prev, lastName: e.target.value }))}
                      required
                      className="border-input"
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <Input
                      type="email"
                      placeholder="Email Address *"
                      value={formData.email}
                      onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                      required
                      className="border-input"
                    />
                    <Input
                      placeholder="LinkedIn URL or Website"
                      value={formData.linkedinUrl}
                      onChange={(e) => setFormData(prev => ({ ...prev, linkedinUrl: e.target.value }))}
                      className="border-input"
                    />
                  </div>

                  <div>
                    <label className="text-sm font-medium text-foreground mb-3 block">
                      Select all that apply *
                    </label>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id="leader"
                          checked={formData.roles.includes('Leader on the Journey')}
                          onCheckedChange={(checked) => 
                            handleRoleChange('Leader on the Journey', checked as boolean)
                          }
                        />
                        <label htmlFor="leader" className="text-sm text-foreground">
                          Leader on the Journey
                        </label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id="coach"
                          checked={formData.roles.includes('Executive Coach')}
                          onCheckedChange={(checked) => 
                            handleRoleChange('Executive Coach', checked as boolean)
                          }
                        />
                        <label htmlFor="coach" className="text-sm text-foreground">
                          Executive Coach
                        </label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id="hr"
                          checked={formData.roles.includes('HR/People Ops Leader')}
                          onCheckedChange={(checked) => 
                            handleRoleChange('HR/People Ops Leader', checked as boolean)
                          }
                        />
                        <label htmlFor="hr" className="text-sm text-foreground">
                          HR/People Ops Leader
                        </label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id="other"
                          checked={formData.roles.includes('Other')}
                          onCheckedChange={(checked) => 
                            handleRoleChange('Other', checked as boolean)
                          }
                        />
                        <label htmlFor="other" className="text-sm text-foreground">
                          Other
                        </label>
                      </div>
                    </div>
                  </div>

                  <Textarea
                    placeholder="What's one thing about executive coaching that you wish worked better?"
                    value={formData.insights}
                    onChange={(e) => setFormData(prev => ({ ...prev, insights: e.target.value }))}
                    rows={4}
                    className="border-input"
                  />

                  <Button 
                    type="submit" 
                    className="w-full"
                    size="lg"
                  >
                    Let's Connect
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-16 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold font-serif text-foreground mb-4">
              Choose Your Growth Journey
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Arete is a shared platform for clients and coaches
            </p>
          </div>

          {/* Pricing Tiers Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pricingTiers.map((tier) => (
              <Card key={tier.id} className="relative flex flex-col h-full">
                {tier.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <Badge variant="default" className="bg-primary text-primary-foreground">
                      MOST POPULAR
                    </Badge>
                  </div>
                )}
                
                <CardHeader className="text-center pb-4">
                  <CardTitle className="text-xl font-semibold mb-2">
                    {tier.name}
                  </CardTitle>
                  <div className="text-3xl font-bold text-primary mb-4">
                    {tier.price}
                  </div>
                </CardHeader>

                <CardContent className="flex-1 flex flex-col">
                  <ul className="space-y-3 mb-6 flex-1">
                    {tier.features.map((feature, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <Check className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-muted-foreground">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {tier.smallPrint && (
                    <p className="text-xs text-muted-foreground mb-4 italic whitespace-pre-line">
                      {tier.smallPrint}
                    </p>
                  )}

                  <Button
                    variant={tier.ctaVariant}
                    className="w-full mt-auto"
                    size="lg"
                    onClick={() => router.push('/waitlist')}
                  >
                    Join Waitlist
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}