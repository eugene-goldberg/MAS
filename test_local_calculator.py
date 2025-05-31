#!/usr/bin/env python3
"""Test the calculator agent locally."""

from mas_system.sub_agents.calculator_agent import calculator_agent

# Test the calculator agent locally
print("Testing calculator agent locally...")

# Test 1: Addition
print("\nTest 1 - Addition: What is 15 + 27?")
response = calculator_agent.run("What is 15 + 27?")
print(f"Response: {response}")

# Test 2: Multiplication
print("\nTest 2 - Multiplication: Calculate 25 times 4")
response = calculator_agent.run("Calculate 25 times 4")
print(f"Response: {response}")

# Test 3: Square root
print("\nTest 3 - Square root: What is the square root of 144?")
response = calculator_agent.run("What is the square root of 144?")
print(f"Response: {response}")
