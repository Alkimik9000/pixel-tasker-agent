import uiautomator2 as u2
from adb_shell.adb_device import AdbDeviceUsb
import google.generativeai as genai
from google.generativeai.generative_models import GenerativeModel
from google.adk.tools import FunctionTool
from PIL import Image
import json
import time
import logging
from typing import Dict, Any, Optional, List
from config import GOOGLE_API_KEY, DEVICE_SERIAL, DEVICE_WIDTH, DEVICE_HEIGHT

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
# Note: genai.configure is not needed with GenerativeModel

# Device connection function
def getDevice() -> Any:
    """Get connected Android device instance."""
    if DEVICE_SERIAL is None:
        raise ValueError("DEVICE_SERIAL environment variable is not set")
    try:
        device = u2.connect(DEVICE_SERIAL)
        logger.info("Successfully connected to device: " + DEVICE_SERIAL)
        return device
    except Exception as e:
        logger.error("Failed to connect to device: " + str(e))
        raise

# Core tool functions with proper ADK structure
def captureScreen() -> Dict[str, Any]:
    """Capture a screenshot of the current device screen.
    
    This tool captures the current screen state of the Android device and saves it as an image file.
    Use this tool when you need to analyze the current UI state before performing actions.
    
    Returns:
        dict: Contains 'image_path' of the saved screenshot and 'success' status.
    """
    try:
        logger.info("Capturing screen...")
        d = getDevice()
        img_path = "current_screen.png"
        d.screenshot(img_path)
        logger.info("Screen captured successfully: " + img_path)
        return {"image_path": img_path, "success": True}
    except Exception as e:
        logger.error("Screen capture failed: " + str(e))
        return {"success": False, "error": str(e)}

def analyzeImage(image_path: str, query: Optional[str] = None) -> Dict[str, Any]:
    """Analyze an Android screen image using Gemini vision to identify UI elements.
    
    This tool uses Gemini vision AI to analyze screenshots and identify clickable UI elements,
    providing bounding boxes and coordinates for automation.
    
    Args:
        image_path: Path to the image file to analyze
        query: Optional specific query for the analysis (default: general UI element detection)
    
    Returns:
        dict: Contains 'analysis' with detected elements including normalized and absolute coordinates.
    """
    if query is None:
        query = "Describe this Android screen, detect buttons/text, provide bounding boxes normalized 0-1000 for elements like 'Add Task'. Output as JSON."
    
    try:
        logger.info("Analyzing image: " + image_path + " with query: " + query)
        model = GenerativeModel("gemini-2.0-flash")
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
        
        logger.info("Image analysis complete, found " + str(len(analysis.get("elements", []))) + " elements")
        return {"analysis": analysis, "success": True}
    except json.JSONDecodeError as e:
        logger.error("Failed to parse Gemini response as JSON: " + str(e))
        return {"success": False, "error": "Invalid JSON response", "raw_response": response.text}
    except Exception as e:
        logger.error("Image analysis failed: " + str(e))
        return {"success": False, "error": str(e)}

def performClick(x: int, y: int) -> Dict[str, Any]:
    """Perform a click action at specified coordinates on the Android device.
    
    This tool executes a tap action at the given x,y coordinates using ADB.
    Use this after analyzing the screen to click on specific UI elements.
    
    Args:
        x: X coordinate for the click
        y: Y coordinate for the click
    
    Returns:
        dict: Contains status message and success indicator.
    """
    try:
        logger.info("Performing click at (" + str(x) + ", " + str(y) + ")")
        device = AdbDeviceUsb(serial=DEVICE_SERIAL)
        device.connect()
        device.shell("input tap " + str(x) + " " + str(y))
        time.sleep(1)  # Delay for UI response
        logger.info("Click executed successfully")
        return {"status": "Clicked at (" + str(x) + ", " + str(y) + ")", "success": True}
    except Exception as e:
        logger.error("Click failed: " + str(e))
        return {"status": "Click failed", "success": False, "error": str(e)}

def performTextInput(text: str) -> Dict[str, Any]:
    """Input text into the currently focused field on the Android device.
    
    This tool types the specified text into whatever field currently has focus.
    Make sure to click on a text field first before using this tool.
    
    Args:
        text: The text to input
    
    Returns:
        dict: Contains status message and success indicator.
    """
    try:
        logger.info("Inputting text: " + text)
        device = AdbDeviceUsb(serial=DEVICE_SERIAL)
        device.connect()
        # Escape quotes and special characters for shell
        escaped_text = text.replace('"', '\\"').replace("'", "\\'")
        device.shell('input text "' + escaped_text + '"')
        time.sleep(1)  # Delay for text input
        logger.info("Text input successful")
        return {"status": "Input text: " + text, "success": True}
    except Exception as e:
        logger.error("Text input failed: " + str(e))
        return {"status": "Text input failed", "success": False, "error": str(e)}

