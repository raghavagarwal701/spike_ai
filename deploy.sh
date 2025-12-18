#!/bin/bash

# Ensure python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Python3 could not be found"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies using uv if available, else pip
if command -v uv &> /dev/null; then
    echo "Using uv to install dependencies..."
    uv pip install -r requirements.txt
else
    echo "Using pip to install dependencies..."
    pip install -r requirements.txt
fi

# Check if credentials.json exists
if [ ! -f "credentials.json" ]; then
    echo "WARNING: credentials.json not found!"
fi

# Start the server in background
echo "Starting server on port 8080..."
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8080 > server.log 2>&1 &

# Wait for server to be ready (max 60 seconds)
echo "Waiting for server to start..."
for i in {1..60}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo "Server is ready!"
        exit 0
    fi
    sleep 1
done

echo "ERROR: Server failed to start within 60 seconds"
cat server.log
exit 1
