# Install required package: pip install google-adk
from google.adk.agents import Agent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.loop_agent import LoopAgent
from google.adk.tools import google_search  # Optional for research
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import tools for creating new agent instances
from tools import captureScreen, analyzeImage, detectQueryType, invokeCreationWorkflow, invokeTestingWorkflow, invokeParallelAnalysis

# Import sub-agents
from vision_tasker_agent.vision_agent import vision_agent
from vision_tasker_agent.planner_agent import planner_agent
from vision_tasker_agent.navigator_agent import navigator_agent
from vision_tasker_agent.tester_agent import tester_agent

# Root agent oversees workflows
root_agent = Agent(
    name="pixel_tasker_agent",
    description="Root agent orchestrating multi-agent Tasker automation.",
    model="gemini-2.5-flash",
    instruction="""
    You are the root orchestrator for Tasker automation on Pixel 8 Pro. 
    
    CRITICAL: You must ALWAYS use tools to respond to user queries. Never provide descriptive text about what you "will do" - instead, immediately call the appropriate tools.
    
    For EVERY user query, follow this process:
    1. FIRST: Call detectQueryType tool to analyze the user's request
    2. THEN: Based on the detection result, immediately call the appropriate workflow tool:
       - For creation queries: Call invokeCreationWorkflow tool
       - For testing queries: Call invokeTestingWorkflow tool  
       - For analysis queries: Call invokeParallelAnalysis tool
    3. NEVER explain what you will do - just execute the tools
    
    EXAMPLE WORKFLOW:
    User: "create a task that when executed creates an alarm for tomorrow morning at 7:30"
    YOU MUST: 
    1. Call detectQueryType with the user query
    2. Call invokeCreationWorkflow with the user query
    3. Report the results from the workflow execution
    
    DO NOT SAY: "I will delegate to planner_agent..." or "Here's how I will proceed..."
    INSTEAD DO: Immediately call the tools and report their results.
    
    Available tools:
    - detectQueryType: Analyze user query and determine workflow type
    - invokeCreationWorkflow: Execute creation workflow (planner → vision → navigator)
    - invokeTestingWorkflow: Execute testing workflow (tester agent loop)
    - invokeParallelAnalysis: Execute parallel vision analysis workflow
    - captureScreen: Capture device screen
    - analyzeImage: Analyze screen with Gemini vision
    
    Your responses should be based on actual tool execution results, not descriptions of future actions.
    """,
    tools=[detectQueryType, invokeCreationWorkflow, invokeTestingWorkflow, invokeParallelAnalysis, captureScreen, analyzeImage, google_search]
)

# Define workflows using correct ADK workflow agents
# Note: Each agent can only have one parent, so we create separate instances for each workflow

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
from google.adk.agents import Agent
vision_agent_1 = Agent(
    name="vision_agent_1",
    description="Sub-agent for capturing and analyzing Pixel screen via Gemini vision (parallel instance 1).",
    model="gemini-2.5-flash",
    instruction="""
    You are responsible for visual analysis of the Pixel 8 Pro screen.
    Your tasks:
    1. Capture screen screenshots of the current UI state
    2. Analyze images using Gemini vision to identify UI elements
    3. Provide bounding boxes and click coordinates for interactive elements
    4. Describe the current screen state for navigation planning
    5. Detect specific UI elements requested by other agents
    
    Always provide detailed descriptions with normalized coordinates and absolute pixel coordinates.
    Focus on actionable UI elements like buttons, text fields, and navigation elements.
    """,
    tools=[captureScreen, analyzeImage]
)

vision_agent_2 = Agent(
    name="vision_agent_2",
    description="Sub-agent for capturing and analyzing Pixel screen via Gemini vision (parallel instance 2).",
    model="gemini-2.5-flash",
    instruction="""
    You are responsible for visual analysis of the Pixel 8 Pro screen.
    Your tasks:
    1. Capture screen screenshots of the current UI state
    2. Analyze images using Gemini vision to identify UI elements
    3. Provide bounding boxes and click coordinates for interactive elements
    4. Describe the current screen state for navigation planning
    5. Detect specific UI elements requested by other agents
    
    Always provide detailed descriptions with normalized coordinates and absolute pixel coordinates.
    Focus on actionable UI elements like buttons, text fields, and navigation elements.
    """,
    tools=[captureScreen, analyzeImage]
)

# Optional parallel workflow for complex screen analysis
parallel_analysis = ParallelAgent(
    name="parallel_analysis",
    sub_agents=[vision_agent_1, vision_agent_2]  # Use separate instances
) 