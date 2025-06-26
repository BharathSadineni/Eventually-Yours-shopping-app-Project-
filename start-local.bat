@echo off
echo Starting Eventually Yours Shopping App (Local Development)
echo.

echo Starting Backend Server...
cd backend
start "Backend Server" cmd /k "python main.py"
cd ..

echo.
echo Starting Frontend Development Server...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo Local Development Setup Complete!
echo ========================================
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Backend Health Check: http://localhost:5000/api/health
echo.
echo Press any key to exit...
pause > nul 