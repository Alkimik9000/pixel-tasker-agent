# Install required package: pip install google-adk
from google.adk.agents import Agent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.loop_agent import LoopAgent
from google.adk.tools import google_search, FunctionTool
import sys
import os
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import tool instances from tools.py
from tools import (
    captureScreenTool, 
    analyzeImageTool, 
    performClickTool, 
    performTextInputTool, 
    navigateTaskerStepTool, 
    generatePlanTool, 
    testTaskTool
)

# Import sub-agents
from vision_tasker_agent.vision_agent import vision_agent
from vision_tasker_agent.planner_agent import planner_agent
from vision_tasker_agent.navigator_agent import navigator_agent
from vision_tasker_agent.tester_agent import tester_agent

# Workflow invocation functions - these will be wrapped as tools
def runCreationWorkflow(user_query: str) -> Dict[str, Any]:
    """Execute the full creation workflow for creating a Tasker task.
    
    This tool runs the complete sequential workflow: planner -> vision -> navigator.
    It automatically executes all steps needed to create a Tasker automation.
    
    Args:
        user_query: Natural language description of the task to create
    
    Returns:
        dict: Contains workflow execution status and results from each step.
    """
    logger.info("Executing creation workflow for: " + user_query)
    
    workflow_result = {
        "workflow": "creation_workflow",
        "query": user_query,
        "steps_completed": []
    }
    
    try:
        # Step 1: Generate plan using planner agent
        logger.info("Step 1: Generating plan...")
        from tools import generatePlan
        plan_result = generatePlan(user_query)
        workflow_result["plan"] = plan_result
        workflow_result["steps_completed"].append("planning")
        
        if not plan_result.get("success", False):
            workflow_result["status"] = "failed"
            workflow_result["error"] = "Plan generation failed"
            return workflow_result
        
        # Step 2: Analyze current screen using vision agent
        logger.info("Step 2: Analyzing current screen...")
        from tools import captureScreen, analyzeImage
        screen_result = captureScreen()
        if screen_result.get("success"):
            analysis_result = analyzeImage(
                screen_result["image_path"],
                "Analyze Tasker UI and identify all clickable elements"
            )
            workflow_result["vision_analysis"] = analysis_result
            workflow_result["steps_completed"].append("vision_analysis")
        
        # Step 3: Execute navigation steps
        logger.info("Step 3: Executing navigation steps...")
        plan_steps = plan_result.get("plan", {})
        if isinstance(plan_steps, dict) and "steps" in plan_steps:
            for step in plan_steps["steps"]:
                step_desc = step.get("ui_element", step.get("action", ""))
                if step_desc:
                    from tools import navigateTaskerStep
                    nav_result = navigateTaskerStep(step_desc)
                    workflow_result["steps_completed"].append("navigate: " + step_desc)
                    if not nav_result.get("success", False):
                        logger.warning("Navigation step failed: " + step_desc)
        
        workflow_result["status"] = "completed"
        workflow_result["message"] = "Creation workflow completed successfully"
        
    except Exception as e:
        logger.error("Creation workflow failed: " + str(e))
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
    
    return workflow_result

def runTestingWorkflow(task_name: str) -> Dict[str, Any]:
    """Execute the testing workflow to validate a Tasker task.
    
    This tool runs the testing loop to verify that a created task works correctly.
    It can perform multiple test iterations if needed.
    
    Args:
        task_name: Name of the Tasker task to test
    
    Returns:
        dict: Contains test results and any identified issues.
    """
    logger.info("Executing testing workflow for task: " + task_name)
    
    workflow_result = {
        "workflow": "testing_workflow",
        "task_name": task_name,
        "iterations": []
    }
    
    try:
        max_iterations = 3
        for i in range(max_iterations):
            logger.info("Test iteration " + str(i + 1))
            from tools import testTask
            test_result = testTask(task_name)
            
            iteration_result = {
                "iteration": i + 1,
                "result": test_result
            }
            workflow_result["iterations"].append(iteration_result)
            
            if test_result.get("passed", False):
                workflow_result["status"] = "passed"
                workflow_result["message"] = "Task tested successfully"
                break
        else:
            workflow_result["status"] = "failed"
            workflow_result["message"] = "Task failed after " + str(max_iterations) + " attempts"
    
    except Exception as e:
        logger.error("Testing workflow failed: " + str(e))
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
    
    return workflow_result

def runAnalysisWorkflow(screen_query: str) -> Dict[str, Any]:
    """Execute parallel screen analysis for complex UI understanding.
    
    This tool performs detailed analysis of the current screen using multiple
    vision agents in parallel for comprehensive UI understanding.
    
    Args:
        screen_query: Specific query about what to analyze on the screen
    
    Returns:
        dict: Contains detailed analysis results from multiple perspectives.
    """
    logger.info("Executing parallel analysis workflow: " + screen_query)
    
    workflow_result = {
        "workflow": "parallel_analysis",
        "query": screen_query,
        "analyses": []
    }
    
    try:
        from tools import captureScreen, analyzeImage
        
        # Capture screen once
        screen_result = captureScreen()
        if not screen_result.get("success"):
            workflow_result["status"] = "failed"
            workflow_result["error"] = "Screen capture failed"
            return workflow_result
        
        # Run multiple analyses in parallel (simulated)
        analysis_queries = [
            "Identify all clickable buttons and their labels",
            "Find all text input fields and their current values",
            "Locate navigation elements like back buttons or menus",
            screen_query  # User's specific query
        ]
        
        for query in analysis_queries:
            analysis_result = analyzeImage(screen_result["image_path"], query)
            workflow_result["analyses"].append({
                "query": query,
                "result": analysis_result
            })
        
        workflow_result["status"] = "completed"
        workflow_result["message"] = "Parallel analysis completed"
        
    except Exception as e:
        logger.error("Analysis workflow failed: " + str(e))
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
    
    return workflow_result

