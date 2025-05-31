#!/usr/bin/env python3
"""Direct test of MAS calculator functionality"""

import vertexai
from vertexai import agent_engines
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "pickuptruckapp")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Initialize Vertex AI
vertexai.init(project=project_id, location=location)

# Get the agent
agent_id = "7391717606375292928"  # Latest MAS deployment with improved calculator prompt
remote_agent = agent_engines.get(agent_id)

# Create a session
session = remote_agent.create_session(user_id="direct_test")

# Test calculator
print("Testing calculator agent...")
print("Question: What is 15 + 27?")
for event in remote_agent.stream_query(
    user_id="direct_test", session_id=session["id"], message="What is 15 + 27?"
):
    if "content" in event:
        if "parts" in event["content"]:
            parts = event["content"]["parts"]
            for part in parts:
                if "text" in part:
                    text_part = part["text"]
                    print(f"Response: {text_part}")

# Test another calculation
print("\n\nTesting multiplication...")
print("Question: Calculate 25 times 4")
for event in remote_agent.stream_query(
    user_id="direct_test", session_id=session["id"], message="Calculate 25 times 4"
):
    if "content" in event:
        if "parts" in event["content"]:
            parts = event["content"]["parts"]
            for part in parts:
                if "text" in part:
                    text_part = part["text"]
                    print(f"Response: {text_part}")

# Test weather
print("\n\nTesting weather agent...")
print("Question: What's the weather in San Francisco?")
for event in remote_agent.stream_query(
    user_id="direct_test", session_id=session["id"], message="What's the weather in San Francisco?"
):
    if "content" in event:
        if "parts" in event["content"]:
            parts = event["content"]["parts"]
            for part in parts:
                if "text" in part:
                    text_part = part["text"]
                    print(f"Response: {text_part}")

# Test greeter
print("\n\nTesting greeter agent...")
print("Question: Hello, my name is John!")
for event in remote_agent.stream_query(
    user_id="direct_test", session_id=session["id"], message="Hello, my name is John!"
):
    if "content" in event:
        if "parts" in event["content"]:
            parts = event["content"]["parts"]
            for part in parts:
                if "text" in part:
                    text_part = part["text"]
                    print(f"Response: {text_part}")