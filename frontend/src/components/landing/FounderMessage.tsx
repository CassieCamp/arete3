import React from 'react';
import Image from 'next/image';
import LinkedInIcon from '../icons/LinkedInIcon';
import WebsiteIcon from '../icons/WebsiteIcon';

const FounderMessage: React.FC = () => {
  return (
    <section className="bg-background py-16 sm:py-24">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="text-center">
          <h2 className="text-4xl font-bold font-serif text-foreground mb-6">
            I built the coaching app of my dreams
          </h2>
          <div className="prose prose-lg max-w-none text-foreground/80 space-y-4">
            <p>
              I'm a 20+ year startup veteran, product exec, and coach who's had multiple coaches since 2019 - from boutique executive firms to solo practitioners to peer circles. I've also coached startup founders and AI/ML engineers on retainer. I know this space from both sides.
            </p>
            <p>
              The reality? Coaching has incredible potential that technology hasn't fully unlocked yet. But here's the thing - while people are increasingly turning to AI for coaching, my worst fear is leaders just talking to robots instead of cultivating deep relationships and practicing self-reflection with humans. But the magic happens when AI serves human connection - amplifying coaches' insights and deepening the work between sessions and between coaches.
            </p>
            <p>
              My goal: Support the coaching industry with AI that empowers coaches, not replaces them. For leaders, I'm building Arete to be your well-worn journal throughout your career - reusable across jobs and coaches, helping you stay consistent with self-reflection between sessions. I hope you'll join the waitlist.
            </p>
          </div>
          
          {/* --- Closing Unit --- */}
          <div className="mt-12 pt-8 border-t border-border/50 flex justify-end">
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="font-mono text-2xl text-foreground">
                  -Cassie
                </p>
                <div className="mt-2 flex items-center justify-end gap-4">
                  <a href="https://cassiecamp.com" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-primary transition-colors">
                    <WebsiteIcon className="w-6 h-6" />
                  </a>
                  <a href="https://www.linkedin.com/in/cassandracampbell/" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-primary transition-colors">
                    <LinkedInIcon className="w-6 h-6" />
                  </a>
                </div>
              </div>
              <div className="w-24 h-24 flex-shrink-0">
                <Image
                  src="/images/founder-headshot.jpg"
                  alt="Cassie Campbell"
                  width={96}
                  height={96}
                  className="rounded-full object-cover object-[center_35%] w-full h-full shadow-md"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FounderMessage;