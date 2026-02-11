@echo off
REM TrustLink Startup Script with API Key
REM Your Google Safe Browsing API key is configured

echo.
echo ============================================================
echo   Starting TrustLink with Learning System Enabled
echo ============================================================
echo.

set GOOGLE_SAFE_BROWSING_KEY=AIzaSyCKU4ITUny98in-_9opmX5ZRDqdNXed8Ig
set VIRUSTOTAL_API_KEY=df06e53efd2c7d8572a7218c634274ca7b8cbb3120fed0c305fbfb2743938a7a

echo Google Safe Browsing: Configured
echo VirusTotal: Configured
echo PhishTank: Configured (free)
echo.
echo Starting application...
echo.

python app.py
