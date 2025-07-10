"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle, Mail, Users, Zap } from 'lucide-react';
import Link from 'next/link';

export default function WaitlistSuccessPage() {

  return (
    <div className="min-h-screen bg-moonlight-ivory flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl border-cloud-grey/30 shadow-lg">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-secondary/20 rounded-full flex items-center justify-center">
            <CheckCircle className="w-8 h-8 text-secondary" />
          </div>
          <CardTitle className="text-2xl font-serif text-midnight-indigo">
            You're on the waitlist!
          </CardTitle>
          <CardDescription className="text-lg text-owlet-teal">
            Thank you for your interest in AI-enhanced executive coaching with Arete.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="bg-primary/5 p-6 rounded-lg">
            <h3 className="font-semibold text-midnight-indigo mb-3">What happens next?</h3>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <Mail className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-midnight-indigo">Email Confirmation</p>
                  <p className="text-sm text-owlet-teal">
                    You'll receive a confirmation email shortly with your waitlist position.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <Users className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-midnight-indigo">Review Process</p>
                  <p className="text-sm text-owlet-teal">
                    Our team will review your application and coaching needs.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <Zap className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-midnight-indigo">Early Access</p>
                  <p className="text-sm text-owlet-teal">
                    Approved users will receive an invitation to create their account and begin their coaching journey.
                  </p>
                </div>
              </div>
            </div>
          </div>


          <div className="text-center space-y-4">
            <p className="text-sm text-owlet-teal">
              Questions about your waitlist status? Contact us at{' '}
              <a href="mailto:hello@arete.coach" className="text-midnight-indigo hover:underline">
                hello@arete.coach
              </a>
            </p>
            
            <Link href="/">
              <Button variant="outline" className="border-midnight-indigo text-midnight-indigo hover:bg-midnight-indigo hover:text-white">
                Return to Homepage
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}