# MAS Testing Frontend - FastAPI + React.js Plan

## Overview

Create a comprehensive testing interface for the Multi-Agent System (MAS) that provides real-time visibility into agent interactions, tool usage, and response generation.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React.js Frontend                       │
├─────────────────────────────────────────────────────────────┤
│  • Chat Interface (left panel)                              │
│  • Agent Response Viewer (right panel)                      │
│  • Tool Usage Timeline                                      │
│  • Real-time updates via WebSocket                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ WebSocket + REST API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                         │
├─────────────────────────────────────────────────────────────┤
│  • REST endpoints for chat                                  │
│  • WebSocket for real-time updates                          │
│  • Agent execution tracking                                 │
│  • Tool call interception                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Integrates with
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    MAS Coordinator                          │
│          (Existing Multi-Agent System)                      │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: Backend Infrastructure

#### 1.1 Project Structure
```
mas-frontend/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── chat.py     # Chat endpoints
│   │   │   │   ├── agents.py   # Agent info endpoints
│   │   │   │   └── websocket.py # WebSocket handler
│   │   │   └── dependencies.py
│   │   ├── core/
│   │   │   ├── config.py       # Configuration
│   │   │   ├── mas_client.py   # MAS integration
│   │   │   └── tracking.py     # Agent/tool tracking
│   │   ├── models/
│   │   │   ├── chat.py         # Pydantic models
│   │   │   ├── agent.py
│   │   │   └── tracking.py
│   │   └── services/
│   │       ├── mas_service.py  # MAS interaction logic
│   │       └── tracking_service.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

#### 1.2 FastAPI Backend Components

##### Main Application (main.py)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, agents, websocket
from app.core.config import settings

app = FastAPI(title="MAS Testing Interface")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
```

##### Data Models (models/)
```python
# models/chat.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    id: str
    content: str
    role: str  # "user" or "assistant"
    timestamp: datetime
    agent_responses: Optional[List['AgentResponse']] = []

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

# models/agent.py
class ToolCall(BaseModel):
    tool_name: str
    tool_type: str
    parameters: dict
    result: dict
    duration_ms: float
    timestamp: datetime

class AgentResponse(BaseModel):
    agent_name: str
    agent_type: str
    response: str
    tools_used: List[ToolCall]
    processing_time_ms: float
    timestamp: datetime

# models/tracking.py
class ExecutionTrace(BaseModel):
    session_id: str
    request_id: str
    coordinator_response: str
    agent_sequence: List[str]
    total_time_ms: float
    agent_responses: List[AgentResponse]
```

##### MAS Integration Service
```python
# services/mas_service.py
import asyncio
from typing import Dict, List, Tuple
import time
from app.models.agent import AgentResponse, ToolCall
from app.core.tracking import TrackingInterceptor

class MASService:
    def __init__(self):
        self.tracking_interceptor = TrackingInterceptor()
        
    async def process_message(
        self, 
        message: str, 
        session_id: str,
        websocket_callback=None
    ) -> Tuple[str, List[AgentResponse]]:
        """
        Process message through MAS with tracking
        """
        # Start tracking
        request_id = self.tracking_interceptor.start_request(session_id)
        
        # Create wrapped MAS coordinator with tracking
        tracked_coordinator = self.tracking_interceptor.wrap_agent(
            mas_coordinator,
            websocket_callback
        )
        
        # Execute request
        start_time = time.time()
        response = await tracked_coordinator.send(message)
        total_time = (time.time() - start_time) * 1000
        
        # Get tracking data
        agent_responses = self.tracking_interceptor.get_responses(request_id)
        
        return response, agent_responses
```

