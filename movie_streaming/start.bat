@echo off
REM Start CinemaStream Movie Distribution Service

echo.
echo ====================================================
echo  CinemaStream - Movie Distribution Service
echo ====================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Flask not found. Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Starting CinemaStream...
echo.
echo ✓ Server running at http://localhost:5000
echo ✓ Opening browser...
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask application
python app.py

pause
