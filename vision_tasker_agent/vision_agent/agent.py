from google.adk.agents import Agent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools import captureScreen, analyzeImage

vision_agent = Agent(
    name="vision_agent",
    description="Sub-agent for capturing and analyzing Pixel screen via Gemini vision.",
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