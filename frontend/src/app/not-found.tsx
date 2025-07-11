import Link from 'next/link'
import { Button } from '@/components/ui/button'
 
export default function NotFound() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-6xl font-serif font-bold text-foreground mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-muted-foreground mb-4">Page Not Found</h2>
        <p className="text-muted-foreground mb-8 max-w-md mx-auto">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link href="/">
          <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">
            Return Home
          </Button>
        </Link>
      </div>
    </div>
  )
}