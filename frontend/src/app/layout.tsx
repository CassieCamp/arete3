import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import { ClerkProvider } from "@clerk/nextjs";
import NextTopLoader from 'nextjs-toploader';

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const playfairDisplay = Playfair_Display({
  variable: "--font-playfair-display",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Arete - AI-Enhanced Executive Coaching",
  description: "Transform your leadership with AI-enhanced executive coaching. Accelerate your professional development with personalized insights and growth tracking.",
  keywords: ["executive coaching", "leadership development", "AI coaching", "professional growth", "transformation"],
  authors: [{ name: "Arete Coaching" }],
  openGraph: {
    title: "Arete - AI-Enhanced Executive Coaching",
    description: "Transform your leadership with AI-enhanced executive coaching",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider
      publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
      signInFallbackRedirectUrl="/dashboard"
      signUpFallbackRedirectUrl="/profile/create/client"
    >
      <html lang="en">
        <body
          className={`${inter.variable} ${playfairDisplay.variable} font-sans antialiased`}
        >
          <NextTopLoader
            color="#3b82f6"
            initialPosition={0.08}
            crawlSpeed={200}
            height={3}
            crawl={true}
            showSpinner={true}
            easing="ease"
            speed={200}
            shadow="0 0 10px #3b82f6,0 0 5px #3b82f6"
          />
          <AuthProvider>
            {children}
          </AuthProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
