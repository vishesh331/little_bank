#!/bin/bash

# Start CinemaStream Movie Distribution Service

echo ""
echo "===================================================="
echo " CinemaStream - Movie Distribution Service"
echo "===================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Flask not found. Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
fi

echo "Starting CinemaStream..."
echo ""
echo "✓ Server running at http://localhost:5000"
echo "✓ Opening browser..."
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Open browser if available
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5000
elif command -v open &> /dev/null; then
    open http://localhost:5000
fi

# Start the Flask application
python3 app.py
