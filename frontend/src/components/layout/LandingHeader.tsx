"use client";

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useClerk, useUser, UserButton } from '@clerk/nextjs';
import { Button } from '@/components/ui/button';
import { AuthDropdown } from '@/components/auth/AuthDropdown';

const LandingHeader = () => {
  const { isSignedIn } = useUser();

  return (
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
  );
};

export default LandingHeader;