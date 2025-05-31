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

"""Test cases for the Calculator Sub-Agent."""

import dotenv
import pytest
from mas_system.sub_agents.calculator_agent import calculator_agent
from google.adk.runners import InMemoryRunner
from google.genai import types

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


@pytest.mark.asyncio
async def test_basic_arithmetic():
    """Test basic arithmetic operations."""
    user_input = "What is 25 + 37?"
    
    runner = InMemoryRunner(agent=calculator_agent)
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
    
    # Should contain the correct answer
    assert "62" in response


@pytest.mark.asyncio
async def test_division_by_zero():
    """Test handling of division by zero."""
    user_input = "Calculate 10 divided by 0"
    
    runner = InMemoryRunner(agent=calculator_agent)
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
    assert any(word in response.lower() for word in ["error", "cannot", "zero", "not allowed"])


@pytest.mark.asyncio
async def test_percentage_calculation():
    """Test percentage calculations."""
    user_input = "What is 15% of 200?"
    
    runner = InMemoryRunner(agent=calculator_agent)
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
    
    # Should contain the correct answer
    assert "30" in response


@pytest.mark.asyncio
async def test_temperature_conversion():
    """Test temperature unit conversion."""
    user_input = "Convert 100 degrees Fahrenheit to Celsius"
    
    runner = InMemoryRunner(agent=calculator_agent)
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
    
    # Should contain the correct conversion (37.78°C)
    assert any(val in response for val in ["37.7", "37.8", "38"])
    assert any(symbol in response.lower() for symbol in ["°c", "celsius"])


@pytest.mark.asyncio
async def test_tip_calculation():
    """Test tip calculation functionality."""
    user_input = "Calculate a 20% tip on a $45.75 bill"
    
    runner = InMemoryRunner(agent=calculator_agent)
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
    
    # Should contain tip amount and total
    assert "$" in response
    assert "9.15" in response  # Tip amount
    assert "54.90" in response  # Total amount


@pytest.mark.asyncio
async def test_multi_step_calculation():
    """Test handling of multi-step calculations."""
    user_input = "First add 25 and 15, then multiply the result by 3"
    
    runner = InMemoryRunner(agent=calculator_agent)
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
    
    # Should show intermediate steps and final result
    assert "40" in response  # 25 + 15
    assert "120" in response  # 40 * 3