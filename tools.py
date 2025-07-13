import uiautomator2 as u2
from adb_shell.adb_device import AdbDeviceUsb
import google.generativeai as genai
from google.generativeai.generative_models import GenerativeModel
from PIL import Image
import json
import time
from typing import Dict, Any, Optional
from config import GOOGLE_API_KEY, DEVICE_SERIAL, DEVICE_WIDTH, DEVICE_HEIGHT

# Load env
genai.configure(api_key=GOOGLE_API_KEY)

# Connect to device
def getDevice() -> Any:
    if DEVICE_SERIAL is None:
        raise ValueError("DEVICE_SERIAL environment variable is not set")
    return u2.connect(DEVICE_SERIAL)

# Capture Screen
def captureScreen() -> Dict[str, Any]:
    d = getDevice()
    img_path = "current_screen.png"
    d.screenshot(img_path)
    return {"image_path": img_path, "success": True}

# Analyze Image with Gemini
def analyzeImage(image_path: str, query: Optional[str] = None) -> Dict[str, Any]:
    if query is None:
        query = "Describe this Android screen, detect buttons/text, provide bounding boxes normalized 0-1000 for elements like 'Add Task'. Output as JSON."
    
    model = GenerativeModel("gemini-2.5-flash")
    img = Image.open(image_path)
    response = model.generate_content(
        [query, img],
        generation_config={"response_mime_type": "application/json"}
    )
    analysis = json.loads(response.text)
    # Convert normalized boxes to absolute coords
    for item in analysis.get("elements", []):
        if "box_2d" in item:
            box = item["box_2d"]  # [ymin, xmin, ymax, xmax] normalized 0-1000
            item["abs_box"] = [
                int(box[1] / 1000 * DEVICE_WIDTH),  # xmin
                int(box[0] / 1000 * DEVICE_HEIGHT), # ymin
                int(box[3] / 1000 * DEVICE_WIDTH),  # xmax
                int(box[2] / 1000 * DEVICE_HEIGHT)  # ymax
            ]
            # Center for click
            item["click_x"] = (item["abs_box"][0] + item["abs_box"][2]) // 2
            item["click_y"] = (item["abs_box"][1] + item["abs_box"][3]) // 2
    return {"analysis": analysis}

# Perform Click (by coords)
def performClick(x: int, y: int) -> Dict[str, str]:
    device = AdbDeviceUsb(serial=DEVICE_SERIAL)
    device.connect()
    device.shell("input tap " + str(x) + " " + str(y))
    time.sleep(1)  # Delay for UI response
    return {"status": "Clicked at (" + str(x) + ", " + str(y) + ")"}

# Navigate Tasker Step (high-level, uses analysis/click)
def navigateTaskerStep(step_description: str) -> Dict[str, Any]:
    # Example: "Open Tasker and click Add Task"
    d = getDevice()
    d.app_start("net.dinglisch.android.taskerm")  # Launch Tasker
    time.sleep(2)
    captureScreen()
    analysis = analyzeImage("current_screen.png", "Find element for: " + step_description + ". Provide box for click.")
    if "elements" in analysis["analysis"] and analysis["analysis"]["elements"]:
        elem = analysis["analysis"]["elements"][0]
        performClick(elem["click_x"], elem["click_y"])
        return {"status": "Step executed"}
    return {"error": "Element not found"}

# Generate Plan
def generatePlan(description: str) -> Dict[str, Any]:
    model = GenerativeModel("gemini-2.5-flash")
    response = model.generate_content("Plan steps to create Tasker task: " + description + ". Output as JSON list of steps.")
    plan = json.loads(response.text)
    return {"plan": plan}

# Test Task
def testTask(task_name: str) -> Dict[str, Any]:
    d = getDevice()
    # Run via intent
    cmd = "am broadcast -a net.dinglisch.android.tasker.ACTION_TASK -e task_name '" + task_name + "'"
    result = d.shell(cmd).output
    # Verify (example: check log or state)
    return {"result": result, "passed": "success" in result.lower()}

# Perform Text Input
def performTextInput(text: str) -> Dict[str, str]:
    device = AdbDeviceUsb(serial=DEVICE_SERIAL)
    device.connect()
    # Escape quotes and special characters for shell
    escaped_text = text.replace('"', '\\"').replace("'", "\\'")
    device.shell('input text "' + escaped_text + '"')
    time.sleep(1)  # Delay for text input
    return {"status": "Input text: " + text}

# Legacy function names for backward compatibility
capture_screen = captureScreen
analyze_image = analyzeImage
perform_click = performClick
navigate_tasker_step = navigateTaskerStep
generate_plan = generatePlan
test_task = testTask
get_device = getDevice
perform_text_input = performTextInput 