# Create FunctionTool wrappers for the workflow functions
runCreationWorkflowTool = FunctionTool(runCreationWorkflow)
runTestingWorkflowTool = FunctionTool(runTestingWorkflow)
runAnalysisWorkflowTool = FunctionTool(runAnalysisWorkflow)

# Root agent with action-oriented instructions
root_agent = Agent(
    name="pixel_tasker_agent",
    description="Root agent orchestrating multi-agent Tasker automation.",
    model="gemini-2.0-flash",
    instruction="""You are a Tasker automation assistant for Pixel 8 Pro. You MUST IMMEDIATELY execute tools based on user requests.

CRITICAL RULES:
1. NEVER describe what you will do. ALWAYS execute tools immediately.
2. For ANY user request, determine the intent and IMMEDIATELY call the appropriate tool.
3. DO NOT say "I will..." or "Let me..." - just execute tools and report results.

TOOL USAGE PATTERNS:

For CREATION requests (keywords: create, make, build, set up, add):
→ IMMEDIATELY call runCreationWorkflow with the user's request

For TESTING requests (keywords: test, verify, check, validate):
→ IMMEDIATELY call runTestingWorkflow with the task name

For ANALYSIS requests (keywords: analyze, look at, examine, what's on screen):
→ IMMEDIATELY call runAnalysisWorkflow with the analysis query

For SPECIFIC ACTIONS:
- To capture screen → call captureScreen
- To analyze an image → call analyzeImage with image path and query
- To click somewhere → call performClick with x,y coordinates
- To input text → call performTextInput with the text
- To navigate UI → call navigateTaskerStep with step description

EXAMPLE INTERACTIONS:

User: "create a task that sets an alarm for 7:30 AM"
You: [IMMEDIATELY call runCreationWorkflow("create a task that sets an alarm for 7:30 AM")]
Then report the actual results.

User: "test the morning alarm task"
You: [IMMEDIATELY call runTestingWorkflow("morning alarm task")]
Then report the test results.

User: "what's on the screen?"
You: [IMMEDIATELY call runAnalysisWorkflow("describe all UI elements on screen")]
Then report what was found.

NEVER provide explanatory text before executing tools. Execute first, explain results after.""",
    tools=[
        runCreationWorkflowTool,
        runTestingWorkflowTool,
        runAnalysisWorkflowTool,
        captureScreenTool,
        analyzeImageTool,
        performClickTool,
        performTextInputTool,
        navigateTaskerStepTool,
        generatePlanTool,
        testTaskTool,
        google_search
    ]
)

# Define the actual workflow agents (these are orchestrated by the root agent's tools)
creation_workflow = SequentialAgent(
    name="creation_workflow",
    sub_agents=[
        planner_agent,  # Step 1: Plan the task
        vision_agent,   # Step 2: Analyze current screen
        navigator_agent # Step 3: Execute navigation
    ]
)

testing_workflow = LoopAgent(
    name="testing_workflow",
    sub_agents=[tester_agent],
    max_iterations=3
)

# For parallel analysis, we need to create separate vision agent instances
# since each agent can only have one parent in ADK
vision_agent_1 = Agent(
    name="vision_agent_1",
    description="Sub-agent for capturing and analyzing Pixel screen via Gemini vision (parallel instance 1).",
    model="gemini-2.0-flash",
    instruction="""You are responsible for visual analysis of the Pixel 8 Pro screen.
    Your tasks:
    1. Capture screen screenshots of the current UI state
    2. Analyze images using Gemini vision to identify UI elements
    3. Provide bounding boxes and click coordinates for interactive elements
    4. Describe the current screen state for navigation planning
    5. Detect specific UI elements requested by other agents
    
    Always provide detailed descriptions with normalized coordinates and absolute pixel coordinates.
    Focus on actionable UI elements like buttons, text fields, and navigation elements.""",
    tools=[captureScreenTool, analyzeImageTool]
)

vision_agent_2 = Agent(
    name="vision_agent_2",
    description="Sub-agent for capturing and analyzing Pixel screen via Gemini vision (parallel instance 2).",
    model="gemini-2.0-flash",
    instruction="""You are responsible for visual analysis of the Pixel 8 Pro screen.
    Your tasks:
    1. Capture screen screenshots of the current UI state
    2. Analyze images using Gemini vision to identify UI elements
    3. Provide bounding boxes and click coordinates for interactive elements
    4. Describe the current screen state for navigation planning
    5. Detect specific UI elements requested by other agents
    
    Always provide detailed descriptions with normalized coordinates and absolute pixel coordinates.
    Focus on actionable UI elements like buttons, text fields, and navigation elements.""",
    tools=[captureScreenTool, analyzeImageTool]
)

# Optional parallel workflow for complex screen analysis
parallel_analysis = ParallelAgent(
    name="parallel_analysis",
    sub_agents=[vision_agent_1, vision_agent_2]  # Use separate instances
) 