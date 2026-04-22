#!/bin/bash
# Quick start script for Mac/Linux
# Activates the venv (if it exists) and starts JARVIS.

cd "$(dirname "$0")"

if [ -d "venv" ]; then
  source venv/bin/activate
fi

echo "Starting JARVIS at http://localhost:8000"
uvicorn backend.main:app --reload --port 8000
