#!/bin/bash

# Arete MVP Development Startup Script
# This script starts both frontend and backend services with proper error handling

set -e  # Exit on any error

echo "🚀 Starting Arete MVP Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is ready!${NC}"
            return 0
        fi
        
        echo "   Attempt $attempt/$max_attempts - $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $service_name failed to start within timeout${NC}"
    return 1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if MongoDB is running
if ! pgrep mongod >/dev/null 2>&1; then
    echo -e "${RED}❌ MongoDB is not running. Please start MongoDB first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ MongoDB is running${NC}"

# Check if ports are available
if check_port 3000; then
    echo -e "${YELLOW}⚠️  Port 3000 is already in use (frontend)${NC}"
fi

if check_port 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use (backend)${NC}"
fi

# Start backend
echo "🔧 Starting backend server..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
source venv/bin/activate

echo "📦 Installing/updating backend dependencies..."
pip install -r requirements-dev.txt >/dev/null 2>&1

# Start backend in background
echo "🚀 Starting FastAPI server..."
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to be ready
if ! wait_for_service "http://127.0.0.1:8000/api/v1/health" "Backend API"; then
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend server..."
cd ../frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start frontend in background
echo "🚀 Starting Next.js server..."
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to be ready
if ! wait_for_service "http://localhost:3000" "Frontend"; then
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}"
echo "🎉 Development environment is ready!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://127.0.0.1:8000"
echo "   API Docs: http://127.0.0.1:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo -e "${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✅ All services stopped${NC}"
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Wait for user to stop
wait $BACKEND_PID $FRONTEND_PID