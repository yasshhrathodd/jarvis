@echo off
REM Quick start script for Windows
cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo Starting JARVIS at http://localhost:8000
uvicorn backend.main:app --reload --port 8000
