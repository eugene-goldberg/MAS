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

"""Test cases for the MAS Coordinator intent routing."""

import textwrap

import dotenv
import pytest
from mas_system.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.genai import types

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


@pytest.mark.asyncio
async def test_weather_routing():
    """Test that weather requests are properly routed to weather agent."""
    user_input = "What's the weather in New York?"
    
    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )
    content = types.UserContent(parts=[types.Part(text=user_input)])
    
    response = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        print(event)
        if event.content.parts and event.content.parts[0].text:
            response = event.content.parts[0].text
    
    # Should mention routing to weather agent
    assert "weather" in response.lower()
    # Should contain actual weather data (temperature, conditions, etc.)
    assert any(word in response.lower() for word in ["°f", "degrees", "temperature"])


@pytest.mark.asyncio
async def test_calculator_routing():
    """Test that calculation requests are properly routed to calculator agent."""
    user_input = "Calculate 15% tip on $85.50"
    
    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )
    content = types.UserContent(parts=[types.Part(text=user_input)])
    
    response = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        print(event)
        if event.content.parts and event.content.parts[0].text:
            response = event.content.parts[0].text
    
    # Should contain tip calculation results
    assert "$" in response
    assert "tip" in response.lower()
    # Should show both tip amount and total
    assert any(word in response.lower() for word in ["12.83", "98.33", "total"])


@pytest.mark.asyncio
async def test_unit_conversion_routing():
    """Test that unit conversion requests are routed to calculator agent."""
    user_input = "Convert 20 degrees Celsius to Fahrenheit"
    
    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )
    content = types.UserContent(parts=[types.Part(text=user_input)])
    
    response = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        print(event)
        if event.content.parts and event.content.parts[0].text:
            response = event.content.parts[0].text
    
    # Should contain conversion result
    assert "68" in response  # 20°C = 68°F
    assert any(symbol in response for symbol in ["°F", "fahrenheit"])


@pytest.mark.asyncio
async def test_ambiguous_request():
    """Test handling of potentially ambiguous requests."""
    user_input = "I need help with the temperature"
    
    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )
    content = types.UserContent(parts=[types.Part(text=user_input)])
    
    response = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        print(event)
        if event.content.parts and event.content.parts[0].text:
            response = event.content.parts[0].text
    
    # Should make a reasonable routing decision
    assert response != ""
    # Should route to one of the agents
    assert any(agent in response.lower() for agent in ["weather", "calculator"])