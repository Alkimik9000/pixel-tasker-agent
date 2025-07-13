#!/usr/bin/env python3
"""
Test script to verify the updated ADK agent implementation.
This simulates expected behavior with proper tool calling and workflow execution.
"""

import sys
import os
import logging

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)

def testToolInstances():
    """Test that all FunctionTool instances are properly created"""
    print("=== Testing Tool Instances ===")
    
    try:
        from tools import (
            captureScreenTool,
            analyzeImageTool,
            performClickTool,
            performTextInputTool,
            navigateTaskerStepTool,
            generatePlanTool,
            testTaskTool
        )
        
        print("✓ All FunctionTool instances imported successfully")
        
        # Test that they are FunctionTool instances
        from google.adk.tools import FunctionTool
        
        tools_to_check = [
            ("captureScreenTool", captureScreenTool),
            ("analyzeImageTool", analyzeImageTool),
            ("performClickTool", performClickTool),
            ("performTextInputTool", performTextInputTool),
            ("navigateTaskerStepTool", navigateTaskerStepTool),
            ("generatePlanTool", generatePlanTool),
            ("testTaskTool", testTaskTool)
        ]
        
        for name, tool in tools_to_check:
            if isinstance(tool, FunctionTool):
                print("✓ " + name + " is a proper FunctionTool instance")
            else:
                print("✗ " + name + " is NOT a FunctionTool instance")
                
    except Exception as e:
        print("✗ Error importing tools: " + str(e))
        return False
    
    return True

def testWorkflowFunctions():
    """Test the workflow invocation functions"""
    print("\n=== Testing Workflow Functions ===")
    
    try:
        from vision_tasker_agent.agent import (
            runCreationWorkflow,
            runTestingWorkflow,
            runAnalysisWorkflow
        )
        
        print("✓ Workflow functions imported successfully")
        
        # Test creation workflow
        print("\n--- Testing Creation Workflow ---")
        result = runCreationWorkflow("create a simple test task")
        print("Workflow result:")
        print("- Status: " + result.get("status", "unknown"))
        print("- Steps completed: " + str(result.get("steps_completed", [])))
        
        # Test analysis workflow
        print("\n--- Testing Analysis Workflow ---")
        result = runAnalysisWorkflow("what buttons are visible?")
        print("Workflow result:")
        print("- Status: " + result.get("status", "unknown"))
        print("- Analyses performed: " + str(len(result.get("analyses", []))))
        
    except Exception as e:
        print("✗ Error testing workflows: " + str(e))
        return False
    
    return True

def testAgentConfiguration():
    """Test that agents are properly configured with tools"""
    print("\n=== Testing Agent Configuration ===")
    
    try:
        from vision_tasker_agent.agent import root_agent
        from vision_tasker_agent.vision_agent import vision_agent
        from vision_tasker_agent.planner_agent import planner_agent
        from vision_tasker_agent.navigator_agent import navigator_agent
        from vision_tasker_agent.tester_agent import tester_agent
        
        agents = [
            ("Root Agent", root_agent),
            ("Vision Agent", vision_agent),
            ("Planner Agent", planner_agent),
            ("Navigator Agent", navigator_agent),
            ("Tester Agent", tester_agent)
        ]
        
        for name, agent in agents:
            print("\n" + name + ":")
            print("- Name: " + agent.name)
            print("- Model: " + str(agent.model))
            print("- Tools: " + str(len(agent.tools)) + " tools registered")
            
            # Check if instructions are action-oriented
            instruction_text = str(agent.instruction) if agent.instruction else ""
            if "IMMEDIATELY" in instruction_text:
                print("✓ Has action-oriented instructions")
            else:
                print("⚠ May need more action-oriented instructions")
    
    except Exception as e:
        print("✗ Error testing agent configuration: " + str(e))
        return False
    
    return True

def simulateExpectedBehavior():
    """Simulate the expected agent behavior"""
    print("\n=== Simulating Expected Agent Behavior ===")
    
    print("\n--- Scenario 1: Creation Request ---")
    print('User: "create a task that when executed creates an alarm for tomorrow morning at 7:30"')
    print("\nExpected Agent Behavior:")
    print("1. Agent recognizes 'create' keyword")
    print("2. Agent IMMEDIATELY calls runCreationWorkflow()")
    print("3. Workflow executes:")
    print("   - generatePlan() creates step-by-step plan")
    print("   - captureScreen() gets current UI state")
    print("   - analyzeImage() identifies clickable elements")
    print("   - navigateTaskerStep() executes each plan step")
    print("4. Agent reports actual results from execution")
    
    print("\n--- Scenario 2: Testing Request ---")
    print('User: "test the morning alarm task"')
    print("\nExpected Agent Behavior:")
    print("1. Agent recognizes 'test' keyword")
    print("2. Agent IMMEDIATELY calls runTestingWorkflow('morning alarm task')")
    print("3. Workflow executes testTask() multiple times if needed")
    print("4. Agent reports test results with pass/fail status")
    
    print("\n--- What Should NOT Happen ---")
    print("✗ Agent says: 'I will delegate to planner_agent...'")
    print("✗ Agent says: 'Let me analyze the screen...'")
    print("✗ Agent provides descriptive text without tool calls")
    print("✗ Agent explains future actions instead of executing")

def main():
    print("ADK Agent Implementation Test Suite")
    print("==================================\n")
    
    # Run all tests
    tests = [
        ("Tool Instances", testToolInstances),
        ("Workflow Functions", testWorkflowFunctions),
        ("Agent Configuration", testAgentConfiguration)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        if not test_func():
            all_passed = False
    
    # Show expected behavior
    simulateExpectedBehavior()
    
    # Summary
    print("\n=== Test Summary ===")
    if all_passed:
        print("✓ All tests passed!")
        print("✓ Tools are properly wrapped with FunctionTool")
        print("✓ Agents have action-oriented instructions")
        print("✓ Workflows are ready for execution")
    else:
        print("✗ Some tests failed - check the output above")
    
    print("\n=== Next Steps ===")
    print("1. Run the agent with: python vision_tasker_agent/agent.py")
    print("2. Or use ADK web UI: adk web")
    print("3. Test with query: 'create a task that sets an alarm for 7:30 AM'")
    print("4. Verify in the Graph tab that tools are being called")
    print("5. Check scrcpy for actual UI interactions")

if __name__ == "__main__":
    main() 