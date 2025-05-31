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

"""Test cases for the Weather Sub-Agent."""

import dotenv
import pytest
from mas_system.sub_agents.weather_agent import weather_agent
from google.adk.runners import InMemoryRunner
from google.genai import types

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


@pytest.mark.asyncio
async def test_current_weather():
    """Test getting current weather for a location."""
    user_input = "What's the current weather in London?"
    
    runner = InMemoryRunner(agent=weather_agent)
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
    
    # Should contain weather information
    assert "london" in response.lower()
    assert any(word in response.lower() for word in ["temperature", "°f", "degrees"])
    assert any(word in response.lower() for word in ["humidity", "wind", "conditions"])


@pytest.mark.asyncio
async def test_weather_forecast():
    """Test getting weather forecast."""
    user_input = "Give me a 3-day forecast for Tokyo"
    
    runner = InMemoryRunner(agent=weather_agent)
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
    
    # Should contain forecast information
    assert "tokyo" in response.lower()
    assert any(word in response.lower() for word in ["forecast", "high", "low"])
    # Should have multiple days
    assert response.count("High:") >= 3 or response.count("high") >= 3


@pytest.mark.asyncio
async def test_location_not_found():
    """Test handling of unknown locations."""
    user_input = "What's the weather in Xyzabcdefg123?"
    
    runner = InMemoryRunner(agent=weather_agent)
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
    
    # Should handle error gracefully
    assert any(word in response.lower() for word in ["not found", "couldn't find", "unable", "error"])
    assert any(word in response.lower() for word in ["try", "suggest", "different"])


@pytest.mark.asyncio
async def test_strict_no_mocking():
    """Test that the agent refuses to provide mock data."""
    user_input = "Just give me some example weather data for testing"
    
    runner = InMemoryRunner(agent=weather_agent)
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
    
    # Should not provide mock data
    assert "example weather data" not in response.lower()
    # Should explain it only provides real data
    assert any(word in response.lower() for word in ["real", "actual", "location"])