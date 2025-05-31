#!/usr/bin/env python3
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv
import os

load_dotenv()

def delete_agent(resource_id: str):
    """Delete a deployed agent from Vertex AI Agent Engine."""
    
    # Initialize Vertex AI
    cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
    cloud_location = os.getenv("GOOGLE_CLOUD_LOCATION")
    
    vertexai.init(
        project=cloud_project,
        location=cloud_location,
    )
    
    # Construct full resource name if only ID is provided
    if not resource_id.startswith("projects/"):
        resource_name = f"projects/{cloud_project}/locations/{cloud_location}/reasoningEngines/{resource_id}"
    else:
        resource_name = resource_id
    
    print(f"Deleting agent: {resource_name}")
    
    try:
        # Get the agent engine
        agent_engine = agent_engines.get(resource_name)
        
        # Delete the agent with force=True to delete child resources
        operation = agent_engine.delete(force=True)
        
        print("Delete operation initiated (force=True).")
        print(f"Operation: {operation}")
        print("Agent deletion in progress...")
        
        # Wait for the operation to complete
        result = operation.result()
        print("Agent deleted successfully!")
        
    except Exception as e:
        print(f"Error deleting agent: {str(e)}")
        return False
    
    return True

def list_agents():
    """List all deployed agents."""
    
    # Initialize Vertex AI
    cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
    cloud_location = os.getenv("GOOGLE_CLOUD_LOCATION")
    
    vertexai.init(
        project=cloud_project,
        location=cloud_location,
    )
    
    print(f"Listing agents in project: {cloud_project}, location: {cloud_location}")
    print("-" * 80)
    
    try:
        # List all reasoning engines (agents)
        agents = agent_engines.list()
        
        if not agents:
            print("No agents found.")
            return
        
        for agent in agents:
            print(f"Name: {agent.name}")
            print(f"Display Name: {agent.display_name}")
            print(f"Created: {agent.create_time}")
            print(f"Updated: {agent.update_time}")
            print("-" * 40)
            
    except Exception as e:
        print(f"Error listing agents: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Delete or list Vertex AI Agent Engine deployments")
    parser.add_argument("--delete", type=str, help="Agent resource ID or full resource name to delete")
    parser.add_argument("--list", action="store_true", help="List all deployed agents")
    
    args = parser.parse_args()
    
    if args.delete:
        delete_agent(args.delete)
    elif args.list:
        list_agents()
    else:
        print("Please specify --delete <resource_id> or --list")
        parser.print_help()

if __name__ == "__main__":
    main()