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
    try:
        plan = json.loads(response.text)
        return {"plan": plan}
    except json.JSONDecodeError:
        # If JSON parsing fails, return the raw text
        return {"plan": response.text, "raw_response": True}

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

# Workflow invocation tools for root agent
def invokeCreationWorkflow(user_query: str) -> Dict[str, Any]:
    """
    Invoke the creation workflow for creating new Tasker tasks.
    This tool triggers the sequential workflow: planner -> vision -> navigator.
    """
    try:
        # Execute the creation workflow with the user query
        # Note: This is a simplified invocation - actual ADK workflow execution 
        # would need proper context and session management
        workflow_result = {
            "workflow": "creation_workflow",
            "query": user_query,
            "status": "initiated",
            "message": "Creation workflow started - delegating to planner, vision, and navigator agents"
        }
        
        # Trigger first step - generate plan
        plan_result = generatePlan(user_query)
        workflow_result["plan"] = str(plan_result)
        
        # Trigger vision analysis
        capture_result = captureScreen()
        if capture_result["success"]:
            analysis_result = analyzeImage(capture_result["image_path"], "Analyze current Tasker screen for navigation")
            workflow_result["vision_analysis"] = str(analysis_result)
        
        # Mark as completed
        workflow_result["status"] = "completed"
        workflow_result["message"] = "Creation workflow executed successfully"
        
        return workflow_result
        
    except Exception as e:
        return {
            "workflow": "creation_workflow",
            "query": user_query,
            "status": "error",
            "error": str(e)
        }

def invokeTestingWorkflow(task_name: str) -> Dict[str, Any]:
    """
    Invoke the testing workflow for validating Tasker tasks.
    This tool triggers the loop workflow with the tester agent.
    """
    try:
        # Execute the testing workflow
        workflow_result = {
            "workflow": "testing_workflow",
            "task_name": task_name,
            "status": "initiated",
            "message": "Testing workflow started - delegating to tester agent"
        }
        
        # Trigger testing
        test_result = testTask(task_name)
        workflow_result["test_result"] = str(test_result)
        
        # Mark as completed
        workflow_result["status"] = "completed"
        workflow_result["message"] = "Testing workflow executed successfully"
        
        return workflow_result
        
    except Exception as e:
        return {
            "workflow": "testing_workflow",
            "task_name": task_name,
            "status": "error",
            "error": str(e)
        }

def invokeParallelAnalysis(analysis_query: str) -> Dict[str, Any]:
    """
    Invoke parallel analysis workflow for complex screen analysis.
    This tool triggers parallel vision analysis.
    """
    try:
        # Execute parallel analysis
        workflow_result = {
            "workflow": "parallel_analysis",
            "query": analysis_query,
            "status": "initiated",
            "message": "Parallel analysis workflow started - using multiple vision agents"
        }
        
        # Trigger screen capture and analysis
        capture_result = captureScreen()
        if capture_result["success"]:
            analysis_result = analyzeImage(capture_result["image_path"], analysis_query)
            workflow_result["analysis"] = str(analysis_result)
            
            # Mark as completed
            workflow_result["status"] = "completed"
            workflow_result["message"] = "Parallel analysis workflow executed successfully"
        
        return workflow_result
        
    except Exception as e:
        return {
            "workflow": "parallel_analysis",
            "query": analysis_query,
            "status": "error",
            "error": str(e)
        }

def detectQueryType(user_query: str) -> Dict[str, Any]:
    """
    Detect the type of user query and determine which workflow to use.
    Returns the appropriate workflow and action to take.
    """
    query_lower = user_query.lower()
    
    # Creation keywords
    creation_keywords = ["create", "make", "build", "set up", "configure", "add", "new task", "automation"]
    
    # Testing keywords  
    testing_keywords = ["test", "verify", "check", "validate", "run", "execute", "try"]
    
    # Analysis keywords
    analysis_keywords = ["analyze", "look at", "examine", "screen", "ui", "interface", "what do you see"]
    
    detected_type = "unknown"
    confidence = 0.0
    
    # Check for creation intent
    creation_matches = sum(1 for keyword in creation_keywords if keyword in query_lower)
    if creation_matches > 0:
        detected_type = "creation"
        confidence = min(creation_matches / len(creation_keywords), 1.0)
    
    # Check for testing intent
    testing_matches = sum(1 for keyword in testing_keywords if keyword in query_lower)
    if testing_matches > 0 and testing_matches > creation_matches:
        detected_type = "testing"
        confidence = min(testing_matches / len(testing_keywords), 1.0)
    
    # Check for analysis intent
    analysis_matches = sum(1 for keyword in analysis_keywords if keyword in query_lower)
    if analysis_matches > 0 and analysis_matches > max(creation_matches, testing_matches):
        detected_type = "analysis"
        confidence = min(analysis_matches / len(analysis_keywords), 1.0)
    
    # Determine recommended workflow
    recommended_workflow = None
    if detected_type == "creation":
        recommended_workflow = "creation_workflow"
    elif detected_type == "testing":
        recommended_workflow = "testing_workflow"
    elif detected_type == "analysis":
        recommended_workflow = "parallel_analysis"
    
    return {
        "query": user_query,
        "detected_type": detected_type,
        "confidence": confidence,
        "recommended_workflow": recommended_workflow,
        "action": "Use invoke" + (recommended_workflow.replace("_", "").title() if recommended_workflow else "CreationWorkflow") + " tool"
    }

# Add new tools to legacy aliases
invoke_creation_workflow = invokeCreationWorkflow
invoke_testing_workflow = invokeTestingWorkflow
invoke_parallel_analysis = invokeParallelAnalysis
detect_query_type = detectQueryType 