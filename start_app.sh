#!/bin/bash

# Spotify WCAG Application Startup Script
# ======================================
# 
# This script starts all the necessary servers and frontend for the Spotify WCAG application
# 
# Usage:
#     ./start_app.sh
#     or
#     bash start_app.sh

echo "🎵 Spotify WCAG Application Startup Script"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nie jest zainstalowany"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js nie jest zainstalowany"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm nie jest zainstalowany"
    exit 1
fi

# Make the Python script executable
chmod +x start_servers.py

# Run the Python startup script
echo "🚀 Uruchamiam aplikację..."
python3 start_servers.py 