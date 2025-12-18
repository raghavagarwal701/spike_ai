#!/bin/bash

# Default values
DEV_MODE=false
PORT=8080

# Parse arguments
for arg in "$@"; do
    case $arg in
        --dev)
            DEV_MODE=true
            shift
            ;;
        *)
            # unknown option
            shift
            ;;
    esac
done

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

# Install dependencies
if command -v uv &> /dev/null; then
    echo "Using uv to install dependencies..."
    uv pip install -r requirements.txt
else
    echo "Using pip to install dependencies..."
    pip install -r requirements.txt
fi

# Check for existing process on port
PID=$(lsof -ti:$PORT)

if [ ! -z "$PID" ]; then
    if [ "$DEV_MODE" = true ]; then
        echo "Dev mode check: Killing existing process on port $PORT (PID: $PID)..."
        kill -9 $PID
        sleep 2
    else
        echo "ERROR: Server is already running on port $PORT (PID: $PID)."
        echo "Use --dev flag to force restart with hot-reloading."
        exit 1
    fi
fi

# Check if credentials.json exists
if [ ! -f "credentials.json" ]; then
    echo "WARNING: credentials.json not found!"
fi

# Construct command
CMD="python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT"
if [ "$DEV_MODE" = true ]; then
    echo "Starting server in DEV mode (auto-reload enabled)..."
    CMD="$CMD --reload"
else
    echo "Starting server in PROD mode..."
fi

# Start the server in background
echo "Executing: $CMD"
nohup $CMD > server.log 2>&1 &

# Wait for server to be ready (max 60 seconds)
echo "Waiting for server to start..."
for i in {1..60}; do
    if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
        echo "Server is ready!"
        exit 0
    fi
    sleep 1
done

echo "ERROR: Server failed to start within 60 seconds"
cat server.log
exit 1
