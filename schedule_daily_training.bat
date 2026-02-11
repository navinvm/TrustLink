@echo off
REM TrustLink - Daily Automated Training
REM Run this script via Windows Task Scheduler every 24 hours

cd /d "%~dp0"
python scheduled_training.py

REM Log the execution
echo [%date% %time%] Daily training completed >> training_schedule.log
