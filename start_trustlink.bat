@echo off
echo ============================================================
echo    TrustLink: Phishing Detection System
echo ============================================================
echo.
echo Starting the application...
echo.

REM Check if Flask is installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo [!] Flask not found. Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Start the Flask application
echo [*] Launching TrustLink server...
echo [*] Once started, open your browser to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
