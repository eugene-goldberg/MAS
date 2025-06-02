# MAS Quick Reference Guide

## 🚀 Quick Start

### Test the System
```bash
# Quick validation
cd /Users/eugene/dev/ai/google/adk-samples/python/agents/MAS
source venv/bin/activate
python3 tests/comprehensive/quick_test.py

# Full test suite (100% coverage)
./tests/comprehensive/run_tests.sh
```

### Deploy Changes
```bash
cd deployment
python3 deploy.py --build --deploy
```

## 🤖 Agent Capabilities

### Weather Agent
```python
# Example queries:
"What's the weather in Paris?"
"Give me a 5-day forecast for New York"
"What's the temperature in Tokyo?"
```

### RAG Agent
```python
# Example queries:
"Create a new document collection called 'research'"
"Add this PDF to my documents"
"Search for information about machine learning"
"List all my document collections"
```

### Academic Agents
```python
# Example workflow:
"Analyze the Transformers paper"
"Find recent papers citing this work"
"Suggest future research directions"
```

### Greeter Agent
```python
# Example queries:
"Hello!"
"Good morning"
"Goodbye"
```

## 📁 Project Structure
```
MAS/
├── mas_system/              # Core agent code
│   ├── agent.py            # MAS Coordinator
│   └── sub_agents/         # All sub-agents
├── cloud_functions/        # RAG ingestion function
├── deployment/             # Deployment scripts
├── tests/                  # Test suites
│   └── comprehensive/      # 100% coverage tests
└── docs/                   # Documentation
```

## 🛠️ Common Commands

### RAG Document Management
```bash
# Upload document to trigger ingestion
gsutil cp document.pdf gs://mas-rag-documents-dev/

# Check processing status
gsutil ls gs://mas-rag-documents-dev/processed/
gsutil ls gs://mas-rag-documents-dev/failed/

# Monitor Cloud Function
./cloud_functions/rag_ingestion/scripts/monitor.sh dev
```

### Testing Specific Agents
```python
# Test individual tools
python3 tests/comprehensive/test_individual_tools.py

# Test specific agent
from mas_system.sub_agents.weather_agent import weather_agent
# Use agent...
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
GOOGLE_CLOUD_PROJECT=pickuptruckapp
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_STORAGE_BUCKET=pickuptruckapp-bucket
```

### Current Deployment
- **MAS Agent ID**: 4901227012439408640
- **Cloud Function**: rag-ingestion-function-dev
- **RAG Corpus**: mas-rag-corpus
- **GCS Bucket**: mas-rag-documents-dev

## 📊 System Stats

| Component | Count |
|-----------|-------|
| Total Agents | 6 |
| Total Tools | 14 |
| Weather Tools | 4 |
| RAG Tools | 7 |
| Academic Tools | 3 |
| Test Coverage | 100% |

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   source venv/bin/activate
   poetry install
   ```

2. **RAG Tool Errors**
   - Ensure Vertex AI APIs are enabled
   - Check IAM permissions
   - Verify corpus exists

3. **Weather API Errors**
   - Check internet connectivity
   - Verify location names

4. **Cloud Function Not Triggering**
   - Check Eventarc permissions
   - Verify bucket configuration
   - Review function logs

### Useful Debug Commands
```bash
# Check function logs
gcloud functions logs read rag-ingestion-function-dev \
  --region=us-central1 --limit=50

# List all corpora
python3 -c "
from mas_system.sub_agents.rag_agent.tools import list_corpora
print(list_corpora())"

# Test weather tool
python3 -c "
from mas_system.sub_agents.weather_agent.tools.weather import get_current_weather
print(get_current_weather('London'))"
```

## 🎯 Key ADK Requirements

**CRITICAL**: All tools must return dictionaries, not strings!

```python
# ✅ Correct
def my_tool():
    return {
        "status": "success",
        "data": {"result": "value"}
    }

# ❌ Wrong
def my_tool():
    return "string result"
```

## 📚 More Information

- Full Architecture: `MAS_ARCHITECTURE.md`
- Visual Diagrams: `MAS_VISUAL_DIAGRAM.md`
- Test Results: `tests/comprehensive/TEST_RESULTS_FINAL.md`
- Cloud Function: `cloud_functions/rag_ingestion/README.md`