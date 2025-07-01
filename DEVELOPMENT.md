# Arete MVP Development Guide

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- MongoDB running locally
- Git

### One-Command Startup
```bash
./start-dev.sh
```

This script will:
- ✅ Check prerequisites (MongoDB, ports)
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
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Troubleshooting Common Issues

### "Failed to fetch" Errors

**Root Cause**: Backend server not running or unreachable

**Solutions**:
1. **Check if backend is running**:
   ```bash
   curl http://127.0.0.1:8000/api/v1/health
   ```
   Should return: `{"status":"ok","message":"Arete MVP API is running"}`

2. **Check for missing dependencies**:
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements-dev.txt
   ```

3. **Verify MongoDB is running**:
   ```bash
   ps aux | grep mongod
   ```

4. **Check port conflicts**:
   ```bash
   lsof -i :8000  # Backend port
   lsof -i :3000  # Frontend port
   ```

### Connection Refused Errors

**Symptoms**: `curl: (7) Failed to connect`

**Solutions**:
1. Ensure backend server started successfully (check terminal output)
2. Verify no firewall blocking ports 3000/8000
3. Check if another process is using the ports

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
   - Test endpoints: http://127.0.0.1:8000/docs

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

## Service URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Backend Health**: http://127.0.0.1:8000/api/v1/health

## Environment Variables

### Frontend (.env)
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Backend (.env)
```
DATABASE_URL=mongodb://localhost:27017/
DATABASE_NAME=arete_mvp_test
CLERK_SECRET_KEY=sk_test_...
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
```

## Error Prevention Checklist

Before starting development:
- [ ] MongoDB is running
- [ ] Ports 3000 and 8000 are available
- [ ] Virtual environment activated (backend)
- [ ] Dependencies installed (both frontend/backend)
- [ ] Environment variables configured

## Getting Help

1. **Check service health**: Run `./start-dev.sh` for automated diagnostics
2. **Check logs**: Look at terminal output for both services
3. **Verify connectivity**: Use curl to test backend endpoints
4. **Browser console**: Check for frontend errors and health check results

## Common Commands

```bash
# Full restart
pkill -f "uvicorn\|next-server"
./start-dev.sh

# Backend only
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Frontend only  
cd frontend && npm run dev

# Health check
curl http://127.0.0.1:8000/api/v1/health

# View logs
tail -f backend/logs/app.log  # If logging to file