"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/ui/page-header";
import { AppLayout } from "@/components/layout/AppLayout";
import { ThreeIconNav } from "@/components/navigation/ThreeIconNav";
import { Check, Target } from "lucide-react";

export default function PricingPage() {
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
      price: "$39/month",
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
        "Queue feedback moments for efficient workflow",
        "Simplify scheduling and billing",
        "$100 credit for every client added"
      ],
      cta: "Start 14-Day Trial",
      ctaVariant: "default" as const
    }
  ];

  return (
    <AppLayout>
      <ThreeIconNav />
      <div className="container mx-auto px-4 py-8 md:pt-20 pb-20">
        {/* Page Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold tracking-tight mb-4">
            Arete is a shared platform for clients and coaches
          </h1>
          <PageHeader
            title="Choose Your Growth Journey"
            className="text-center"
          />
        </div>

        {/* Pricing Tiers Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
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
                >
                  {tier.cta}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

      </div>
    </AppLayout>
  );
}