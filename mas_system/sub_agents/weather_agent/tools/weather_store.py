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

from google.cloud import firestore
from google.cloud.firestore import SERVER_TIMESTAMP
from typing import Dict, Any, Optional, List
import logging
import os
from datetime import datetime, timedelta

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Firestore client once
_firestore_client = None

def get_firestore_client() -> firestore.Client:
    """
    Get or create a Firestore client instance.
    
    Returns:
        firestore.Client: Firestore client instance
    """
    global _firestore_client
    
    if _firestore_client is None:
        try:
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            _firestore_client = firestore.Client(project=project_id)
            logger.info(f"Firestore client initialized for project: {project_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {str(e)}")
            raise
    
    return _firestore_client


def save_weather_data(weather_data: Dict[str, Any], data_type: str = "current") -> Optional[str]:
    """
    Save weather data to Firestore.
    
    Args:
        weather_data: Weather data from the API
        data_type: Type of data - "current" or "forecast"
    
    Returns:
        Optional[str]: Document ID if successful, None if failed
    """
    try:
        # Skip if there's an error in the data
        if "error" in weather_data:
            logger.warning(f"Skipping save due to error: {weather_data['error']}")
            return None
        
        client = get_firestore_client()
        
        # Create collection name based on data type
        collection_name = "weather_current" if data_type == "current" else "weather_forecasts"
        
        # Prepare document data
        doc_data = {
            "location": weather_data.get("location", "Unknown"),
            "coordinates": weather_data.get("coordinates", {}),
            "timestamp": SERVER_TIMESTAMP,
            "data_type": data_type,
        }
        
        if data_type == "current":
            # Add current weather specific fields
            doc_data.update({
                "temperature": weather_data.get("temperature"),
                "temperature_unit": weather_data.get("unit", "fahrenheit"),
                "description": weather_data.get("description"),
                "humidity": weather_data.get("humidity"),
                "wind_speed": weather_data.get("wind_speed"),
                "feels_like": weather_data.get("feels_like"),
                "precipitation_probability": weather_data.get("precipitation_probability"),
                "api_timestamp": weather_data.get("timestamp")
            })
        else:
            # Add forecast specific fields
            doc_data.update({
                "forecast_days": weather_data.get("days"),
                "temperature_unit": weather_data.get("unit", "fahrenheit"),
                "forecasts": weather_data.get("forecast", [])
            })
        
        # Save to Firestore
        doc_ref = client.collection(collection_name).add(doc_data)
        doc_id = doc_ref[1].id
        
        logger.info(f"Saved {data_type} weather data for {doc_data['location']} with ID: {doc_id}")
        return doc_id
        
    except Exception as e:
        logger.error(f"Failed to save weather data: {str(e)}")
        return None


def get_recent_weather(location: str, hours: int = 24) -> List[Dict[str, Any]]:
    """
    Retrieve recent weather data for a location.
    
    Args:
        location: Location name
        hours: Number of hours to look back (default 24)
    
    Returns:
        List of weather records
    """
    try:
        client = get_firestore_client()
        
        # Calculate time threshold
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Query recent weather data
        query = (
            client.collection("weather_current")
            .where("location", "==", location)
            .where("timestamp", ">=", time_threshold)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(10)
        )
        
        results = []
        for doc in query.stream():
            data = doc.to_dict()
            data["doc_id"] = doc.id
            # Convert timestamp to ISO format
            if "timestamp" in data and data["timestamp"]:
                data["timestamp"] = data["timestamp"].isoformat()
            results.append(data)
        
        logger.info(f"Retrieved {len(results)} weather records for {location}")
        return results
        
    except Exception as e:
        logger.error(f"Failed to retrieve weather data: {str(e)}")
        return []


def get_weather_statistics(location: str, days: int = 7) -> Dict[str, Any]:
    """
    Get weather statistics for a location over the specified days.
    
    Args:
        location: Location name
        days: Number of days to analyze
    
    Returns:
        Dictionary with statistics
    """
    try:
        client = get_firestore_client()
        
        # Calculate time threshold
        time_threshold = datetime.utcnow() - timedelta(days=days)
        
        # Query weather data
        query = (
            client.collection("weather_current")
            .where("location", "==", location)
            .where("timestamp", ">=", time_threshold)
        )
        
        temps = []
        humidity_values = []
        conditions = {}
        
        for doc in query.stream():
            data = doc.to_dict()
            
            if "temperature" in data and data["temperature"] is not None:
                temps.append(data["temperature"])
            
            if "humidity" in data and data["humidity"] is not None:
                humidity_values.append(data["humidity"])
            
            if "description" in data:
                condition = data["description"]
                conditions[condition] = conditions.get(condition, 0) + 1
        
        if not temps:
            return {"error": f"No weather data found for {location} in the last {days} days"}
        
        # Calculate statistics
        stats = {
            "location": location,
            "period_days": days,
            "data_points": len(temps),
            "temperature": {
                "avg": round(sum(temps) / len(temps), 1),
                "min": min(temps),
                "max": max(temps)
            },
            "humidity": {
                "avg": round(sum(humidity_values) / len(humidity_values), 1) if humidity_values else None
            },
            "most_common_condition": max(conditions.items(), key=lambda x: x[1])[0] if conditions else None,
            "conditions_breakdown": conditions
        }
        
        logger.info(f"Calculated statistics for {location} over {days} days")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to calculate weather statistics: {str(e)}")
        return {"error": str(e)}


def cleanup_old_data(days_to_keep: int = 30) -> int:
    """
    Clean up weather data older than specified days.
    
    Args:
        days_to_keep: Number of days of data to keep
    
    Returns:
        Number of documents deleted
    """
    try:
        client = get_firestore_client()
        
        # Calculate cutoff time
        cutoff_time = datetime.utcnow() - timedelta(days=days_to_keep)
        
        deleted_count = 0
        
        # Clean up current weather data
        for collection_name in ["weather_current", "weather_forecasts"]:
            query = client.collection(collection_name).where("timestamp", "<", cutoff_time)
            
            for doc in query.stream():
                doc.reference.delete()
                deleted_count += 1
        
        logger.info(f"Deleted {deleted_count} old weather records")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Failed to cleanup old data: {str(e)}")
        return 0