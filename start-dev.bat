@echo off
echo Starting Eventually Yours Shopping App Development Environment...
echo.

echo Starting Backend...
start "Backend" cmd /k "cd backend && python main.py"

echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak > nul

echo Starting Frontend...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Development servers started!
echo Backend: https://eventually-yours-shopping-app.onrender.com
echo Frontend: http://localhost:5173
echo.
pause 