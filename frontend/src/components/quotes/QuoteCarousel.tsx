"use client";

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Heart, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

interface Quote {
  id: string;
  quote_text: string;
  author: string;
  source?: string;
  category: string;
  tags: string[];
  like_count: number;
  is_liked: boolean;
}

interface QuoteCarouselProps {
  className?: string;
}

export function QuoteCarousel({ className = "" }: QuoteCarouselProps) {
  const { getAuthToken } = useAuth();
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDailyQuotes();
  }, []);

  const loadDailyQuotes = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const token = await getAuthToken();
      if (!token) {
        throw new Error('No authentication token available');
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/quotes?count=5`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load quotes');
      }

      const data = await response.json();
      setQuotes(data.quotes || []);
    } catch (error) {
      console.error('Failed to load quotes:', error);
      setError('Failed to load quotes. Please try again.');
      // Set some fallback quotes for development
      setQuotes([
        {
          id: 'fallback-1',
          quote_text: 'The only way to do great work is to love what you do.',
          author: 'Steve Jobs',
          category: 'motivation',
          tags: ['passion', 'work'],
          like_count: 0,
          is_liked: false
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLikeQuote = async (quoteId: string) => {
    try {
      const token = await getAuthToken();
      if (!token) return;

      const currentQuote = quotes[currentIndex];
      const newLikedState = !currentQuote.is_liked;

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/quotes/${quoteId}/like`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ liked: newLikedState })
      });

      if (!response.ok) {
        throw new Error('Failed to like quote');
      }

      // Update local state optimistically
      setQuotes(prev => prev.map(quote => 
        quote.id === quoteId 
          ? { 
              ...quote, 
              is_liked: newLikedState,
              like_count: newLikedState ? quote.like_count + 1 : quote.like_count - 1
            }
          : quote
      ));
    } catch (error) {
      console.error('Failed to like quote:', error);
    }
  };

  const nextQuote = () => {
    setCurrentIndex((prev) => (prev + 1) % quotes.length);
  };

  const prevQuote = () => {
    setCurrentIndex((prev) => (prev - 1 + quotes.length) % quotes.length);
  };

  const goToQuote = (index: number) => {
    setCurrentIndex(index);
  };

  if (isLoading) {
    return (
      <Card className={`w-full max-w-md mx-auto ${className}`}>
        <CardContent className="p-8">
          <div className="flex items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || quotes.length === 0) {
    return (
      <Card className={`w-full max-w-md mx-auto ${className}`}>
        <CardContent className="p-8 text-center">
          <p className="text-muted-foreground">
            {error || 'No quotes available at the moment.'}
          </p>
          <Button 
            variant="outline" 
            onClick={loadDailyQuotes}
            className="mt-4"
          >
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  const currentQuote = quotes[currentIndex];

  return (
    <Card className={`w-full max-w-md mx-auto ${className}`}>
      <CardContent className="p-8">
        {/* Quote Content */}
        <div className="text-center mb-6">
          <blockquote className="text-lg font-medium text-foreground mb-4 leading-relaxed">
            "{currentQuote.quote_text}"
          </blockquote>
          <cite className="text-sm text-muted-foreground">
            — {currentQuote.author}
            {currentQuote.source && (
              <span className="block text-xs text-muted-foreground mt-1">
                {currentQuote.source}
              </span>
            )}
          </cite>
        </div>
        
        {/* Heart Button */}
        <div className="flex justify-center mb-6">
          <Button
            variant="ghost"
            size="lg"
            onClick={() => handleLikeQuote(currentQuote.id)}
            className={`p-3 rounded-full transition-all duration-200 hover:scale-110 ${
              currentQuote.is_liked
                ? 'text-red-500 hover:text-red-600'
                : 'text-muted-foreground hover:text-red-500'
            }`}
          >
            <Heart 
              className={`w-6 h-6 ${currentQuote.is_liked ? 'fill-current' : ''}`} 
            />
          </Button>
        </div>
        
        {/* Navigation */}
        {quotes.length > 1 && (
          <div className="flex justify-between items-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={prevQuote}
              className="p-2 rounded-full"
            >
              <ChevronLeft className="w-5 h-5" />
            </Button>
            
            {/* Dots Indicator */}
            <div className="flex space-x-2">
              {quotes.map((_, index) => (
                <button
                  key={index}
                  onClick={() => goToQuote(index)}
                  className={`w-2 h-2 rounded-full transition-colors ${
                    index === currentIndex 
                      ? 'bg-primary' 
                      : 'bg-muted-foreground/30 hover:bg-muted-foreground/50'
                  }`}
                />
              ))}
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={nextQuote}
              className="p-2 rounded-full"
            >
              <ChevronRight className="w-5 h-5" />
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Skeleton component for loading state
export function QuoteCarouselSkeleton({ className = "" }: { className?: string }) {
  return (
    <Card className={`w-full max-w-md mx-auto ${className}`}>
      <CardContent className="p-8">
        <div className="text-center mb-6">
          <div className="h-4 bg-muted rounded w-3/4 mx-auto mb-2"></div>
          <div className="h-4 bg-muted rounded w-1/2 mx-auto mb-4"></div>
          <div className="h-3 bg-muted rounded w-1/3 mx-auto"></div>
        </div>
        
        <div className="flex justify-center mb-6">
          <div className="w-12 h-12 bg-muted rounded-full"></div>
        </div>
        
        <div className="flex justify-between items-center">
          <div className="w-8 h-8 bg-muted rounded-full"></div>
          <div className="flex space-x-2">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="w-2 h-2 bg-muted rounded-full"></div>
            ))}
          </div>
          <div className="w-8 h-8 bg-muted rounded-full"></div>
        </div>
      </CardContent>
    </Card>
  );
}