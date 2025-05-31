#!/usr/bin/env python3
"""Debug the calculator agent to see what it returns."""

# Test the string_math functions directly
from mas_system.sub_agents.calculator_agent.tools import string_math

# Test direct function calls
print("Testing string_math functions directly:")
print("=" * 60)

# Test addition
result = string_math.add_and_format(15, 27)
print(f"add_and_format(15, 27) = {result}")

# Test multiplication  
result = string_math.multiply_and_format(25, 4)
print(f"multiply_and_format(25, 4) = {result}")

# Test square root
result = string_math.square_root_and_format(144)
print(f"square_root_and_format(144) = {result}")

print("\n" + "=" * 60)
print("Testing calculator agent:")

# Import the agent
from mas_system.sub_agents.calculator_agent import calculator_agent
from google.adk.tools.agent_tool import AgentTool

# Create an AgentTool wrapper around calculator_agent
calculator_tool = AgentTool(agent=calculator_agent)

# Show tool info
print(f"\nTool name: {calculator_tool.name}")
print(f"Tool description: {calculator_tool.description}")

# Try to invoke the tool as MAS coordinator would
print("\n" + "=" * 60)
print("Testing AgentTool invocation:")

try:
    # Check available methods
    print("Available methods on calculator_tool:")
    for attr in dir(calculator_tool):
        if not attr.startswith('_'):
            print(f"  - {attr}")
    
    # Try different invocation methods
    if hasattr(calculator_tool, '__call__'):
        print("\nTrying calculator_tool('What is 15 + 27?')...")
        result = calculator_tool("What is 15 + 27?")
        print(f"Result: {result}")
    elif hasattr(calculator_tool, 'run'):
        print("\nTrying calculator_tool.run('What is 15 + 27?')...")
        result = calculator_tool.run("What is 15 + 27?")
        print(f"Result: {result}")
        
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e)}")
    
# Also test the agent directly
print("\n" + "=" * 60)
print("Testing calculator_agent directly:")
print("Available methods on calculator_agent:")
for attr in dir(calculator_agent):
    if not attr.startswith('_') and not attr.startswith('model_'):
        print(f"  - {attr}")