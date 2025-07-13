from google.adk.agents import Agent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools import performClick, navigateTaskerStep, performTextInput

navigator_agent = Agent(
    name="navigator_agent",
    description="Sub-agent for navigating Tasker UI on Pixel via clicks and inputs.",
    model="gemini-2.5-flash",
    instruction="""
    You are responsible for executing UI navigation and interaction on the Pixel 8 Pro.
    Your tasks:
    1. Execute clicks on UI elements using coordinates from vision analysis
    2. Navigate through Tasker UI following step-by-step plans
    3. Input text into form fields and text areas
    4. Launch applications and navigate between screens
    5. Handle UI state changes and transitions
    6. Retry failed actions with different approaches
    
    Use vision data to understand current UI state and execute precise actions.
    Always verify successful navigation before proceeding to next steps.
    Handle errors gracefully and provide detailed feedback on action results.
    """,
    tools=[performClick, navigateTaskerStep, performTextInput]
) 