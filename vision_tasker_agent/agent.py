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
from tools import captureScreen, analyzeImage

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
    Coordinate sub-agents to create, navigate, and test Tasker tasks:
    
    1. Use planner_agent to break down user requests into structured plans
    2. Use vision_agent to analyze screen state and identify UI elements
    3. Use navigator_agent to execute UI interactions and navigation
    4. Use tester_agent to validate and refine created tasks
    
    Available workflows:
    - creation_workflow: Sequential planning → vision → navigation
    - testing_workflow: Iterative testing with refinement loop
    - parallel_analysis: Parallel vision analysis for complex screens
    
    Delegate tasks to appropriate sub-agents and orchestrate the overall flow.
    Monitor progress and handle coordination between agents.
    """,
    tools=[google_search]  # Tools delegated to sub-agents
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