'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
 
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])
 
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-4xl font-serif font-bold text-foreground mb-4">Something went wrong!</h1>
        <p className="text-muted-foreground mb-8 max-w-md mx-auto">
          An unexpected error occurred. Please try again.
        </p>
        <Button
          onClick={reset}
          className="bg-primary hover:bg-primary/90 text-primary-foreground"
        >
          Try again
        </Button>
      </div>
    </div>
  )
}