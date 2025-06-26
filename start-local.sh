#!/bin/bash

echo "Starting Eventually Yours Shopping App (Local Development)"
echo

echo "Starting Backend Server..."
cd backend
gnome-terminal --title="Backend Server" -- bash -c "python main.py; exec bash" &
cd ..

echo
echo "Starting Frontend Development Server..."
cd frontend
gnome-terminal --title="Frontend Server" -- bash -c "npm run dev; exec bash" &
cd ..

echo
echo "========================================"
echo "Local Development Setup Complete!"
echo "========================================"
echo
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:5173"
echo
echo "Backend Health Check: http://localhost:5000/api/health"
echo
echo "Both servers are running in separate terminals."
echo "Press Ctrl+C to stop this script."
echo

# Wait for user to stop
wait 