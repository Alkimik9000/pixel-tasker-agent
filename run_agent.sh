#!/bin/bash

# Source environment variables
source .env

# Launch scrcpy in background for mirroring
echo "Starting scrcpy for device: $DEVICE_SERIAL"
scrcpy --serial=$DEVICE_SERIAL &

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Start the agent
echo "Starting Pixel Tasker Agent..."
python vision_tasker_agent/agent.py 