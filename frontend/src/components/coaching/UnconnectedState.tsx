"use client";

import { InterestForm } from "./InterestForm";
import { Users, Heart, Target } from "lucide-react";

export function UnconnectedState() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Welcome Section */}
      <div className="text-center space-y-6">
        <div className="flex justify-center">
          <div className="p-4 bg-primary/10 rounded-full">
            <Users className="w-12 h-12 text-primary" />
          </div>
        </div>
        
        <div className="space-y-4">
          <h1 className="text-3xl font-bold text-foreground font-serif">
            Welcome to Coaching
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            The coaching app of my dreams.
            Connect with experienced coaches who will guide you toward your goals 
            with tailored strategies and ongoing support.
          </p>
        </div>

        {/* Benefits Grid */}
        <div className="grid md:grid-cols-3 gap-6 mt-12 mb-12">
          <div className="text-center space-y-3">
            <div className="flex justify-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Target className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <h3 className="font-semibold text-foreground">Goal-Focused</h3>
            <p className="text-sm text-muted-foreground">
              Work with coaches who understand your unique objectives and create actionable plans to achieve them.
            </p>
          </div>
          
          <div className="text-center space-y-3">
            <div className="flex justify-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <Users className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <h3 className="font-semibold text-foreground">Expert Guidance</h3>
            <p className="text-sm text-muted-foreground">
              Connect with experienced coaches who bring proven methodologies and personalized insights.
            </p>
          </div>
          
          <div className="text-center space-y-3">
            <div className="flex justify-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Heart className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <h3 className="font-semibold text-foreground">Ongoing Support</h3>
            <p className="text-sm text-muted-foreground">
              Receive continuous encouragement and accountability to stay motivated on your journey.
            </p>
          </div>
        </div>
      </div>

      {/* Interest Form Section */}
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-foreground mb-2">
            Ready to Get Started?
          </h2>
          <p className="text-muted-foreground">
            Tell us about your goals and we'll match you with the perfect coach.
          </p>
        </div>
        
        <InterestForm />
      </div>
    </div>
  );
}