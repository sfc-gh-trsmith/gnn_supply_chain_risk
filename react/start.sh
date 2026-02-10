#!/bin/bash
set -e

cd "$(dirname "$0")"
mkdir -p logs

echo "Starting GNN Supply Chain Risk App..."

# Start backend
echo "Starting backend..."
cd backend
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -q -r requirements.txt

SNOWFLAKE_CONNECTION_NAME="${SNOWFLAKE_CONNECTION_NAME:-demo}" uvicorn api.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID >> ../.services.pid
cd ..

# Wait for backend to start
echo "Waiting for backend..."
sleep 3

# Start frontend
echo "Starting frontend..."
cd frontend
npm install --silent
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID >> ../.services.pid
cd ..

echo ""
echo "=========================================="
echo "  GNN Supply Chain Risk App Started"
echo "=========================================="
echo ""
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "  Logs: ./logs/"
echo "  Stop: ./stop.sh"
echo ""
