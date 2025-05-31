# Multi-Agent System (MAS)

## Overview

A sophisticated multi-agent system that uses an intelligent coordinator to route user requests to specialized sub-agents. The system demonstrates intent-based routing where the coordinator evaluates natural language requests and delegates them to the appropriate expert agent for handling.

The system includes:
1. **Coordinator Agent**: Analyzes user intent and routes requests
2. **Weather Agent**: Provides real-time weather information from Open-Meteo API
3. **Calculator Agent**: Performs mathematical operations and unit conversions

This architecture showcases how to build scalable multi-agent systems where specialized agents handle domain-specific tasks while a coordinator manages the overall interaction flow.

## Agent Details

| Feature | Description |
| --- | --- |
| **Interaction Type** | Conversational with Intent Routing |
| **Complexity** | Medium |
| **Agent Type** | Multi Agent with Coordinator Pattern |
| **Components** | LlmAgent (coordinator), Agent (sub-agents), External APIs |
| **Sub-Agents** | Weather (Open-Meteo API), Calculator (Mathematical Operations) |

### System Architecture

```
User Request
     ↓
Coordinator Agent (LlmAgent)
     ├─ Evaluates Intent
     └─ Routes to:
         ├─ Weather Agent
         │   ├─ Current Weather
         │   ├─ Forecasts
         │   └─ Cloud Functions
         │
         └─ Calculator Agent
             ├─ Basic Math
             ├─ Unit Conversions
             └─ Complex Calculations
```

## Sub-Agent Capabilities

### Weather Agent
- **Current Weather**: Real-time conditions for any location
- **Forecasts**: Up to 7-day weather predictions
- **Data Points**: Temperature, humidity, wind, precipitation
- **Cloud Functions**: Lucky numbers and temperature adjustments
- **Data Storage**: Automatic saving to Cloud Firestore

### Calculator Agent
- **Basic Operations**: Add, subtract, multiply, divide
- **Advanced Math**: Powers, square roots, percentages
- **Unit Conversions**: Temperature, distance, weight
- **Practical Tools**: Tip calculator, BMI, compound interest

## Setup and Installation

### Prerequisites

1. **Python 3.11+**
2. **Poetry** for dependency management
   ```bash
   pip install poetry
   ```
3. **Google Cloud Project** with:
   - Vertex AI API enabled
   - Cloud Firestore in Native mode
   - Cloud Functions (optional)
   - Storage bucket for deployment
4. **gcloud CLI** installed and authenticated

### Installation Steps

1. **Clone and Navigate**
   ```bash
   cd /path/to/MAS
   ```

2. **Install Dependencies**
   ```bash
   poetry install
   ```

3. **Configure Environment**
   
   Copy `.env.example` to `.env` and update:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket-name
   RANDOM_NUMBER_FUNCTION_URL=your-cloud-function-url
   ```

4. **Authenticate**
   ```bash
   gcloud auth application-default login
   ```

## Deployment

### Build and Deploy

1. **Build the Package**
   ```bash
   poetry build --format=wheel --output=deployment
   ```

2. **Deploy to Vertex AI**
   ```bash
   cd deployment
   python3 deploy.py
   ```

   The deployment will return an agent ID for future use.

### Managing Deployments

- **List Agents**: `python3 delete_agent.py --list`
- **Delete Agent**: `python3 delete_agent.py --delete <agent_id>`

## Testing

### Run Tests

```bash
# Unit tests
pytest tests/

# Integration tests
python3 tests/test_integration.py

# Test specific sub-agents
python3 tests/test_weather_subagent.py
python3 tests/test_calculator_subagent.py
```

### Example Interactions

**Weather Query:**
```
User: "What's the weather in San Francisco?"
Coordinator: Routes to Weather Agent
Weather Agent: "The current weather in San Francisco, California, United States is 65°F with partly cloudy skies..."
```

**Calculator Query:**
```
User: "Calculate 20% tip on $75.50"
Coordinator: Routes to Calculator Agent
Calculator Agent: "Calculating 20% tip on $75.50: The tip amount is $15.10, making your total $90.60"
```

**Unit Conversion:**
```
User: "Convert 32 degrees Fahrenheit to Celsius"
Coordinator: Routes to Calculator Agent (handles conversions)
Calculator Agent: "32°F equals 0°C"
```

## Cloud Integration

### Firestore Integration
Weather data is automatically saved to Firestore:
- Collection: `weather_current` (current conditions)
- Collection: `weather_forecasts` (forecast data)

### Cloud Functions
Optional integration for random number generation:
- Deploy function from `cloud_functions/random_number_generator/`
- Update `RANDOM_NUMBER_FUNCTION_URL` in `.env`

## Architecture Notes

### Coordinator Design
- Uses `LlmAgent` for natural language intent evaluation
- Implements zero-shot classification based on keywords and context
- Routes complete user requests without modification

### Sub-Agent Pattern
- Sub-agents use simple `Agent` class (not `LlmAgent`)
- Each maintains domain-specific tools and prompts
- Complete separation of concerns

### State Management
- Coordinator doesn't maintain conversation state
- Each sub-agent handles its own context
- Clean request/response pattern

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all paths updated from `academic_research` to `mas_system`
   - Check `__init__.py` files are properly configured

2. **Weather API Failures**
   - Open-Meteo is free and doesn't require API keys
   - Check location names are spelled correctly
   - Try adding state/country for clarity

3. **Deployment Issues**
   - Verify all dependencies in `pyproject.toml`
   - Check Google Cloud permissions
   - Ensure storage bucket exists

## Future Enhancements

- Add more specialized sub-agents
- Implement conversation memory
- Add agent selection confidence scores
- Support multi-agent collaboration
- Implement fallback handling

## License

Copyright 2025 Google LLC. Licensed under the Apache License, Version 2.0.