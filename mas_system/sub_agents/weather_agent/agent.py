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

"""Weather agent for retrieving weather information and forecasts."""

from google.adk import Agent
from google.adk.tools import FunctionTool

from . import prompt
from .tools import weather, random_number

MODEL = "gemini-2.0-flash-001"


weather_agent = Agent(
    model=MODEL,
    name="weather_agent",
    description="Handles all weather-related queries including current conditions, forecasts, and weather data for any location",
    instruction=prompt.WEATHER_AGENT_PROMPT,
    tools=[
        FunctionTool(func=weather.get_current_weather),
        FunctionTool(func=weather.get_weather_forecast),
        FunctionTool(func=random_number.get_random_lucky_number),
        FunctionTool(func=random_number.get_random_temperature_adjustment),
    ],
)