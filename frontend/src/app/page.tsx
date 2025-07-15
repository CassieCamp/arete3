"use client";

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useClerk, useUser, UserButton } from '@clerk/nextjs';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AuthDropdown } from '@/components/auth/AuthDropdown';
import { Check } from 'lucide-react';
import FounderMessage from '@/components/landing/FounderMessage';
import StatsSection from '@/components/landing/StatsSection';
import WhyArete from '@/components/landing/WhyArete';
import { CenterIcon } from '@/components/icons/CenterIcon';

export default function HomePage() {
  const router = useRouter();
  const { redirectToSignIn } = useClerk();
  const { user, isSignedIn } = useUser();

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
      cta: "Join the Waitlist",
      ctaVariant: "outline" as const
    },
    {
      id: "client-solo",
      name: "Client Growth Enhanced",
      price: "$39/month",
      popular: true,
      features: [
        "Unlimited AI session analysis",
        "Progress tracking & highlights",
        "One lifelong journey across all coaches*",
        "Covers coaching costs for coaches not on the Pro plan**"
      ],
      cta: "Join the Waitlist",
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
      cta: "Join the Waitlist",
      ctaVariant: "default" as const
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-card/95 backdrop-blur-sm border-b border-border">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold font-serif text-foreground hover:opacity-80 transition-opacity">
            Arete
          </Link>
          <div className="flex gap-4 items-center">
            {isSignedIn ? (
              <>
                <Link href="/member/journey">
                  <Button variant="ghost">
                    My Arete
                  </Button>
                </Link>
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
                <Link href="https://forms.gle/o2oQGGgMTv8RgdyV6" target="_blank" rel="noopener noreferrer">
                  <Button>
                    Join the Waitlist
                  </Button>
                </Link>
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
            <Link href="https://forms.gle/o2oQGGgMTv8RgdyV6" target="_blank" rel="noopener noreferrer">
              <Button
                size="lg"
                className="px-8 py-3 text-lg"
              >
                Join the Waitlist
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <FounderMessage />


      <StatsSection />

      <WhyArete />

      <div className="flex justify-center py-12">
        <CenterIcon />
      </div>

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
            <div className="text-center">
              <Link href="https://forms.gle/o2oQGGgMTv8RgdyV6" target="_blank" rel="noopener noreferrer">
                <Button size="lg" className="px-8 py-3 text-lg">
                  Join the Waitlist
                </Button>
              </Link>
            </div>
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

                  <Link
                    href={tier.cta === 'Join the Waitlist' ? "https://forms.gle/o2oQGGgMTv8RgdyV6" : "/sign-up"}
                    className="w-full"
                    target={tier.cta === 'Join the Waitlist' ? "_blank" : undefined}
                    rel={tier.cta === 'Join the Waitlist' ? "noopener noreferrer" : undefined}
                  >
                    <Button
                      variant={tier.ctaVariant}
                      className="w-full mt-auto"
                      size="lg"
                    >
                      {tier.cta}
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}