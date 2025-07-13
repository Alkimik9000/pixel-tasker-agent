# Pixel Agent Configuration

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Google API Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_api_key_here

# Device Configuration
# Find your device serial with: adb devices
DEVICE_SERIAL=your_device_serial_here

# Device dimensions (default for Pixel 8 Pro)
DEVICE_WIDTH=1344
DEVICE_HEIGHT=2992

# Tasker package name (usually doesn't need to change)
TASKER_PACKAGE_NAME=net.dinglisch.android.taskerm
```

## Setup Instructions

1. **Copy configuration**: `cp config.py.example config.py`
2. **Get Google API Key**: Visit https://makersuite.google.com/app/apikey
3. **Find Device Serial**: Run `adb devices` to get your device serial
4. **Create .env file**: Copy the template above and fill in your values
5. **Install dependencies**: `./venv/bin/pip install -r requirements.txt`
6. **Run the agent**: `./venv/bin/python vision_tasker_agent/agent.py`

## Requirements

- Python 3.8+
- ADB installed and device connected
- Google API key with Gemini access
