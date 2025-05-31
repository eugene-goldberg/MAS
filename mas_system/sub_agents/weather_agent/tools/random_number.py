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
import os
from typing import Dict, Any, Optional, List, Union
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Cloud Function URL
CLOUD_FUNCTION_URL = "https://us-central1-pickuptruckapp.cloudfunctions.net/generate-random-number"

def get_random_number(
    min_value: int = 1, 
    max_value: int = 100, 
    count: int = 1,
    decimal_places: int = 0
) -> Dict[str, Any]:
    """
    Get random number(s) from the Cloud Function.
    
    Args:
        min_value: Minimum value (inclusive)
        max_value: Maximum value (inclusive)
        count: Number of random numbers to generate (1-100)
        decimal_places: Number of decimal places (0 for integers, up to 10 for floats)
        
    Returns:
        Dictionary containing the random number(s) and metadata
    """
    try:
        # Prepare request payload
        payload = {
            "min": min_value,
            "max": max_value,
            "count": count,
            "decimal_places": decimal_places
        }
        
        # Make request to Cloud Function
        response = requests.post(
            CLOUD_FUNCTION_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # Check response status
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        if data.get("status") == "success":
            logger.info(f"Generated random number(s): {data.get('numbers')}")
            return {
                "success": True,
                "numbers": data.get("numbers"),
                "parameters": data.get("parameters"),
                "timestamp": data.get("timestamp")
            }
        else:
            logger.error(f"Cloud Function error: {data.get('error')}")
            return {
                "success": False,
                "error": data.get("error", "Unknown error")
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to call Cloud Function: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


def get_random_lucky_number() -> Dict[str, Any]:
    """
    Get a random lucky number between 1 and 100.
    This is a convenience function for the weather agent.
    
    Returns:
        Dictionary containing the lucky number
    """
    result = get_random_number(min_value=1, max_value=100, count=1)
    
    if result.get("success"):
        return {
            "lucky_number": result["numbers"],
            "message": f"Your lucky number is {result['numbers']}! 🍀",
            "timestamp": result.get("timestamp")
        }
    else:
        return {
            "error": result.get("error", "Could not generate lucky number"),
            "message": "Sorry, I couldn't generate a lucky number right now."
        }


def get_random_temperature_adjustment() -> Dict[str, Any]:
    """
    Get a random temperature adjustment for fun weather predictions.
    Returns a value between -5 and +5 degrees.
    
    Returns:
        Dictionary containing the temperature adjustment
    """
    result = get_random_number(min_value=-5, max_value=5, count=1)
    
    if result.get("success"):
        adjustment = result["numbers"]
        if adjustment > 0:
            message = f"It might feel {adjustment}°F warmer than expected! ☀️"
        elif adjustment < 0:
            message = f"It might feel {abs(adjustment)}°F cooler than expected! ❄️"
        else:
            message = "The temperature will feel just right! 😊"
            
        return {
            "adjustment": adjustment,
            "message": message,
            "timestamp": result.get("timestamp")
        }
    else:
        return {
            "error": result.get("error", "Could not generate temperature adjustment"),
            "adjustment": 0,
            "message": "Temperature feels as expected."
        }