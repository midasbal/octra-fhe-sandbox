#!/bin/bash
echo "Starting Octra FHE Terminal..."
if [ ! -d "venv" ]; then
    echo "Virtual environment (venv) not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
python3 main.py
