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

"""Multi-Agent System: Coordinator that routes requests to specialized sub-agents."""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from .sub_agents.weather_agent import weather_agent
from .sub_agents.greeter_agent import greeter_agent
from .sub_agents.academic_wrapper import academic_websearch_wrapper, academic_newresearch_wrapper
from .sub_agents.rag_agent import rag_agent

MODEL = "gemini-2.0-flash-001"


mas_coordinator = LlmAgent(
    name="mas_coordinator",
    model=MODEL,
    description=(
        "Main coordinator that intelligently routes user requests to "
        "the weather agent for weather-related queries, "
        "the greeter agent for greetings and welcomes, "
        "the academic newresearch agent for finding recent research papers, "
        "the academic websearch agent for searching academic content online, or "
        "the rag agent for document-based knowledge retrieval and corpus management"
    ),
    instruction=prompt.MAS_COORDINATOR_PROMPT,
    tools=[
        AgentTool(agent=weather_agent),
        AgentTool(agent=greeter_agent),
        AgentTool(agent=academic_newresearch_wrapper),
        AgentTool(agent=academic_websearch_wrapper),
        AgentTool(agent=rag_agent),
    ],
)

root_agent = mas_coordinator