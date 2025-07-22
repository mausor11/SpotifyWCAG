@echo off
REM Spotify WCAG Application Startup Script
REM ======================================
REM 
REM This script starts all the necessary servers and frontend for the Spotify WCAG application
REM 
REM Usage:
REM     start_app.bat

echo 🎵 Spotify WCAG Application Startup Script
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nie jest zainstalowany
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js nie jest zainstalowany
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm nie jest zainstalowany
    pause
    exit /b 1
)

REM Run the Python startup script
echo 🚀 Uruchamiam aplikację...
python start_servers.py

pause 