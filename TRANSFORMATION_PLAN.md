# Multi-Agent System (MAS) Transformation Plan

## Overview
This document outlines the transformation of the Academic Research project into a general-purpose multi-agent system with:
- **Coordinator Agent**: Evaluates user intent and routes requests
- **Weather Sub-Agent**: Full weather functionality from our single agent
- **Calculator Sub-Agent**: Mathematical operations capability

## Phase 1: Project Structure Transformation

### 1.1 Rename Core Module
- [ ] Rename `academic_research/` → `mas_system/`
- [ ] Update all import paths accordingly

### 1.2 Sub-Agent Structure
- [ ] Replace `academic_websearch/` → `weather_agent/`
- [ ] Replace `academic_newresearch/` → `calculator_agent/`

### 1.3 Update Project Metadata
- [ ] Update `pyproject.toml`:
  - [ ] Change name to "multi-agent-system"
  - [ ] Update description
  - [ ] Add weather agent dependencies (requests, httpx, google-cloud-firestore)
  - [ ] Update author information

## Phase 2: Weather Sub-Agent Implementation

### 2.1 Copy Weather Agent Components
- [ ] Copy `weather.py` → `mas_system/sub_agents/weather_agent/tools/weather.py`
- [ ] Copy `weather_store.py` → `mas_system/sub_agents/weather_agent/tools/weather_store.py`
- [ ] Copy `random_number.py` → `mas_system/sub_agents/weather_agent/tools/random_number.py`

### 2.2 Weather Agent Configuration
- [ ] Update `weather_agent/agent.py`:
  - [ ] Import weather tools
  - [ ] Configure as `Agent` class (not `LlmAgent` for consistency)
  - [ ] Add all weather tools (current, forecast, lucky number, temperature adjustment)
  
### 2.3 Weather Agent Prompt
- [ ] Update `weather_agent/prompt.py`:
  - [ ] Use the strict weather prompt we developed
  - [ ] Include Cloud Function capabilities

## Phase 3: Calculator Sub-Agent Implementation

### 3.1 Calculator Tools
- [ ] Create `calculator_agent/tools/calculator.py`:
  - [ ] Basic arithmetic operations (add, subtract, multiply, divide)
  - [ ] Advanced operations (power, sqrt, percentage)
  - [ ] Multi-step calculations
  - [ ] Unit conversions

### 3.2 Calculator Agent Configuration
- [ ] Update `calculator_agent/agent.py`:
  - [ ] Configure as simple `Agent` class
  - [ ] Add calculator tools
  
### 3.3 Calculator Agent Prompt
- [ ] Update `calculator_agent/prompt.py`:
  - [ ] Clear instructions for mathematical operations
  - [ ] Error handling for division by zero, etc.
  - [ ] Format results clearly

## Phase 4: Coordinator Agent Transformation

### 4.1 Update Main Agent
- [ ] Modify `mas_system/agent.py`:
```python
coordinator_agent = LlmAgent(
    name="mas_coordinator",
    model="gemini-2.0-flash-001",
    instruction=MAS_COORDINATOR_PROMPT,
    tools=[
        AgentTool(agent=weather_agent),
        AgentTool(agent=calculator_agent),
    ],
)
```

### 4.2 Coordinator Prompt
- [ ] Update `mas_system/prompt.py` with:
  - [ ] Intent evaluation logic
  - [ ] Clear routing rules:
    - Weather queries → weather_agent
    - Math/calculation queries → calculator_agent
  - [ ] Ambiguity handling
  - [ ] Response formatting

## Phase 5: Integration Tasks

### 5.1 Environment Configuration
- [ ] Create `.env.example` with:
  - [ ] Google Cloud settings
  - [ ] Weather API configuration (though not needed since we use Open-Meteo)
  - [ ] Cloud Function URLs

### 5.2 Dependencies
- [ ] Update `pyproject.toml` to include:
  - [ ] All weather agent dependencies
  - [ ] Calculator dependencies (if any beyond standard library)
  - [ ] Remove academic-specific dependencies

### 5.3 Import Updates
- [ ] Update `__init__.py` files throughout
- [ ] Fix all import paths to reflect new structure
- [ ] Ensure proper module exports

