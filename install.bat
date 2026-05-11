@echo off
echo ===================================================
echo     CyberSentric Installer
echo ===================================================

echo.
echo [1/2] Setting up Backend (FastAPI)...
cd backend
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
echo Upgrading pip and build tools (This fixes the stuck terminal issue)...
python -m pip install --upgrade pip setuptools wheel
echo Installing Python dependencies...
pip install -r requirements.txt
cd ..

echo.
echo [2/2] Setting up Frontend (React)...
cd frontend
call npm install
cd ..

echo.
echo ===================================================
echo     Installation Complete!
echo     You can now double-click start.bat to run
echo ===================================================
pause