##### Tracking Interceptor
```python
# core/tracking.py
from typing import Dict, List, Callable
import functools
import time

class TrackingInterceptor:
    """Intercepts and tracks agent/tool calls"""
    
    def __init__(self):
        self.active_requests: Dict[str, List[AgentResponse]] = {}
        
    def wrap_agent(self, agent, websocket_callback=None):
        """Wrap agent to track tool calls"""
        # Implementation to intercept tool calls
        # and track which agent is responding
        
    def wrap_tool(self, tool_func, agent_name: str, websocket_callback=None):
        """Wrap tool function to track execution"""
        @functools.wraps(tool_func)
        async def wrapped(*args, **kwargs):
            start_time = time.time()
            
            # Notify via WebSocket that tool is being called
            if websocket_callback:
                await websocket_callback({
                    "type": "tool_start",
                    "agent": agent_name,
                    "tool": tool_func.__name__,
                    "parameters": kwargs
                })
            
            # Execute tool
            result = await tool_func(*args, **kwargs)
            
            duration = (time.time() - start_time) * 1000
            
            # Record tool call
            tool_call = ToolCall(
                tool_name=tool_func.__name__,
                tool_type=type(tool_func).__name__,
                parameters=kwargs,
                result=result,
                duration_ms=duration,
                timestamp=datetime.now()
            )
            
            # Notify completion
            if websocket_callback:
                await websocket_callback({
                    "type": "tool_complete",
                    "agent": agent_name,
                    "tool": tool_func.__name__,
                    "duration_ms": duration,
                    "result": result
                })
            
            return result
        
        return wrapped
```

##### WebSocket Handler
```python
# api/routes/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.mas_service import MASService
import json

router = APIRouter()
mas_service = MASService()

@router.websocket("/chat/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process with MAS
            response, agent_responses = await mas_service.process_message(
                message_data["message"],
                session_id,
                websocket_callback=lambda update: websocket.send_json(update)
            )
            
            # Send final response
            await websocket.send_json({
                "type": "complete",
                "response": response,
                "agent_responses": [r.dict() for r in agent_responses]
            })
            
    except WebSocketDisconnect:
        print(f"Client {session_id} disconnected")
```

### Phase 2: React Frontend

#### 2.1 Component Architecture
```
src/
├── components/
│   ├── Chat/
│   │   ├── ChatInterface.tsx      # Main chat UI
│   │   ├── MessageList.tsx        # Message history
│   │   ├── MessageInput.tsx       # Input component
│   │   └── Message.tsx            # Individual message
│   ├── AgentPanel/
│   │   ├── AgentResponsePanel.tsx # Agent responses container
│   │   ├── AgentCard.tsx          # Individual agent display
│   │   ├── ToolTimeline.tsx       # Tool execution timeline
│   │   └── ToolCallDetail.tsx     # Tool call details
│   ├── Layout/
│   │   ├── Header.tsx
│   │   └── SplitLayout.tsx        # Split panel layout
│   └── Common/
│       ├── LoadingSpinner.tsx
│       └── ErrorBoundary.tsx
├── hooks/
│   ├── useWebSocket.ts            # WebSocket connection
│   ├── useChat.ts                 # Chat state management
│   └── useAgentTracking.ts        # Agent tracking state
├── services/
│   ├── api.ts                     # REST API calls
│   └── websocket.ts               # WebSocket service
├── types/
│   ├── chat.ts
│   └── agent.ts
└── App.tsx
```

#### 2.2 Key React Components

##### Main App Layout
```tsx
// App.tsx
import React from 'react';
import { ChatInterface } from './components/Chat/ChatInterface';
import { AgentResponsePanel } from './components/AgentPanel/AgentResponsePanel';
import { SplitLayout } from './components/Layout/SplitLayout';
import { ChatProvider } from './contexts/ChatContext';
import { AgentTrackingProvider } from './contexts/AgentTrackingContext';

function App() {
  return (
    <ChatProvider>
      <AgentTrackingProvider>
        <SplitLayout
          left={<ChatInterface />}
          right={<AgentResponsePanel />}
        />
      </AgentTrackingProvider>
    </ChatProvider>
  );
}
```

##### Chat Interface Component
```tsx
// components/Chat/ChatInterface.tsx
import React, { useState } from 'react';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { useChat } from '../../hooks/useChat';
import { useWebSocket } from '../../hooks/useWebSocket';

export const ChatInterface: React.FC = () => {
  const { messages, addMessage } = useChat();
  const { sendMessage, isConnected } = useWebSocket();
  
  const handleSendMessage = async (content: string) => {
    // Add user message
    addMessage({
      role: 'user',
      content,
      timestamp: new Date()
    });
    
    // Send to backend
    await sendMessage(content);
  };
  
  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>MAS Chat</h2>
        <ConnectionStatus connected={isConnected} />
      </div>
      <MessageList messages={messages} />
      <MessageInput onSend={handleSendMessage} />
    </div>
  );
};
```