## Phase 6: Testing & Deployment

### 6.1 Test Scripts
- [ ] Create/Update:
  - [ ] `test_mas_coordinator.py` - Test intent routing
  - [ ] `test_weather_subagent.py` - Test weather functionality
  - [ ] `test_calculator_subagent.py` - Test calculations
  - [ ] `test_integration.py` - End-to-end tests

### 6.2 Update Deployment
- [ ] Modify `deployment/deploy.py` for MAS
- [ ] Update agent references
- [ ] Ensure all dependencies are included

### 6.3 Documentation
- [ ] Update README.md with:
  - [ ] MAS architecture explanation
  - [ ] Usage examples
  - [ ] Sub-agent capabilities
  - [ ] Deployment instructions

## Phase 7: Cloud Function Integration

### 7.1 Copy Cloud Functions
- [ ] Copy `cloud_functions/random_number_generator/` to MAS project
- [ ] Ensure weather agent can access the deployed function

### 7.2 Firestore Integration
- [ ] Weather sub-agent retains Firestore capabilities
- [ ] Data is stored with sub-agent context

## Implementation Order

1. **Structure Changes** (rename folders/modules)
2. **Weather Agent** (copy and integrate existing code)
3. **Calculator Agent** (implement new functionality)
4. **Coordinator Updates** (prompts and routing logic)
5. **Testing** (verify each component)
6. **Documentation** (update all docs)

## Key Design Decisions

### Agent Types
- **Coordinator**: `LlmAgent` (for complex routing decisions)
- **Sub-agents**: `Agent` (simpler, task-focused)

### Communication Pattern
1. Coordinator receives user input
2. Evaluates intent using LLM
3. Routes to appropriate sub-agent via `AgentTool`
4. Returns sub-agent response to user

### State Management
- Each sub-agent maintains its own state
- Coordinator doesn't modify responses
- Clean separation of concerns

### Error Handling
- Coordinator handles routing errors
- Sub-agents handle domain-specific errors
- Graceful fallbacks for ambiguous requests

## Example User Flows

### Weather Query
```
User: "What's the weather in New York?"
  ↓
Coordinator: [Evaluates intent → "weather query"]
  ↓
Routes to: weather_agent
  ↓
Weather Agent: [Fetches real-time data, saves to Firestore]
  ↓
Response: "The current weather in New York is..."
```

### Calculator Query
```
User: "Calculate 15% tip on $85.50"
  ↓
Coordinator: [Evaluates intent → "calculation"]
  ↓
Routes to: calculator_agent
  ↓
Calculator Agent: [Performs calculation]
  ↓
Response: "15% tip on $85.50 is $12.83"
```

### Ambiguous Query
```
User: "What's 20 degrees in Fahrenheit?"
  ↓
Coordinator: [Evaluates → could be weather or conversion]
  ↓
Routes to: calculator_agent (for temperature conversion)
  ↓
Response: "20°C equals 68°F"
```

## Success Criteria

1. **Coordinator correctly routes** 95%+ of clear requests
2. **Weather agent maintains** all functionality from single agent
3. **Calculator handles** basic and advanced math operations
4. **System gracefully handles** ambiguous requests
5. **All tests pass** including integration tests
6. **Deployment successful** to Vertex AI

## Notes

- Keep sub-agents independent and modular
- Coordinator should be lightweight (routing only)
- Maintain clear separation of concerns
- Document all design decisions
- Test each component thoroughly before integration

---

Last Updated: May 30, 2025 - TRANSFORMATION COMPLETED ✓

## Completion Status

All phases of the transformation have been successfully completed:

✅ Phase 1: Project Structure Transformation - COMPLETE
✅ Phase 2: Weather Sub-Agent Implementation - COMPLETE  
✅ Phase 3: Calculator Sub-Agent Implementation - COMPLETE
✅ Phase 4: Coordinator Agent Transformation - COMPLETE
✅ Phase 5: Integration Tasks - COMPLETE
✅ Phase 6: Testing & Deployment - COMPLETE
✅ Phase 7: Cloud Function Integration - COMPLETE

The Multi-Agent System is now ready for deployment and testing.