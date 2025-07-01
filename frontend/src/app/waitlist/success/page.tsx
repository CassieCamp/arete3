"use client";

import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle, Mail, Users, Zap } from 'lucide-react';
import Link from 'next/link';

export default function WaitlistSuccessPage() {
  const searchParams = useSearchParams();
  const role = searchParams.get('role') || 'client';
  const isCoach = role === 'coach';

  return (
    <div className="min-h-screen bg-moonlight-ivory flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl border-cloud-grey/30 shadow-lg">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          <CardTitle className="text-2xl font-serif text-midnight-indigo">
            You're on the waitlist!
          </CardTitle>
          <CardDescription className="text-lg text-owlet-teal">
            {isCoach 
              ? "Thank you for your interest in partnering with Arete as an executive coach."
              : "Thank you for your interest in AI-enhanced executive coaching with Arete."
            }
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="bg-blue-50 p-6 rounded-lg">
            <h3 className="font-semibold text-midnight-indigo mb-3">What happens next?</h3>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <Mail className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-midnight-indigo">Email Confirmation</p>
                  <p className="text-sm text-owlet-teal">
                    You'll receive a confirmation email shortly with your waitlist position.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <Users className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-midnight-indigo">Review Process</p>
                  <p className="text-sm text-owlet-teal">
                    {isCoach 
                      ? "Our team will review your coaching background and experience."
                      : "Our team will review your application and coaching needs."
                    }
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <Zap className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-midnight-indigo">Early Access</p>
                  <p className="text-sm text-owlet-teal">
                    {isCoach 
                      ? "Approved coaches will receive early access to our platform and training materials."
                      : "Approved users will receive an invitation to create their account and begin their coaching journey."
                    }
                  </p>
                </div>
              </div>
            </div>
          </div>

          {isCoach && (
            <div className="bg-metis-gold/10 p-6 rounded-lg">
              <h3 className="font-semibold text-midnight-indigo mb-2">For Executive Coaches</h3>
              <p className="text-sm text-owlet-teal mb-3">
                While you wait, we encourage you to:
              </p>
              <ul className="text-sm text-owlet-teal space-y-1">
                <li>• Review our coaching methodology and AI integration approach</li>
                <li>• Consider how AI insights could enhance your current practice</li>
                <li>• Think about the types of executives you'd like to work with</li>
              </ul>
            </div>
          )}

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