##### Agent Response Panel
```tsx
// components/AgentPanel/AgentResponsePanel.tsx
import React from 'react';
import { AgentCard } from './AgentCard';
import { ToolTimeline } from './ToolTimeline';
import { useAgentTracking } from '../../hooks/useAgentTracking';

export const AgentResponsePanel: React.FC = () => {
  const { currentExecution, agentResponses } = useAgentTracking();
  
  return (
    <div className="agent-panel">
      <div className="panel-header">
        <h2>Agent Activity</h2>
        {currentExecution && (
          <ExecutionStatus status={currentExecution.status} />
        )}
      </div>
      
      <div className="timeline-section">
        <h3>Execution Timeline</h3>
        <ToolTimeline execution={currentExecution} />
      </div>
      
      <div className="agents-section">
        <h3>Agent Responses</h3>
        {agentResponses.map((response, idx) => (
          <AgentCard key={idx} response={response} />
        ))}
      </div>
    </div>
  );
};
```

##### Agent Card Component
```tsx
// components/AgentPanel/AgentCard.tsx
import React, { useState } from 'react';
import { AgentResponse } from '../../types/agent';
import { ToolCallDetail } from './ToolCallDetail';

export const AgentCard: React.FC<{ response: AgentResponse }> = ({ response }) => {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <div className={`agent-card ${response.agent_type}`}>
      <div className="agent-header" onClick={() => setExpanded(!expanded)}>
        <div className="agent-info">
          <span className="agent-icon">{getAgentIcon(response.agent_type)}</span>
          <h4>{response.agent_name}</h4>
        </div>
        <div className="agent-stats">
          <span className="tool-count">{response.tools_used.length} tools</span>
          <span className="time">{response.processing_time_ms}ms</span>
        </div>
      </div>
      
      {expanded && (
        <div className="agent-details">
          <div className="response-text">
            {response.response}
          </div>
          
          <div className="tools-section">
            <h5>Tools Used:</h5>
            {response.tools_used.map((tool, idx) => (
              <ToolCallDetail key={idx} toolCall={tool} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
```

##### Tool Timeline Component
```tsx
// components/AgentPanel/ToolTimeline.tsx
import React from 'react';
import { ExecutionTrace } from '../../types/agent';

export const ToolTimeline: React.FC<{ execution: ExecutionTrace }> = ({ execution }) => {
  if (!execution) return null;
  
  const timelineItems = execution.agent_responses.flatMap(agent =>
    agent.tools_used.map(tool => ({
      agent: agent.agent_name,
      tool: tool.tool_name,
      timestamp: tool.timestamp,
      duration: tool.duration_ms
    }))
  ).sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  
  return (
    <div className="tool-timeline">
      {timelineItems.map((item, idx) => (
        <div key={idx} className="timeline-item">
          <div className="timeline-marker" />
          <div className="timeline-content">
            <div className="timeline-header">
              <span className="agent-name">{item.agent}</span>
              <span className="tool-name">{item.tool}</span>
            </div>
            <div className="timeline-meta">
              <span className="duration">{item.duration}ms</span>
              <span className="time">{formatTime(item.timestamp)}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
```

