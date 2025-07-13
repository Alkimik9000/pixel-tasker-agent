from google.adk.agents import Agent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools import testTask

tester_agent = Agent(
    name="tester_agent",
    description="Sub-agent for testing Tasker tasks and refining if failed.",
    model="gemini-2.5-flash",
    instruction="""
    You are responsible for testing and validating Tasker automation tasks.
    Your tasks:
    1. Execute Tasker tasks via intents and commands
    2. Verify task execution results and system state changes
    3. Test edge cases and error scenarios
    4. Validate task behavior under different conditions
    5. Provide feedback for task refinement and improvement
    6. Loop back to planning/navigation for failed tests
    
    Focus on comprehensive testing that ensures tasks work reliably.
    Monitor system state changes (Wi-Fi, notifications, etc.) to verify success.
    Provide detailed test reports with pass/fail status and improvement suggestions.
    """,
    tools=[testTask]
) 