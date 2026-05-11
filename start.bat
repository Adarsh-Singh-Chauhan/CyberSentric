@echo off
echo ===================================================
echo     Starting CyberSentric
echo ===================================================

echo Building Frontend App...
cd frontend
call npm install
call npm run build
cd ..

echo Starting CyberSentric Server (Frontend + Backend on single port)...
start "CyberSentric Server" cmd /k "cd backend && call venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

echo.
echo Server is starting...
echo Once started, access the app at: http://localhost:8000
echo.
pause
