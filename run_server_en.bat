@echo off
REM Student Analytics System Auto-Restart Script
REM This script continuously runs the application and automatically restarts it when it exits

echo ===================================
echo Student Analytics System Auto-Start
===================================
echo Starting application...
echo Press Ctrl+C to stop this script

echo. > server_status.log

:START_LOOP
  echo [%date% %time%] Starting application... >> server_status.log
  echo [%date% %time%] Starting application...
  
  REM Run the application
  python app.py
  
  REM Check exit code
  if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] Application exited normally, preparing to restart... >> server_status.log
    echo [%date% %time%] Application exited normally, preparing to restart...
  ) else (
    echo [%date% %time%] Application crashed with exit code: %ERRORLEVEL%, preparing to restart... >> server_status.log
    echo [%date% %time%] Application crashed with exit code: %ERRORLEVEL%, preparing to restart...
  )
  
  REM Wait 2 seconds before restarting
  echo [%date% %time%] Restarting in 2 seconds... >> server_status.log
  echo Restarting in 2 seconds...
  ping -n 3 127.0.0.1 > nul
  
  echo. >> server_status.log
goto START_LOOP