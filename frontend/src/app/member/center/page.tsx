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
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import { CaveIcon } from "@/components/icons/CaveIcon";
import { useRef, useState, useEffect } from "react";

// Custom CSS for hiding scrollbar and ethereal glow effect
const scrollbarStyle = `
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
  
  .ethereal-glow {
    box-shadow: var(--shadow-xl);
    transform: scale(1.02);
    background: hsl(var(--card));
    border: 2px solid hsl(var(--primary) / 0.2);
  }
  
  .ethereal-glow::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    background: linear-gradient(45deg,
      hsl(var(--primary) / 0.1),
      hsl(var(--primary) / 0.3),
      hsl(var(--primary) / 0.1));
    border-radius: 50%;
    z-index: -1;
    animation: ethereal-pulse 3s ease-in-out infinite;
  }
  
  @keyframes ethereal-pulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 0.6; }
  }
`;

export default function CenterPage() {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);
  const [activeCardIndex, setActiveCardIndex] = useState(0);

  const centerCards = [
    {
      id: "values",
      title: "Values",
      description: "Explore and define your core values",
      icon: Heart,
      href: null // Placeholder - no link yet
    },
    {
      id: "energy",
      title: "Energy",
      description: "Understand your energy patterns and sources",
      icon: Zap,
      href: null // Placeholder - no link yet
    },
    {
      id: "personality",
      title: "Personality",
      description: "Discover your personality traits and preferences",
      icon: Brain,
      href: null // Placeholder - no link yet
    },
    {
      id: "destinations",
      title: "Destinations",
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

  // Check scroll position and update arrow visibility and active card
  const checkScrollPosition = () => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current;
      setShowLeftArrow(scrollLeft > 0);
      setShowRightArrow(scrollLeft < scrollWidth - clientWidth - 10);
      
      // Calculate which card is currently in view
      const cardWidth = 320; // Card width + gap
      const currentIndex = Math.round(scrollLeft / cardWidth);
      setActiveCardIndex(Math.min(currentIndex, centerCards.length - 1));
    }
  };

  // Handle scroll arrows
  const scrollTo = (direction: 'left' | 'right') => {
    if (scrollContainerRef.current) {
      const scrollAmount = 320; // Card width + gap
      const currentScroll = scrollContainerRef.current.scrollLeft;
      const targetScroll = direction === 'left'
        ? currentScroll - scrollAmount
        : currentScroll + scrollAmount;
      
      scrollContainerRef.current.scrollTo({
        left: targetScroll,
        behavior: 'smooth'
      });
    }
  };

  // Handle dot clicks to scroll to specific card
  const scrollToCard = (index: number) => {
    if (scrollContainerRef.current) {
      const scrollAmount = 320; // Card width + gap
      const targetScroll = index * scrollAmount;
      
      scrollContainerRef.current.scrollTo({
        left: targetScroll,
        behavior: 'smooth'
      });
    }
  };

  // Mouse drag functionality
  const handleMouseDown = (e: React.MouseEvent) => {
    if (scrollContainerRef.current) {
      setIsDragging(true);
      setStartX(e.pageX - scrollContainerRef.current.offsetLeft);
      setScrollLeft(scrollContainerRef.current.scrollLeft);
      scrollContainerRef.current.style.cursor = 'grabbing';
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !scrollContainerRef.current) return;
    e.preventDefault();
    const x = e.pageX - scrollContainerRef.current.offsetLeft;
    const walk = (x - startX) * 2; // Scroll speed multiplier
    scrollContainerRef.current.scrollLeft = scrollLeft - walk;
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    if (scrollContainerRef.current) {
      scrollContainerRef.current.style.cursor = 'grab';
    }
  };

  const handleMouseLeave = () => {
    setIsDragging(false);
    if (scrollContainerRef.current) {
      scrollContainerRef.current.style.cursor = 'grab';
    }
  };

  // Update arrow visibility on scroll
  useEffect(() => {
    const container = scrollContainerRef.current;
    if (container) {
      checkScrollPosition();
      container.addEventListener('scroll', checkScrollPosition);
      return () => container.removeEventListener('scroll', checkScrollPosition);
    }
  }, []);

  // Update arrow visibility on resize
  useEffect(() => {
    const handleResize = () => checkScrollPosition();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <AppLayout>
      <style jsx>{scrollbarStyle}</style>
      <ThreeIconNav />
      <div className="container mx-auto px-4 py-8 md:pt-20 pb-20">
        <PageHeader
          icon={CaveIcon as any}
          title="Center"
          subtitle=""
        />
        
        <div className="w-full relative">
          {/* Scroll arrows - only visible on desktop hover */}
          <div className="hidden md:block">
            {showLeftArrow && (
              <button
                onClick={() => scrollTo('left')}
                className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-card/90 hover:bg-card shadow-lg rounded-full p-2 transition-all opacity-0 group-hover:opacity-100"
                style={{ marginTop: '2rem' }}
              >
                <ChevronLeft className="w-6 h-6 text-muted-foreground" />
              </button>
            )}
            {showRightArrow && (
              <button
                onClick={() => scrollTo('right')}
                className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-card/90 hover:bg-card shadow-lg rounded-full p-2 transition-all opacity-0 group-hover:opacity-100"
                style={{ marginTop: '2rem' }}
              >
                <ChevronRight className="w-6 h-6 text-muted-foreground" />
              </button>
            )}
          </div>

          {/* Horizontal scrolling container with enhanced desktop functionality */}
          <div className="group">
            <div
              ref={scrollContainerRef}
              className="flex overflow-x-auto gap-8 px-4 py-8 snap-x snap-mandatory scrollbar-hide cursor-grab select-none"
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseLeave}
              style={{
                cursor: isDragging ? 'grabbing' : 'grab',
                userSelect: 'none'
              }}
            >
            {centerCards.map((card, index) => {
              const IconComponent = card.icon;
              const isActive = index === activeCardIndex;
              
              const cardContent = (
                <div className={`flex-shrink-0 w-80 h-80 rounded-full bg-card shadow-lg border border-border flex flex-col items-center justify-center p-8 transition-all duration-500 hover:shadow-xl hover:scale-105 cursor-pointer snap-center relative ${
                  isActive ? 'ethereal-glow' : ''
                }`}>
                  <div className={`mb-6 p-4 rounded-full transition-all duration-300 ${
                    isActive ? 'bg-primary shadow-lg' : 'bg-primary'
                  }`}>
                    <IconComponent className={`w-12 h-12 transition-all duration-300 ${
                      isActive ? 'text-primary-foreground drop-shadow-sm' : 'text-primary-foreground/80'
                    }`} />
                  </div>
                  <h3 className={`text-2xl font-semibold text-center mb-3 transition-all duration-300 ${
                    isActive ? 'text-foreground drop-shadow-sm' : 'text-foreground/90'
                  }`}>{card.title}</h3>
                  <p className={`text-center mb-6 text-sm leading-relaxed transition-all duration-300 ${
                    isActive ? 'text-muted-foreground' : 'text-muted-foreground/80'
                  }`}>
                    {card.description}
                  </p>
                  <div className="mt-auto">
                    {card.href ? (
                      <Button variant="outline" size="sm" className={`rounded-full transition-all duration-300 ${
                        isActive ? 'shadow-md border-border' : ''
                      }`}>
                        Open
                      </Button>
                    ) : (
                      <Button variant="outline" size="sm" disabled className={`rounded-full transition-all duration-300 ${
                        isActive ? 'shadow-md border-border' : ''
                      }`}>
                        Coming Soon
                      </Button>
                    )}
                  </div>
                </div>
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
          </div>
          
          {/* Scroll indicator dots - clickable */}
          <div className="flex justify-center mt-6 gap-2">
            {centerCards.map((_, index) => (
              <button
                key={index}
                onClick={() => scrollToCard(index)}
                className={`w-3 h-3 rounded-full transition-all duration-200 hover:scale-110 ${
                  index === activeCardIndex
                    ? 'bg-primary shadow-md'
                      : 'bg-muted hover:bg-muted/80'
                }`}
                aria-label={`Go to ${centerCards[index].title} card`}
              />
            ))}
          </div>

          {/* Star Wars Quote */}
          <div className="mt-12 text-center">
            <p className="text-lg italic text-muted-foreground max-w-2xl mx-auto">
              "Luke Skywalker: What's in the cave?"
              <br />
              "Yoda: Only what you bring with you."
              <br />
              <span className="text-sm">- <em>The Empire Strikes Back</em></span>
            </p>
          </div>

        </div>
      </div>
    </AppLayout>
  );
}