import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";

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
    <html lang="en">
      <body
        className={`${inter.variable} ${playfairDisplay.variable} font-sans antialiased`}
      >
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
