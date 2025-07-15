import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ClerkProvider } from '@clerk/nextjs'
import { AuthProvider } from '@/context/AuthContext'
import { EntryModalProvider } from '@/context/EntryModalContext'
import { NavigationProvider } from '@/context/NavigationContext'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Arete - Personal Development Platform',
  description: 'The coaching app of my dreams',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider
      publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
      signInFallbackRedirectUrl="/member/journey"
      signUpFallbackRedirectUrl="/profile/create/client"
    >
      <html lang="en">
        <body className={inter.className}>
          <AuthProvider>
            <EntryModalProvider>
              <NavigationProvider>
                {children}
              </NavigationProvider>
            </EntryModalProvider>
          </AuthProvider>
        </body>
      </html>
    </ClerkProvider>
  )
}