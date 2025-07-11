'use client'

import { Button } from '@/components/ui/button'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html>
      <body>
        <div className="min-h-screen bg-background flex items-center justify-center px-4">
          <div className="text-center">
            <h1 className="text-4xl font-serif font-bold text-foreground mb-4">Application Error</h1>
            <p className="text-muted-foreground mb-8 max-w-md mx-auto">
              A critical error occurred. Please refresh the page or try again later.
            </p>
            <Button
              onClick={reset}
              className="bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              Try again
            </Button>
          </div>
        </div>
      </body>
    </html>
  )
}