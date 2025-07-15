import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/profile(.*)',
  '/documents(.*)',
  '/goals(.*)',
  '/insights(.*)',
  '/journey(.*)',
  '/center(.*)',
  '/connections(.*)',
  '/settings(.*)',
  '/coach(.*)',
  '/client-invitation(.*)',
  '/dev-sync(.*)',
  '/uat-dashboard(.*)',
  '/test-basecamp(.*)'
]);

const isPublicRoute = createRouteMatcher([
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/',
  '/pricing(.*)',
  '/demo-landing(.*)'
]);

export default clerkMiddleware(async (auth, req) => {
  // Get authentication info
  const { userId, sessionClaims } = await auth();
  
  // Handle role-based redirects for authenticated users
  if (userId && sessionClaims) {
    const userRole = (sessionClaims.publicMetadata as any)?.primary_role;
    
    // Redirect coaches from homepage to their clients page
    if (userRole === 'coach' && req.nextUrl.pathname === '/') {
      return NextResponse.redirect(new URL('/coach/clients', req.url));
    }
    
    // Redirect members from homepage to their journey page
    if (userRole === 'member' && req.nextUrl.pathname === '/') {
      return NextResponse.redirect(new URL('/member/journey', req.url));
    }
  }
  
  // Allow public routes to pass through without authentication
  if (isPublicRoute(req)) {
    return NextResponse.next();
  }
  
  // Protect all other routes that match the protected pattern
  if (isProtectedRoute(req)) {
    if (!userId) {
      return NextResponse.redirect(new URL('/sign-in', req.url));
    }
  }
  
  return NextResponse.next();
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    "/((?!_next|[^?]*\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes
    "/(api|trpc)(.*)",
  ],
};