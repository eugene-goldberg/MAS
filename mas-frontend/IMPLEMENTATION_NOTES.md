# MAS Frontend Implementation Notes

## Overview
This document describes the implementation of a FastAPI + React.js frontend for testing and visualizing the MAS (Multi-Agent System) project.

## Architecture

### Backend (FastAPI)
- **WebSocket Communication**: Real-time bidirectional communication between frontend and MAS
- **Session Management**: Tracks user sessions and conversation history
- **MAS Integration**: Direct integration with the MAS coordinator agent
- **No Mocks**: All connections are real - no mock data or simulated responses

### Frontend (React + TypeScript)
- **Material-UI**: Professional UI components
- **WebSocket Hook**: Custom React hook for WebSocket management
- **Real-time Updates**: Live display of agent responses and execution traces
- **Agent Activity Panel**: Visual representation of agent interactions

## Key Implementation Challenges & Solutions

### 1. WebSocket Handler Registration Issue

**Problem**: Multiple components registering handlers for the same WebSocket event type were overwriting each other.

**Root Cause**: The WebSocket hook was using a simple Map that only allowed one handler per event type.

**Solution**: Modified the WebSocket hook to support multiple handlers per event type:
```typescript
// Before: Map<string, handler>
const messageHandlers = useRef<Map<string, (data: any) => void>>(new Map());

// After: Map<string, Set<handler>>
const messageHandlers = useRef<Map<string, Set<(data: any) => void>>>(new Map());
```

This allowed both the chat component and agent tracking component to listen for `agent_response` events.

### 2. Academic Agents Context Variable Error

**Problem**: Academic agents failing with "Context variable not found: `seminal_paper`" errors.

**Root Cause**: 
- Academic agents expected context variables in their prompts (e.g., `{seminal_paper}`)
- The ADK's `AgentTool` wrapper doesn't support passing context variables

**Solution**: Created wrapper agents that handle natural language without requiring context variables:
```python
# mas_system/sub_agents/academic_wrapper.py
academic_websearch_wrapper = LlmAgent(
    name="academic_websearch_wrapper",
    instruction="Extract paper info from query and search for citations..."
)
```

### 3. TypeScript Compilation Errors

**Problem**: MetricsPanel component had TypeScript errors after removing mock data.

**Solution**: Added proper type definitions:
```typescript
interface AgentStats {
  avgResponseTime: number;
  totalCalls: number;
  toolUsage: Record<string, number>;
}

const agentStats: Record<string, AgentStats> = {};
```

### 4. React StrictMode Double Mounting

**Problem**: WebSocket connections being created twice in development due to React's StrictMode.

**Solution**: Added proper cleanup and connection state management in the WebSocket hook to handle component unmounting gracefully.

## Testing Strategy

### 1. Corpus Setup
Created automated scripts to set up test data:
- `setup_corpus_websocket.py`: Creates a corpus with the Transformer paper
- Test documents stored in `tests/transformer_paper.txt`

### 2. UI Testing Suite
Comprehensive Selenium-based tests:
- `test_ui_complete.py`: Tests all 5 agents with proper response validation
- `test_ui_academic_complete.py`: Focused testing of academic workflow
- Tests verify real end-to-end functionality without mocks

### 3. Test Workflow
1. Setup: Create corpus with seminal paper
2. Greeting: Test greeter agent
3. Weather: Test weather agent  
4. RAG: Query corpus for paper information
5. Academic Search: Find papers citing the seminal work
6. Research Directions: Get future research suggestions

## Academic Agents Workflow

The academic agents now support a natural workflow:

1. **Query Corpus**: "Tell me about the Transformer paper in the corpus"
2. **Find Citations**: "Search for recent papers citing this work"  
3. **Research Directions**: "Suggest future research based on this paper"

No need to manually set context variables - the wrapper agents extract the necessary information from natural language queries.

## Key Files

### Backend
- `app/api/routes/websocket.py`: WebSocket endpoint implementation
- `app/core/mas_client.py`: MAS system integration
- `app/services/mas_service.py`: Business logic for MAS interactions

### Frontend  
- `src/hooks/useWebSocket.ts`: WebSocket connection management
- `src/hooks/useChat.ts`: Chat state and message handling
- `src/components/Chat/`: Chat UI components
- `src/components/AgentPanel/`: Agent activity visualization

### MAS System
- `mas_system/agent.py`: Coordinator configuration
- `mas_system/prompt.py`: Coordinator routing instructions
- `mas_system/sub_agents/academic_wrapper.py`: Academic agent wrappers

## Deployment

### Local Development
```bash
# Backend
cd mas-frontend/backend
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend
cd mas-frontend/frontend
npm start

# Run tests
cd mas-frontend/tests
python test_ui_complete.py
```

### Environment Variables
```
GOOGLE_CLOUD_PROJECT=your-project
GOOGLE_CLOUD_LOCATION=us-central1
ANTHROPIC_MODEL=gemini-2.0-flash-001
```

## Lessons Learned

1. **AgentTool Limitations**: Cannot pass context variables to wrapped agents
2. **WebSocket Complexity**: Need to handle multiple listeners for same event types
3. **Type Safety**: Proper TypeScript types prevent runtime errors
4. **Real Testing**: No mocks ensures actual functionality works end-to-end
5. **Wrapper Pattern**: Useful for adapting agents with specific requirements

## Future Enhancements

1. **Streaming Responses**: Show agent responses as they're generated
2. **File Upload**: Allow users to upload PDFs directly to corpus
3. **Visualization**: Better visual representation of agent interactions
4. **Export**: Allow exporting conversation history
5. **Multi-corpus**: Support switching between different document collections