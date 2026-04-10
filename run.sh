#!/bin/bash
# Start the Mognadsdialog server
cd "$(dirname "$0")"
source venv/bin/activate
echo "Starting Mognadsdialog on http://localhost:8501"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8501
