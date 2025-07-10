# Clerk Configuration Guide

## Issue Resolution Summary

### Problem
Clerk sign-in and waitlist functionality was broken due to environment configuration mismatches.

### Root Cause
The live Clerk keys (`pk_live_*` and `sk_live_*`) were not configured to allow localhost:3000 as an authorized domain, causing 400 errors and preventing Clerk components from rendering.

### Solution Applied
Switched to test keys for local development while preserving live keys for production deployment.

## Environment Configuration

### Local Development (.env.local)
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_Zmlyc3Qtd2Vhc2VsLTEwLmNsZXJrLmFjY291bnRzLmRldiQ
CLERK_SECRET_KEY=sk_test_lmSNNAI1wCJjoON8EYab6kv0SGg9FdGSp0WLtDlMvI
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Production Deployment
For production, use the live keys:
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_Y2xlcmsuYXJldGUuY29hY2gk
CLERK_SECRET_KEY=sk_live_H25Gpeg59dE1uQI4LJZ6f3Imn6fqcL7EEIzqlOjxog
CLERK_WEBHOOK_SECRET=whsec_Dvsc0pERAu4/aUKFCRVNKdptNWuHI833
```

## Key Changes Made

### Frontend (`frontend/src/app/layout.tsx`)
- Added explicit `publishableKey` prop to ClerkProvider
- Updated to use modern redirect props (`signInFallbackRedirectUrl`, `signUpFallbackRedirectUrl`)

### Backend (`backend/.env`)
- Updated Clerk secret key to match frontend environment
- Set appropriate webhook secret for development

### Build System
- Cleared Next.js cache (`.next` directory) to resolve JavaScript 404 errors
- Ensured proper compilation of Clerk components

## Verification Steps

1. ✅ Client waitlist page loads correctly at `/waitlist/client`
2. ✅ Coach waitlist page loads correctly at `/waitlist/coach`
3. ✅ Clerk Waitlist components render properly
4. ✅ Email submission works and redirects to success page
5. ✅ No console errors or 400/404 HTTP errors
6. ✅ Webhook configuration ready for user creation events

## Production Deployment Notes

### Required Clerk Dashboard Configuration
Before deploying to production with live keys:

1. **Domain Configuration**: Add production domain to allowed origins in Clerk dashboard
2. **Webhook Endpoints**: Configure webhook URL: `https://your-domain.com/api/v1/webhooks/clerk`
3. **Redirect URLs**: Update sign-in/sign-up redirect URLs for production domain

### Security Considerations
- ✅ Environment files are properly excluded from version control
- ✅ Live keys are only used in production environment
- ✅ Test keys are used for local development
- ✅ Webhook signature verification is implemented

## Testing Checklist

- [x] Waitlist signup flow (client)
- [x] Waitlist signup flow (coach)
- [x] Success page redirection
- [x] No JavaScript errors
- [x] Proper Clerk component rendering
- [x] Environment variable loading
- [x] Backend webhook endpoint ready

## Troubleshooting

### Common Issues
1. **400 Errors**: Check that Clerk keys match the environment (test vs live)
2. **Component Not Rendering**: Verify publishableKey is properly set in ClerkProvider
3. **JavaScript 404s**: Clear Next.js cache with `rm -rf .next`
4. **Webhook Failures**: Ensure webhook secret matches Clerk dashboard configuration