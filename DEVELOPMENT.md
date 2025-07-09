# Arete MVP Development Guide

## Overview

Arete MVP is a coaching platform that connects coaches and clients through AI-powered insights and document analysis. The platform consists of a FastAPI backend with MongoDB Atlas database and a Next.js frontend with Clerk authentication.

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- MongoDB Atlas account and cluster
- Git

### One-Command Startup
```bash
./start-dev.sh
```

This script will:
- ✅ Check prerequisites (MongoDB Atlas connectivity, ports)
- ✅ Install/update all dependencies
- ✅ Start backend server (port 8000)
- ✅ Start frontend server (port 3000)
- ✅ Verify both services are healthy
- ✅ Provide clear status updates

## Manual Setup

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Environment Configuration

### Backend (.env)
Create a `.env` file in the `backend` directory:
```
# MongoDB Atlas
DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=arete_mvp_production

# Clerk Authentication
CLERK_SECRET_KEY=sk_test_...
CLERK_WEBHOOK_SECRET=whsec_...

# AI Services
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...

# Email Service
SENDGRID_API_KEY=SG...

# API Configuration
API_V1_STR=/api/v1

# Beta Access Control
COACH_WHITELIST_EMAILS=coach1@example.com,coach2@example.com
```

### Frontend (.env.local)
Create a `.env.local` file in the `frontend` directory:
```
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# API Configuration
NEXT_PUBLIC_API_URL=http://0.0.0.0:8000
```

## Service URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://0.0.0.0:8000
- **API Documentation**: http://0.0.0.0:8000/docs
- **Backend Health**: http://0.0.0.0:8000/api/v1/health

## Troubleshooting Common Issues

### "Failed to fetch" Errors

**Root Cause**: Backend server not running or unreachable

**Solutions**:
1. **Check if backend is running**:
   ```bash
   curl http://0.0.0.0:8000/api/v1/health
   ```
   Should return: `{"status":"ok","message":"Arete MVP API is running"}`

2. **Check for missing dependencies**:
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements-dev.txt
   ```

3. **Verify MongoDB Atlas connectivity**:
   - Check your Atlas cluster is running
   - Verify IP whitelist includes your current IP
   - Confirm database credentials are correct

4. **Check port conflicts**:
   ```bash
   lsof -i :8000  # Backend port
   lsof -i :3000  # Frontend port
   ```

### MongoDB Atlas Connection Issues

**Symptoms**: `pymongo.errors.ServerSelectionTimeoutError`

**Solutions**:
1. **Verify connection string format**:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/database_name
   ```

2. **Check Atlas cluster status**:
   - Ensure cluster is not paused
   - Verify network access settings
   - Confirm database user permissions

3. **Test connection manually**:
   ```bash
   cd backend
   source venv/bin/activate
   python3 -c "from app.db.mongodb import get_database; print('Connected!' if get_database() else 'Failed')"
   ```

### Connection Refused Errors

**Symptoms**: `curl: (7) Failed to connect`

**Solutions**:
1. Ensure backend server started successfully (check terminal output)
2. Verify no firewall blocking ports 3000/8000
3. Check if another process is using the ports
4. Confirm uvicorn is binding to 0.0.0.0, not 127.0.0.1

### Import/Module Errors

**Symptoms**: `ModuleNotFoundError` in backend

**Solutions**:
1. Activate virtual environment: `source backend/venv/bin/activate`
2. Install missing dependencies: `pip install -r requirements-dev.txt`
3. Check Python path and virtual environment

## Development Workflow

### Making Changes

1. **Backend Changes**:
   - FastAPI auto-reloads on file changes
   - Check terminal for any import/syntax errors
   - Test endpoints: http://0.0.0.0:8000/docs

2. **Frontend Changes**:
   - Next.js auto-reloads on file changes
   - Check browser console for errors
   - Check terminal for compilation errors

### Adding New Dependencies

1. **Backend**:
   ```bash
   cd backend
   source venv/bin/activate
   pip install new-package
   pip freeze > requirements-dev.txt
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install new-package
   ```

### Health Checks

The frontend includes automatic health checking:
- Open browser console to see health check results
- Manual check: Import and use `HealthChecker.runDiagnostics()`

## External Services Setup

### MongoDB Atlas
1. Create a MongoDB Atlas account
2. Create a new cluster
3. Create a database user with read/write permissions
4. Add your IP address to the network access list
5. Get the connection string and update your `.env` file

### Clerk Authentication
1. Create a Clerk account and application
2. Configure authentication providers as needed
3. Set up webhooks for user management
4. Copy API keys to environment files

### AI Services
- **OpenAI**: Required for document analysis and insights
- **Anthropic**: Fallback AI provider
- Both require API keys in environment configuration

### SendGrid (Email)
- Required for sending notifications and invitations
- Configure API key and sender verification

## Error Prevention Checklist

Before starting development:
- [ ] MongoDB Atlas cluster is running and accessible
- [ ] Ports 3000 and 8000 are available
- [ ] Virtual environment activated (backend)
- [ ] Dependencies installed (both frontend/backend)
- [ ] Environment variables configured for all services
- [ ] External service API keys are valid

## Getting Help

1. **Check service health**: Run `./start-dev.sh` for automated diagnostics
2. **Check logs**: Look at terminal output for both services
3. **Verify connectivity**: Use curl to test backend endpoints
4. **Browser console**: Check for frontend errors and health check results
5. **Database connectivity**: Test MongoDB Atlas connection separately

## Common Commands

```bash
# Full restart
pkill -f "uvicorn\|next-server"
./start-dev.sh

# Backend only
cd backend && source venv/bin/activate && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend only  
cd frontend && npm run dev

# Health check
curl http://0.0.0.0:8000/api/v1/health

# Test MongoDB Atlas connection
cd backend && source venv/bin/activate && python3 -c "from app.db.mongodb import get_database; print(get_database())"
```

## Project Structure

```
arete-mvp/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── core/           # Configuration
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Backend environment variables
├── frontend/               # Next.js application
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   └── services/      # API client services
│   ├── package.json       # Node.js dependencies
│   └── .env.local         # Frontend environment variables
└── DEVELOPMENT.md         # This file