import Link from 'next/link'
import { Button } from '@/components/ui/button'
 
export default function NotFound() {
  return (
    <div className="min-h-screen bg-moonlight-ivory flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-6xl font-serif font-bold text-midnight-indigo mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-owlet-teal mb-4">Page Not Found</h2>
        <p className="text-muted-foreground mb-8 max-w-md mx-auto">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link href="/">
          <Button className="bg-midnight-indigo hover:bg-midnight-indigo/90 text-white">
            Return Home
          </Button>
        </Link>
      </div>
    </div>
  )
}