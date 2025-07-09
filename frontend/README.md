# Arete MVP Frontend

This is the frontend application for Arete MVP, a coaching platform that connects coaches and clients through AI-powered insights and document analysis.

## Technology Stack

- **Framework**: Next.js 15 with App Router
- **Authentication**: Clerk
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI primitives
- **Forms**: React Hook Form with Zod validation
- **Language**: TypeScript

## Key Features

- **Dashboard**: Centralized view for coaches and clients
- **Document Management**: Upload and analyze coaching documents
- **Session Insights**: AI-powered analysis of coaching sessions
- **Goal Tracking**: Set and monitor coaching goals
- **Relationship Management**: Connect coaches with clients
- **Real-time Notifications**: Stay updated on coaching activities

## Development Setup

For complete setup instructions, please refer to the main [DEVELOPMENT.md](../DEVELOPMENT.md) file in the project root.

### Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000).

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── dashboard/         # Main dashboard and features
│   ├── profile/           # User profile management
│   ├── waitlist/          # Beta access waitlist
│   └── layout.tsx         # Root layout with Clerk provider
├── components/            # Reusable React components
│   ├── ui/               # Base UI components (buttons, forms, etc.)
│   ├── dashboard/        # Dashboard-specific components
│   ├── insights/         # Session insights components
│   └── navigation/       # Navigation components
├── services/             # API client services
├── hooks/                # Custom React hooks
├── lib/                  # Utility functions and configurations
└── utils/                # Helper functions
```

## Environment Variables

Create a `.env.local` file in the frontend directory with:

```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_API_URL=http://0.0.0.0:8000
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Authentication

The application uses Clerk for authentication with support for:
- Email/password authentication
- Social login providers
- Organization management for coaching relationships
- Role-based access control (coaches vs clients)

## API Integration

The frontend communicates with the FastAPI backend through service modules located in `src/services/`. These services handle:
- User management
- Document operations
- Session insights
- Goal tracking
- Notifications

For backend setup and API documentation, see the main [DEVELOPMENT.md](../DEVELOPMENT.md) file.
