"use client";

import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { AppLayout } from "@/components/layout/AppLayout";
import { ThreeIconNav } from "@/components/navigation/ThreeIconNav";
import {
  Heart,
  Zap,
  Brain,
  MapPin,
  User,
  FileText,
  Settings,
  Tent
} from "lucide-react";

export default function BasecampPage() {
  const basecampCards = [
    {
      id: "values",
      title: "My Values",
      description: "Explore and define your core values",
      icon: Heart,
      href: null // Placeholder - no link yet
    },
    {
      id: "energy",
      title: "My Energy",
      description: "Understand your energy patterns and sources",
      icon: Zap,
      href: null // Placeholder - no link yet
    },
    {
      id: "personality",
      title: "My Personality",
      description: "Discover your personality traits and preferences",
      icon: Brain,
      href: null // Placeholder - no link yet
    },
    {
      id: "destinations",
      title: "My Destinations",
      description: "Set and track your goals and aspirations",
      icon: MapPin,
      href: null // Placeholder - no link yet
    },
    {
      id: "documents",
      title: "Documents",
      description: "Upload and manage your coaching documents",
      icon: FileText,
      href: "/documents"
    },
    {
      id: "profile",
      title: "Profile",
      description: "Manage your personal information and preferences",
      icon: User,
      href: "/profile/edit"
    },
    {
      id: "settings",
      title: "Settings",
      description: "Configure your account and application settings",
      icon: Settings,
      href: "/settings"
    }
  ];

  return (
    <AppLayout>
      <ThreeIconNav />
      <div className="container mx-auto px-4 py-8 md:pt-20 pb-20">
        <PageHeader
          icon={Tent}
          title="Basecamp"
          subtitle=""
        />
        
        <div className="w-full max-w-4xl mx-auto">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {basecampCards.map((card) => {
              const IconComponent = card.icon;
              
              const cardContent = (
                <Card className="h-full transition-all hover:shadow-md hover:scale-[1.02] cursor-pointer">
                  <CardHeader className="text-center">
                    <div className="mx-auto mb-4 p-3 rounded-full bg-primary w-fit">
                      <IconComponent className="w-8 h-8 text-slate-100" />
                    </div>
                    <CardTitle className="text-xl">{card.title}</CardTitle>
                    <CardDescription className="text-center">
                      {card.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="flex justify-center">
                      {card.href ? (
                        <Button variant="outline" size="sm">
                          Open
                        </Button>
                      ) : (
                        <Button variant="outline" size="sm" disabled>
                          Coming Soon
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );

              // Wrap with Link if href exists, otherwise return the card directly
              return card.href ? (
                <Link key={card.id} href={card.href} className="block">
                  {cardContent}
                </Link>
              ) : (
                <div key={card.id}>
                  {cardContent}
                </div>
              );
            })}
          </div>

          {/* Ted Lasso Quote */}
          <div className="mt-12 text-center">
            <p className="text-lg italic text-slate-600 max-w-2xl mx-auto">
              "I think that's what coaching is all about: helping people become the best versions of themselves."
              <br />
              - Ted Lasso
            </p>
          </div>

        </div>
      </div>
    </AppLayout>
  );
}