#### 2.3 WebSocket Hook
```typescript
// hooks/useWebSocket.ts
import { useEffect, useRef, useState, useCallback } from 'react';
import { useAgentTracking } from './useAgentTracking';

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const { updateExecution, addToolCall } = useAgentTracking();
  
  useEffect(() => {
    // Connect to WebSocket
    const sessionId = generateSessionId();
    ws.current = new WebSocket(`ws://localhost:8000/ws/chat/${sessionId}`);
    
    ws.current.onopen = () => setIsConnected(true);
    ws.current.onclose = () => setIsConnected(false);
    
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'tool_start':
          addToolCall({
            agent: data.agent,
            tool: data.tool,
            status: 'running',
            startTime: new Date()
          });
          break;
          
        case 'tool_complete':
          updateToolCall({
            agent: data.agent,
            tool: data.tool,
            status: 'complete',
            duration: data.duration_ms,
            result: data.result
          });
          break;
          
        case 'complete':
          updateExecution({
            response: data.response,
            agentResponses: data.agent_responses
          });
          break;
      }
    };
    
    return () => {
      ws.current?.close();
    };
  }, []);
  
  const sendMessage = useCallback((message: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ message }));
    }
  }, []);
  
  return { sendMessage, isConnected };
};
```

### Phase 3: Styling and UI/UX

#### 3.1 UI Design Principles
- **Split Panel Layout**: 60/40 split between chat and agent panel
- **Real-time Updates**: Smooth animations for tool execution
- **Color Coding**: Different colors for each agent type
- **Responsive Design**: Works on desktop and tablet

#### 3.2 CSS Structure
```scss
// styles/main.scss
.app-container {
  display: flex;
  height: 100vh;
  
  .chat-panel {
    flex: 3;
    display: flex;
    flex-direction: column;
    
    .message-list {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
    }
  }
  
  .agent-panel {
    flex: 2;
    background: #f5f5f5;
    overflow-y: auto;
    
    .agent-card {
      margin: 10px;
      padding: 15px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      
      &.weather_agent {
        border-left: 4px solid #3498db;
      }
      
      &.rag_agent {
        border-left: 4px solid #9b59b6;
      }
      
      &.academic_agent {
        border-left: 4px solid #e74c3c;
      }
    }
  }
  
  .tool-timeline {
    position: relative;
    padding: 20px;
    
    .timeline-item {
      position: relative;
      padding-left: 30px;
      margin-bottom: 20px;
      
      &::before {
        content: '';
        position: absolute;
        left: 10px;
        top: 0;
        bottom: -20px;
        width: 2px;
        background: #ddd;
      }
    }
  }
}
```

### Phase 4: Advanced Features

#### 4.1 Session Management
```python
# services/session_service.py
class SessionService:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        
    def create_session(self, session_id: str) -> Session:
        session = Session(
            id=session_id,
            created_at=datetime.now(),
            messages=[],
            agent_executions=[]
        )
        self.sessions[session_id] = session
        return session
        
    def save_execution(self, session_id: str, execution: ExecutionTrace):
        if session_id in self.sessions:
            self.sessions[session_id].agent_executions.append(execution)
```

#### 4.2 Export Functionality
```typescript
// services/export.ts
export const exportChatHistory = (messages: Message[], agentData: AgentResponse[]) => {
  const exportData = {
    timestamp: new Date().toISOString(),
    messages,
    agentResponses: agentData,
    summary: generateSummary(agentData)
  };
  
  const blob = new Blob([JSON.stringify(exportData, null, 2)], {
    type: 'application/json'
  });
  
  downloadBlob(blob, `mas-chat-${Date.now()}.json`);
};
```

#### 4.3 Real-time Metrics
```typescript
// components/Metrics/MetricsPanel.tsx
export const MetricsPanel: React.FC = () => {
  const { agentStats } = useAgentMetrics();
  
  return (
    <div className="metrics-panel">
      <h3>Performance Metrics</h3>
      <div className="metrics-grid">
        {Object.entries(agentStats).map(([agent, stats]) => (
          <MetricCard
            key={agent}
            agent={agent}
            avgResponseTime={stats.avgResponseTime}
            totalCalls={stats.totalCalls}
            toolUsage={stats.toolUsage}
          />
        ))}
      </div>
    </div>
  );
};
```

### Phase 5: Deployment

#### 5.1 Docker Configuration
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# frontend/Dockerfile
FROM node:16-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
```

#### 5.2 Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
      - GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION}
    volumes:
      - ${GOOGLE_APPLICATION_CREDENTIALS}:/app/credentials.json
      
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

## Implementation Roadmap

### Week 1: Backend Foundation
- [ ] Set up FastAPI project structure
- [ ] Implement MAS integration service
- [ ] Create tracking interceptor
- [ ] Build WebSocket handler
- [ ] Test with MAS system

### Week 2: Core Frontend
- [ ] Set up React project
- [ ] Implement chat interface
- [ ] Create agent response panel
- [ ] Build WebSocket connection
- [ ] Basic styling

### Week 3: Advanced Features
- [ ] Tool execution timeline
- [ ] Real-time metrics
- [ ] Session management
- [ ] Export functionality
- [ ] Error handling

### Week 4: Polish & Deploy
- [ ] UI/UX improvements
- [ ] Performance optimization
- [ ] Docker deployment
- [ ] Testing & documentation
- [ ] Production deployment

## Success Criteria

1. **Real-time Visibility**: See which agent is processing in real-time
2. **Tool Transparency**: Clear display of all tool calls with parameters
3. **Performance Metrics**: Track response times and tool usage
4. **User Experience**: Smooth, responsive interface
5. **Reliability**: Stable WebSocket connections and error recovery