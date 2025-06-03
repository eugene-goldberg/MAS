# MAS Complete System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   USER INTERFACE                                 │
│                                                                                  │
│  ┌─────────────────────────┐              ┌─────────────────────────────────┐  │
│  │    Direct Python CLI    │              │      MAS Frontend Web App       │  │
│  │                         │              │                                  │  │
│  │  poetry run chat        │              │  http://localhost:3000           │  │
│  │  (Terminal Interface)   │              │  (Browser Interface)             │  │
│  └────────────┬────────────┘              └────────────┬────────────────────┘  │
│               │                                         │                        │
└───────────────┼─────────────────────────────────────────┼────────────────────────┘
                │                                         │
                │ Direct Python Call                      │ WebSocket (ws://)
                │                                         │
                ▼                                         ▼
┌─────────────────────────────────────┬─────────────────────────────────────────┐
│         MAS Coordinator             │         FastAPI Backend                  │
│    (Direct Integration)             │      (WebSocket Handler)                 │
│                                     │                                           │
│                                     │  • Session Management                    │
│                                     │  • Message Processing                    │
│                                     │  • MASClient Integration                 │
│                                     └─────────────┬───────────────────────────┘
│                                                   │
│                                                   │ MASClient.send_message()
│                                                   ▼
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        MAS Coordinator Agent                             │ │
│  │                    (gemini-2.0-flash-001)                               │ │
│  │                                                                          │ │
│  │  Role: Intelligent request routing based on user intent                  │ │
│  │  Tools: AgentTool wrappers for all sub-agents                           │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                         │
│                    ┌─────────────────┴──────────────────┐                     │
│                    │    Intent Analysis & Routing       │                     │
│                    └─────────────────┬──────────────────┘                     │
└─────────────────────────────────────┼─────────────────────────────────────────┘
                                      │
        ┌─────────────┬───────────────┼───────────────┬─────────────┐
        ▼             ▼               ▼               ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Weather    │ │   Greeter    │ │     RAG      │ │  Academic    │ │  Academic    │
│    Agent     │ │    Agent     │ │    Agent     │ │  WebSearch   │ │ NewResearch  │
│              │ │              │ │              │ │   Wrapper    │ │   Wrapper    │
├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤
│ Model:       │ │ Model:       │ │ Model:       │ │ Model:       │ │ Model:       │
│ gemini-2.0-  │ │ gemini-1.5-  │ │ gemini-2.0-  │ │ gemini-2.0-  │ │ gemini-2.0-  │
│ flash-001    │ │ flash        │ │ flash-001    │ │ flash-001    │ │ flash-001    │
├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤
│ Tools:       │ │ Tools:       │ │ Tools:       │ │ Wraps:       │ │ Wraps:       │
│ • get_weather│ │ • None       │ │ • create_    │ │ academic_    │ │ academic_    │
│ • get_       │ │ (LLM only)   │ │   corpus     │ │ websearch_   │ │ newresearch_ │
│   forecast   │ │              │ │ • add_data   │ │ agent        │ │ agent        │
│              │ │              │ │ • rag_query  │ │              │ │              │
└──────┬───────┘ └──────────────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                                  │               │               │
       ▼                                  ▼               ▼               ▼
┌──────────────┐                  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Open-Meteo   │                  │ Vertex AI    │ │   Google     │ │  Research    │
│     API      │                  │     RAG      │ │   Search     │ │  Analysis    │
│              │                  │              │ │              │ │              │
│ Weather Data │                  │ Document     │ │ Academic     │ │ Future       │
│              │                  │ Embeddings   │ │ Papers       │ │ Directions   │
└──────────────┘                  └──────────────┘ └──────────────┘ └──────────────┘
```

## Message Flow Example

### Academic Research Workflow

```
1. User Message (via Frontend)
   "Tell me about the Transformer paper in the corpus"
   
2. WebSocket Message
   {
     "type": "chat_message",
     "content": "Tell me about the Transformer paper in the corpus"
   }
   
3. MAS Coordinator Analysis
   - Identifies: Document query about specific paper
   - Routes to: RAG Agent
   
4. RAG Agent Processing
   - Tool: rag_query
   - Corpus: seminal_papers
   - Query: "Transformer paper"
   
5. Response Flow
   RAG Agent → Coordinator → FastAPI → WebSocket → React UI
   
6. User Sees
   "The Transformer paper, titled 'Attention Is All You Need'..."
   
7. Follow-up Query
   "Search for recent papers citing this work"
   
8. Coordinator Routes to
   academic_websearch_wrapper (not the original agent)
   
9. Wrapper Agent
   - Extracts: "Transformer" / "Attention Is All You Need"
   - Searches: Recent citations (2024-2025)
   - Returns: List of citing papers
   
10. Final Display
    React UI shows:
    - Chat message with citations
    - Agent activity panel showing:
      * RAG Agent (first query)
      * Academic WebSearch Wrapper (second query)
    - Execution times and tool usage
```

## Key Architectural Decisions

### 1. Coordinator Pattern
- **Why**: Centralized routing logic
- **Benefit**: Easy to add new agents
- **Trade-off**: Single point of failure

### 2. Wrapper Agents for Academic Functions
- **Why**: ADK AgentTool can't pass context variables
- **Benefit**: Natural language interface
- **Trade-off**: Extra abstraction layer

### 3. WebSocket for Frontend
- **Why**: Real-time bidirectional communication
- **Benefit**: Live updates, persistent connection
- **Trade-off**: Stateful connections complicate scaling

### 4. Separate Frontend/Backend
- **Why**: Clear separation of concerns
- **Benefit**: Can scale independently
- **Trade-off**: Additional complexity

## Technology Stack

### Frontend
- React 18 with TypeScript
- Material-UI for components
- WebSocket API for real-time
- Selenium for testing

### Backend
- FastAPI (Python)
- Google ADK for agents
- Vertex AI for LLMs
- AsyncIO for concurrency

### Infrastructure
- Google Cloud Platform
- Vertex AI APIs
- Cloud Storage
- Firestore (optional)

## Deployment Architecture

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   Cloud Run         │     │   Cloud Run         │     │  Vertex AI          │
│   (Frontend)        │────▶│   (Backend)         │────▶│  Endpoints          │
│                     │     │                     │     │                     │
│  • React App        │     │  • FastAPI          │     │  • MAS Coordinator  │
│  • Static Assets    │     │  • WebSocket        │     │  • Sub-Agents       │
│  • Nginx            │     │  • MAS Client       │     │  • Models           │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
                                      │
                                      ▼
                            ┌─────────────────────┐
                            │   Cloud Firestore   │
                            │                     │
                            │  • Sessions         │
                            │  • Conversations    │
                            │  • Metrics          │
                            └─────────────────────┘
```

## Testing Strategy

### Unit Tests
- Individual agent testing
- Tool function validation
- Service layer tests

### Integration Tests
- WebSocket connection tests
- End-to-end message flow
- Agent routing validation

### UI Tests (Selenium)
- Full conversation flows
- All agent interactions
- Error handling scenarios

### Performance Tests
- Response time monitoring
- Concurrent user handling
- WebSocket stability

## Security Considerations

1. **Authentication**: Add auth to WebSocket endpoints
2. **Rate Limiting**: Prevent abuse of agent calls
3. **Input Validation**: Sanitize all user inputs
4. **CORS**: Configure for production domains
5. **Secrets**: Use Secret Manager for API keys

## Monitoring & Observability

1. **Metrics**:
   - Response times per agent
   - Success/failure rates
   - Active WebSocket connections

2. **Logging**:
   - Structured JSON logs
   - Request/response traces
   - Error tracking

3. **Alerts**:
   - High error rates
   - Slow response times
   - Agent failures