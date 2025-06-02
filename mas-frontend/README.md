# MAS Testing Frontend

A comprehensive testing and visualization interface for the Multi-Agent System (MAS) using FastAPI (backend) and React.js (frontend).

## Features

- **Real-time Chat Interface**: Interactive chat with the MAS coordinator
- **Agent Activity Visualization**: See which agents are processing requests in real-time
- **Tool Usage Timeline**: Track tool executions with timing information
- **WebSocket Communication**: Live updates as agents process requests
- **Session Management**: Persistent chat history and execution traces
- **Performance Metrics**: Track agent response times and tool usage

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

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- Google Cloud credentials configured
- MAS system deployed

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the backend:
```bash
python -m app.main
```

The API will be available at http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env if needed
```

4. Run the frontend:
```bash
npm start
```

The UI will be available at http://localhost:3000

## Docker Deployment

Run both services with Docker Compose:

```bash
docker-compose up --build
```

## API Documentation

Once the backend is running, view the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Available Agents

1. **Weather Agent**: Weather information and forecasts
2. **RAG Agent**: Document management and semantic search
3. **Academic WebSearch**: Find academic papers
4. **Academic NewResearch**: Suggest research directions
5. **Greeter Agent**: Handle greetings and farewells

## Development

### Backend Structure
```
backend/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Core functionality
│   ├── models/       # Data models
│   └── services/     # Business logic
└── tests/            # Test suite
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/   # React components
│   ├── contexts/     # Context providers
│   ├── hooks/        # Custom hooks
│   ├── services/     # API services
│   └── types/        # TypeScript types
└── public/           # Static assets
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## License

This project is part of the Google Agent Development Kit samples.