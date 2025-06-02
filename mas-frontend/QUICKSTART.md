# MAS Testing Frontend - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Prerequisites
- Python 3.9+ installed
- Node.js 16+ installed
- MAS system available at `/Users/eugene/dev/ai/google/adk-samples/python/agents/MAS`

### 1. Run Setup Script
```bash
./setup.sh
```

### 2. Configure Environment (Backend)
Edit `backend/.env`:
```env
GOOGLE_CLOUD_PROJECT=pickuptruckapp
GOOGLE_CLOUD_LOCATION=us-central1
MAS_AGENT_ID=4901227012439408640
```

### 3. Test MAS Connection
```bash
cd backend
source venv/bin/activate
python test_mas_connection.py
```

### 4. Start Backend
```bash
python -m app.main
```
Backend runs at http://localhost:8000

### 5. Start Frontend (new terminal)
```bash
cd frontend
npm start
```
Frontend runs at http://localhost:3000

## 🎯 Testing the System

1. Open http://localhost:3000 in your browser
2. Check the connection status indicator (should show "Connected")
3. Try these test messages:
   - "Hello!" - Tests the Greeter Agent
   - "What's the weather in Paris?" - Tests the Weather Agent
   - "List my document collections" - Tests the RAG Agent
   - "Find papers on transformers" - Tests the Academic Agent

## 📊 Features to Explore

### Chat Interface (Left Panel)
- Real-time message sending
- Message history with timestamps
- Agent response indicators

### Agent Activity (Right Panel)
- **Timeline Tab**: Visual timeline of agent/tool execution
- **Responses Tab**: Detailed agent responses with tool usage
- **Metrics Tab**: Performance metrics and statistics

## 🐳 Docker Alternative

If you prefer Docker:
```bash
docker-compose up --build
```

## 🔧 Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify MAS path in `backend/app/core/mas_client.py`
- Run `python test_mas_connection.py` to debug

### Frontend connection issues
- Check backend is running at http://localhost:8000
- Verify WebSocket URL in frontend console
- Check browser developer tools for errors

### MAS import errors
- Ensure you're in the MAS virtual environment
- Check that MAS system path is correct
- Verify all MAS dependencies are installed

## 📚 Next Steps

1. View API documentation: http://localhost:8000/docs
2. Export chat history using the UI
3. Monitor real-time agent execution
4. Analyze performance metrics
5. Customize the UI for your needs

## 🛠️ Development Tips

- Backend hot-reload is enabled in debug mode
- Frontend auto-refreshes on code changes
- Use Chrome DevTools for WebSocket debugging
- Check `docker-compose logs` for container issues

## 📝 Key Files to Know

- `backend/app/services/mas_service.py` - MAS integration logic
- `frontend/src/components/Chat/ChatInterface.tsx` - Main chat UI
- `frontend/src/components/AgentPanel/ToolTimeline.tsx` - Execution visualization
- `backend/app/core/tracking.py` - Agent/tool execution tracking