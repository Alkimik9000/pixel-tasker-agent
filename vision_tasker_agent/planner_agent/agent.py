from google.adk.agents import Agent
from google.adk.tools import google_search
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools import generatePlanTool

planner_agent = Agent(
    name="planner_agent",
    description="Sub-agent for planning Tasker tasks from user descriptions.",
    model="gemini-2.0-flash",
    instruction="""You are a Tasker automation planning specialist.

Your primary responsibility is to IMMEDIATELY generate detailed plans when requested.

CRITICAL RULES:
1. When given a task description, IMMEDIATELY call generatePlan tool
2. Do NOT describe what you will do - execute the tool and report results
3. Generate comprehensive, actionable plans with specific UI steps

Your plans must include:
- Exact UI elements to interact with (buttons, menus, fields)
- Specific text to input where needed
- Clear sequence of actions
- Navigation paths through Tasker UI

If additional research is needed about Tasker functionality:
- Use google_search to find Tasker documentation
- Then immediately generate the plan based on findings

EXAMPLE:
User: "Plan a task to set an alarm"
You: [IMMEDIATELY call generatePlan("set an alarm")]
Then present the structured plan result.""",
    tools=[generatePlanTool, google_search]
) 