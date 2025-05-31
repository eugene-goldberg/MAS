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

import requests
from typing import Dict, Any, Tuple
from datetime import datetime
from .weather_store import save_weather_data
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Open-Meteo API (free, no API key required)
# This is a real weather API that provides actual weather data
BASE_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

def get_coordinates(location: str) -> Tuple[float, float, str]:
    """
    Get coordinates for a location using Open-Meteo's geocoding API.
    
    Args:
        location: City name or location
        
    Returns:
        Tuple of (latitude, longitude, formatted_name)
    """
    try:
        response = requests.get(
            GEOCODING_URL,
            params={
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            return (
                result["latitude"],
                result["longitude"],
                f"{result['name']}, {result.get('admin1', '')}, {result['country']}"
            )
        else:
            raise ValueError(f"Location '{location}' not found")
    except Exception as e:
        raise ValueError(f"Failed to geocode location: {str(e)}")


def get_current_weather(location: str) -> Dict[str, Any]:
    """
    Get current weather for a given location using Open-Meteo API.
    
    Args:
        location: City name or location (e.g., "New York", "London", "Tokyo")
        
    Returns:
        Dictionary containing weather information
    """
    try:
        # Get coordinates for the location
        lat, lon, formatted_location = get_coordinates(location)
        
        # Fetch weather data
        response = requests.get(
            BASE_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "hourly": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,weather_code",
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "timezone": "auto"
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        current = data["current_weather"]
        
        # Get current hour's detailed data
        current_time = datetime.fromisoformat(current["time"])
        hourly_data = data["hourly"]
        current_hour_index = 0
        
        # Map weather codes to descriptions
        weather_descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        
        weather_code = current.get("weathercode", 0)
        description = weather_descriptions.get(weather_code, "Unknown")
        
        weather_result = {
            "location": formatted_location,
            "temperature": round(current["temperature"]),
            "unit": "fahrenheit",
            "description": description,
            "humidity": hourly_data["relative_humidity_2m"][current_hour_index],
            "wind_speed": round(current["windspeed"]),
            "feels_like": round(hourly_data["apparent_temperature"][current_hour_index]),
            "precipitation_probability": hourly_data["precipitation_probability"][current_hour_index],
            "timestamp": current["time"],
            "coordinates": {"latitude": lat, "longitude": lon}
        }
        
        # Save to Firestore
        try:
            doc_id = save_weather_data(weather_result, "current")
            if doc_id:
                logger.info(f"Saved current weather data to Firestore: {doc_id}")
        except Exception as e:
            logger.error(f"Failed to save to Firestore: {e}")
        
        return weather_result
    except Exception as e:
        return {
            "error": f"Failed to fetch weather data: {str(e)}",
            "location": location
        }


def get_weather_forecast(location: str, days: int = 5) -> Dict[str, Any]:
    """
    Get weather forecast for a given location using Open-Meteo API.
    
    Args:
        location: City name or location
        days: Number of days to forecast (1-7)
        
    Returns:
        Dictionary containing forecast information
    """
    try:
        # Limit days to 7 (API maximum)
        days = min(days, 7)
        
        # Get coordinates for the location
        lat, lon, formatted_location = get_coordinates(location)
        
        # Fetch forecast data
        response = requests.get(
            BASE_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
                "temperature_unit": "fahrenheit",
                "timezone": "auto",
                "forecast_days": days
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        # Map weather codes to descriptions
        weather_descriptions = {
            0: "Clear sky",
            1: "Mainly clear", 
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        
        # Format forecast data
        daily_data = data["daily"]
        forecast_data = []
        
        for i in range(len(daily_data["time"])):
            weather_code = daily_data["weather_code"][i]
            description = weather_descriptions.get(weather_code, "Unknown")
            
            forecast_data.append({
                "date": daily_data["time"][i],
                "temperature_high": round(daily_data["temperature_2m_max"][i]),
                "temperature_low": round(daily_data["temperature_2m_min"][i]),
                "description": description,
                "precipitation_chance": daily_data["precipitation_probability_max"][i],
                "precipitation_amount": daily_data["precipitation_sum"][i]
            })
        
        forecast_result = {
            "location": formatted_location,
            "forecast": forecast_data,
            "days": len(forecast_data),
            "unit": "fahrenheit",
            "coordinates": {"latitude": lat, "longitude": lon}
        }
        
        # Save to Firestore
        try:
            doc_id = save_weather_data(forecast_result, "forecast")
            if doc_id:
                logger.info(f"Saved forecast data to Firestore: {doc_id}")
        except Exception as e:
            logger.error(f"Failed to save to Firestore: {e}")
        
        return forecast_result
    except Exception as e:
        return {
            "error": f"Failed to fetch forecast data: {str(e)}",
            "location": location
        }