def navigateTaskerStep(step_description: str) -> Dict[str, Any]:
    """Navigate through Tasker UI by finding and clicking elements based on description.
    
    This high-level tool combines screen capture, analysis, and clicking to navigate Tasker.
    It launches Tasker if needed and attempts to find and click the described UI element.
    
    Args:
        step_description: Description of what to find and click (e.g., "Add Task button")
    
    Returns:
        dict: Contains execution status and any errors.
    """
    try:
        logger.info("Navigating Tasker step: " + step_description)
        d = getDevice()
        
        # Launch Tasker if not already open
        d.app_start("net.dinglisch.android.taskerm")
        time.sleep(2)
        
        # Capture and analyze screen
        capture_result = captureScreen()
        if not capture_result.get("success"):
            return {"status": "failed", "error": "Screen capture failed"}
        
        analysis_result = analyzeImage(
            capture_result["image_path"], 
            "Find element for: " + step_description + ". Provide box for click."
        )
        
        if not analysis_result.get("success"):
            return {"status": "failed", "error": "Image analysis failed"}
        
        # Click on the first matching element
        elements = analysis_result.get("analysis", {}).get("elements", [])
        if elements:
            elem = elements[0]
            if "click_x" in elem and "click_y" in elem:
                click_result = performClick(elem["click_x"], elem["click_y"])
                if click_result.get("success"):
                    return {"status": "Step executed successfully", "success": True}
                else:
                    return {"status": "Click failed", "success": False, "error": click_result.get("error")}
        
        return {"status": "Element not found", "success": False, "error": "No matching elements found"}
    except Exception as e:
        logger.error("Navigation step failed: " + str(e))
        return {"status": "failed", "success": False, "error": str(e)}

def generatePlan(description: str) -> Dict[str, Any]:
    """Generate a structured plan for creating a Tasker task based on user description.
    
    This tool uses Gemini to create a step-by-step plan for automating a task in Tasker.
    The plan includes specific UI actions needed to create the automation.
    
    Args:
        description: Natural language description of the desired Tasker automation
    
    Returns:
        dict: Contains the generated plan as a list of steps.
    """
    try:
        logger.info("Generating plan for: " + description)
        model = GenerativeModel("gemini-2.0-flash")
        
        prompt = """Create a detailed step-by-step plan to implement this Tasker automation: """ + description + """
        
        Output as a JSON list with the following structure:
        {
            "steps": [
                {
                    "step_number": 1,
                    "action": "Open Tasker app",
                    "ui_element": "Tasker app icon",
                    "description": "Launch the Tasker application"
                },
                ...
            ]
        }
        
        Include specific UI elements to click and any text to input."""
        
        response = model.generate_content(prompt)
        
        try:
            plan = json.loads(response.text)
            logger.info("Plan generated with " + str(len(plan.get("steps", []))) + " steps")
            return {"plan": plan, "success": True}
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw text
            logger.warning("Failed to parse plan as JSON, returning raw text")
            return {"plan": response.text, "raw_response": True, "success": True}
    except Exception as e:
        logger.error("Plan generation failed: " + str(e))
        return {"success": False, "error": str(e)}

def testTask(task_name: str) -> Dict[str, Any]:
    """Test a Tasker task by executing it via intent and checking the result.
    
    This tool runs a Tasker task using Android intents and monitors the result.
    Use this to verify that created tasks work correctly.
    
    Args:
        task_name: Name of the Tasker task to test
    
    Returns:
        dict: Contains test result and pass/fail status.
    """
    try:
        logger.info("Testing Tasker task: " + task_name)
        d = getDevice()
        
        # Run via intent
        cmd = "am broadcast -a net.dinglisch.android.tasker.ACTION_TASK -e task_name '" + task_name + "'"
        result = d.shell(cmd).output
        
        logger.info("Task execution result: " + result)
        
        # Simple pass/fail check
        passed = "error" not in result.lower() and "exception" not in result.lower()
        
        return {
            "result": result, 
            "passed": passed,
            "success": True,
            "task_name": task_name
        }
    except Exception as e:
        logger.error("Task testing failed: " + str(e))
        return {"success": False, "passed": False, "error": str(e)}

# Create FunctionTool instances for ADK
captureScreenTool = FunctionTool(captureScreen)
analyzeImageTool = FunctionTool(analyzeImage)
performClickTool = FunctionTool(performClick)
performTextInputTool = FunctionTool(performTextInput)
navigateTaskerStepTool = FunctionTool(navigateTaskerStep)
generatePlanTool = FunctionTool(generatePlan)
testTaskTool = FunctionTool(testTask) 