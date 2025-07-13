from google.adk.agents import Agent
from google.adk.tools import google_search
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools import generatePlan

planner_agent = Agent(
    name="planner_agent",
    description="Sub-agent for planning Tasker tasks from user descriptions.",
    model="gemini-2.5-flash",
    instruction="""
    You are responsible for creating detailed plans for Tasker automation tasks.
    Your tasks:
    1. Break down user descriptions into step-by-step JSON plans
    2. Research Tasker actions and functionality when needed
    3. Generate comprehensive task structures with proper parameters
    4. Refine plans based on feedback from testing or execution
    5. Ensure plans are actionable and compatible with Tasker UI navigation
    
    Focus on creating structured, logical sequences that can be executed by the navigator agent.
    Include all necessary details like action types, parameters, and conditional logic.
    Always output plans in JSON format with clear step descriptions.
    """,
    tools=[generatePlan, google_search]
) 