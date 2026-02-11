# TrustLink Startup Script with API Key
# Your Google Safe Browsing API key is configured

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting TrustLink with Learning System Enabled" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$env:GOOGLE_SAFE_BROWSING_KEY = "AIzaSyCKU4ITUny98in-_9opmX5ZRDqdNXed8Ig"
$env:VIRUSTOTAL_API_KEY = "df06e53efd2c7d8572a7218c634274ca7b8cbb3120fed0c305fbfb2743938a7a"

Write-Host "Google Safe Browsing: Configured" -ForegroundColor Green
Write-Host "VirusTotal: Configured" -ForegroundColor Green
Write-Host "PhishTank: Configured (free)" -ForegroundColor Green
Write-Host ""
Write-Host "Starting application..." -ForegroundColor Cyan
Write-Host ""

python app.py
