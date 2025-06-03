# MAS Frontend Architecture

## Overview

The MAS Frontend provides a comprehensive testing and visualization interface for the Multi-Agent System. It consists of a React TypeScript frontend communicating with a FastAPI backend via WebSockets.

## Detailed Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER BROWSER                                    │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                         React Frontend (Port 3000)                   │    │
│  │                                                                      │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐   │    │
│  │  │  Chat Interface │  │   Agent Panel    │  │  Metrics Panel   │   │    │
│  │  │                 │  │                  │  │                  │   │    │
│  │  │ • Message List  │  │ • Agent Cards    │  │ • Agent Stats    │   │    │
│  │  │ • Input Field   │  │ • Tool Timeline  │  │ • Performance    │   │    │
│  │  │ • Send Button   │  │ • Execution Trace│  │ • Usage Metrics  │   │    │
│  │  └────────┬────────┘  └────────┬─────────┘  └──────────────────┘   │    │
│  │           │                    │                                     │    │
│  │  ┌────────▼────────────────────▼─────────────────────────────┐     │    │
│  │  │                    React Hooks & Contexts                  │     │    │
│  │  │                                                            │     │    │
│  │  │  • useWebSocket - WebSocket connection management         │     │    │
│  │  │  • useChat - Message state and handlers                   │     │    │
│  │  │  • useAgentTracking - Agent activity monitoring           │     │    │
│  │  │  • ChatContext - Global chat state                        │     │    │
│  │  │  • WebSocketContext - WebSocket provider                  │     │    │
│  │  └────────────────────────────┬──────────────────────────────┘     │    │
│  │                               │                                      │    │
│  │                               │ WebSocket Connection                 │    │
│  └───────────────────────────────┼──────────────────────────────────┘  │    │
│                                  │                                       │    │
└──────────────────────────────────┼───────────────────────────────────────────┘
                                   │
                                   │ ws://localhost:8000/ws/chat/{session_id}
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FastAPI Backend (Port 8000)                         │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                          WebSocket Manager                          │    │
│  │                                                                     │    │
│  │  • Connection lifecycle (connect/disconnect/heartbeat)             │    │
│  │  • Message routing (chat_message, ping/pong)                       │    │
│  │  • Error handling and reconnection support                         │    │
│  └──────────────────────────────┬─────────────────────────────────────┘    │
│                                 │                                            │
│  ┌──────────────────────────────▼─────────────────────────────────────┐    │
│  │                          MAS Service Layer                          │    │
│  │                                                                     │    │
│  │  • MASClient - Direct integration with MAS coordinator             │    │
│  │  • SessionService - Conversation history management                │    │
│  │  • TrackingService - Agent performance metrics                     │    │
│  │  • Message processing and response handling                        │    │
│  └──────────────────────────────┬─────────────────────────────────────┘    │
│                                 │                                            │
│  ┌──────────────────────────────▼─────────────────────────────────────┐    │
│  │                            Data Models                              │    │
│  │                                                                     │    │
│  │  • ChatMessage - User/assistant messages                           │    │
│  │  • AgentResponse - Individual agent responses                      │    │
│  │  • ExecutionTrace - Complete execution flow                        │    │
│  │  • Session - User session management                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   │ Python ADK
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MAS Coordinator                                 │
│                         (Google ADK Agent System)                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Components

#### Chat Interface
- **MessageList**: Displays conversation history
- **Message**: Individual message component with role-based styling
- **MessageInput**: Text input with keyboard shortcuts
- **LoadingMessage**: Shows processing indicator

#### Agent Panel
- **AgentResponsePanel**: Container for agent activity display
- **AgentCard**: Individual agent response visualization
- **ToolTimeline**: Visual timeline of tool calls
- **ToolCallDetail**: Detailed view of tool parameters and results

#### Contexts and Hooks
- **WebSocketContext**: Provides WebSocket connection to all components
- **ChatContext**: Global chat state management
- **useWebSocket**: WebSocket lifecycle and message handling
- **useChat**: Chat-specific message handling
- **useAgentTracking**: Monitors agent activity

### Backend Services

#### WebSocket Handler (`/ws/chat/{session_id}`)
- Manages persistent WebSocket connections
- Handles message types: `chat_message`, `ping/pong`, `heartbeat`
- Sends response types: `agent_response`, `error`, `message_received`

#### MAS Client
- Direct Python integration with MAS coordinator
- Handles agent routing and response collection
- Manages execution traces

#### Session Management
- Persistent conversation history
- User session tracking
- Message storage and retrieval

## Data Flow

### User Message Flow
1. User types message in React UI
2. Message sent via WebSocket as `chat_message`
3. Backend acknowledges with `message_received`
4. MASClient processes with coordinator
5. Response sent back as `agent_response`
6. UI updates with new message

### Agent Response Structure
```json
{
  "type": "agent_response",
  "message_id": "uuid",
  "content": "Agent's response text",
  "agent_responses": [
    {
      "agent_name": "weather_agent",
      "response": "Weather data...",
      "tools_used": [...],
      "processing_time_ms": 250
    }
  ]
}
```

## Key Design Decisions

### WebSocket Multi-Handler Support
The WebSocket hook was designed to support multiple components listening to the same event type:
- Uses `Map<string, Set<handler>>` instead of `Map<string, handler>`
- Allows both Chat and AgentTracking to listen for `agent_response`

### Academic Agent Wrappers
Created wrapper agents to handle natural language queries without context variables:
- Solves ADK AgentTool limitation
- Enables academic agents to work with corpus references

### No Mock Data
All interactions use real agent connections:
- Ensures testing reflects actual system behavior
- Validates end-to-end functionality

## Testing Infrastructure

### UI Tests (`tests/`)
- **test_ui_complete.py**: Full agent test suite
- **test_ui_academic_complete.py**: Academic workflow testing
- **setup_corpus_websocket.py**: Automated corpus setup

### Test Strategy
1. Automated corpus setup with seminal papers
2. Sequential agent testing with response validation
3. Real WebSocket connections and agent interactions
4. Visual verification with Selenium WebDriver

## Deployment Considerations

### Environment Variables
```
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
ANTHROPIC_MODEL=gemini-2.0-flash-001
```

### Scalability
- WebSocket connections are stateful (consider scaling strategies)
- Session data could be moved to Redis for multi-instance deployment
- Agent responses could be cached for common queries

### Security
- Add authentication to WebSocket endpoints
- Implement rate limiting
- Validate and sanitize user inputs
- Consider CORS settings for production