"""Wrapper functions for weather tools that return ADK-compatible format."""

from mas_system.sub_agents.weather_agent.tools.weather import get_current_weather, get_weather_forecast


def test_get_weather(location: str) -> dict:
    """Wrapper for get_current_weather that returns ADK format."""
    try:
        result = get_current_weather(location)
        if "error" in result:
            return {
                "status": "error",
                "message": result["error"],
                "data": result
            }
        else:
            return {
                "status": "success",
                "message": f"Retrieved weather for {result.get('location', location)}",
                "data": result
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": {}
        }


def test_get_forecast(location: str, days: int = 3) -> dict:
    """Wrapper for get_weather_forecast that returns ADK format."""
    try:
        result = get_weather_forecast(location, days)
        if "error" in result:
            return {
                "status": "error",
                "message": result["error"],
                "data": result
            }
        else:
            return {
                "status": "success",
                "message": f"Retrieved {days}-day forecast for {result.get('location', location)}",
                "data": result
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": {}
        }