# Pixel Agent Configuration

A multi-agent system for automating Tasker tasks on Pixel 8 Pro using Google's Agent Development Kit (ADK).

## Recent Updates (ADK Agent Fix)

**Problem Fixed**: The agent was generating descriptive text instead of executing tools.

**Solution Implemented**:
- All tools now properly wrapped with `FunctionTool` for ADK compatibility
- Agent instructions rewritten to be action-oriented with "IMMEDIATELY" directives
- Real workflow execution functions that chain multiple tool calls
- Comprehensive logging and error handling throughout

See `ADK_AGENT_FIX_SUMMARY.md` for detailed technical documentation of the fixes.

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
5. **Install dependencies**: `pip install -r requirements.txt`
6. **Test the implementation**: `python test_updated_agent.py`

## Running the Agent

### Option 1: ADK Web UI (Recommended)
```bash
adk web
```
Then open http://localhost:8000 in your browser.

### Option 2: Command Line
```bash
adk run pixel_agent
```

### Option 3: Direct Python
```bash
python vision_tasker_agent/agent.py
```

## Testing the Fixed Agent

1. **Connect your Pixel device**:
   ```bash
   adb devices  # Should show your device
   ```

2. **Run the test script**:
   ```bash
   python test_updated_agent.py
   ```

3. **Test with a real query**:
   - In ADK web UI, enter: "create a task that sets an alarm for 7:30 AM"
   - Check the Graph tab to see tool execution flow
   - Monitor your device with scrcpy to see UI interactions

## Expected Behavior

When you query: "create a task that when executed creates an alarm for tomorrow morning at 7:30"

The agent will:
1. Immediately call `runCreationWorkflow` 
2. Execute `generatePlan` to create step-by-step instructions
3. Execute `captureScreen` to get current UI state
4. Execute `analyzeImage` to find clickable elements
5. Execute multiple `navigateTaskerStep` calls to create the task
6. Return actual execution results

## Requirements

- Python 3.8+
- ADB installed and device connected
- Google API key with Gemini access
- Pixel 8 Pro with Tasker installed
- google-adk package (`pip install google-adk`)

## Troubleshooting

If the agent still provides descriptive text:
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check that your device is connected: `adb devices`
3. Verify tools are FunctionTool instances: `python test_updated_agent.py`
4. Check logs for any errors during tool execution

## Architecture

- **Root Agent**: Orchestrates workflows with action-oriented instructions
- **Planner Agent**: Generates step-by-step plans
- **Vision Agent**: Captures and analyzes screen state
- **Navigator Agent**: Executes UI interactions
- **Tester Agent**: Validates created tasks

All agents now use FunctionTool-wrapped tools and have "IMMEDIATELY execute" instructions to ensure action over description.
