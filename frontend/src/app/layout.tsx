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
  description: 'Transform your potential into achievement with personalized coaching and insights.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
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