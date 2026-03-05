@echo off
REM ThreatSense Startup Script for Windows

echo =====================================
echo ThreatSense AI Detection System
echo =====================================
echo.

REM Create necessary directories
if not exist logs mkdir logs
if not exist data mkdir data
if not exist models mkdir models
if not exist storage mkdir storage

REM Load environment variables
if exist .env (
    echo Loading environment configuration from .env
    REM Note: Windows batch doesn't parse .env files easily
    REM Consider using PowerShell or manually setting variables
) else (
    echo .env file not found. Creating from .env.example
    copy .env.example .env
    echo Please edit .env with your configuration and run again.
    pause
    exit /b 1
)

REM Check Python version
echo.
echo Checking Python version...
python --version

REM Create virtual environment if needed
if not exist venv (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Initialize database
echo.
echo Initializing database...
python -c "from database import init_db; init_db()"

REM Start the application
echo.
echo Starting ThreatSense...
echo API will be available at: http://localhost:8000
echo Dashboard: http://localhost:8000/
echo.
echo Press Ctrl+C to stop
echo.

uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
