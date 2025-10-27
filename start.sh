#!/bin/bash

# Start script for Number Plate Detection System (Linux/Mac)

echo "Starting Number Plate Detection System..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Start backend in background
echo "Starting backend server..."
python backend/app.py &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo "Frontend started with PID: $FRONTEND_PID"

echo ""
echo "===== Application Started ====="
echo "Frontend: http://localhost:5173"
echo "Backend: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Cleanup on exit
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM

# Wait for both processes
wait
