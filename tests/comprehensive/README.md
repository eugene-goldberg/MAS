# Comprehensive MAS Agent Testing Suite

This directory contains comprehensive tests to verify full functionality of every tool in every agent of the Multi-Agent System (MAS).

## Test Files

### 1. `test_all_agents_tools.py`
Main comprehensive test suite that tests:
- **Weather Agent**: All weather tools (get_weather, get_forecast)
- **RAG Agent**: All RAG tools (create_corpus, list_corpora, add_data, rag_query, get_corpus_info, delete_corpus)
- **Academic Agents**: PDF analysis and formatting tools
- **Greeter Agent**: Response generation
- **MAS Coordinator**: Routing to appropriate sub-agents

Generates detailed JSON report with test results.

### 2. `quick_test.py`
Quick validation test for rapid checks:
- Basic functionality of key agents
- Minimal test coverage
- Fast execution (~10 seconds)

### 3. `test_individual_tools.py`
Direct tool testing without agent wrappers:
- Isolates tool-specific issues
- Tests tools with direct function calls
- Helpful for debugging

### 4. `run_tests.sh`
Bash script to run the comprehensive test suite:
- Sets up environment
- Activates virtual environment
- Runs all tests
- Reports results

## Running Tests

### Quick Validation
```bash
cd /Users/eugene/dev/ai/google/adk-samples/python/agents/MAS
python3 tests/comprehensive/quick_test.py
```

### Comprehensive Test Suite
```bash
cd /Users/eugene/dev/ai/google/adk-samples/python/agents/MAS
./tests/comprehensive/run_tests.sh
```

### Individual Tool Testing
```bash
cd /Users/eugene/dev/ai/google/adk-samples/python/agents/MAS
source venv/bin/activate
python3 tests/comprehensive/test_individual_tools.py
```

### Direct Python Execution
```bash
cd /Users/eugene/dev/ai/google/adk-samples/python/agents/MAS
source venv/bin/activate
python3 tests/comprehensive/test_all_agents_tools.py
```

## Test Coverage

### Weather Agent Tools
- ✅ `get_weather(city)` - Get current weather
- ✅ `get_forecast(city, days)` - Get weather forecast
- ✅ Agent query response

### RAG Agent Tools
- ✅ `create_corpus()` - Create new RAG corpus
- ✅ `list_corpora()` - List all corpora
- ✅ `add_data()` - Add document to corpus
- ✅ `rag_query()` - Query documents
- ✅ `get_corpus_info()` - Get corpus details
- ✅ `delete_corpus()` - Delete corpus

### Academic Agent Tools
- ✅ `analyze_seminal_paper()` - Analyze PDF paper
- ✅ `prepare_paper_for_citation_search()` - Format for search
- ✅ `format_citations_for_research()` - Format citations

### Greeter Agent
- ✅ Greeting responses
- ✅ Farewell responses
- ✅ General conversation

### MAS Coordinator
- ✅ Route to Weather Agent
- ✅ Route to RAG Agent
- ✅ Route to Academic Agents
- ✅ Route to Greeter Agent

## Test Output

### Console Output
- Real-time test execution status
- Pass/Fail indicators
- Summary statistics

### JSON Report
Generated at: `test_report_<timestamp>.json`

Contains:
- Test timestamp
- Summary statistics
- Detailed results for each test
- Error messages and stack traces
- Performance metrics

## Expected Results

All tests should pass with:
- ✅ 100% success rate
- No errors or failures
- Response times under 5 seconds per test
- Proper error handling for edge cases

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure `.env` file exists with correct credentials
   - Check GOOGLE_CLOUD_PROJECT is set

2. **Module Import Errors**
   - Activate virtual environment
   - Install dependencies: `poetry install`

3. **RAG Corpus Errors**
   - Ensure Vertex AI APIs are enabled
   - Check IAM permissions

4. **Network Timeouts**
   - Check internet connectivity
   - Retry tests

## Adding New Tests

To add tests for new tools:

1. Import the tool in `test_all_agents_tools.py`
2. Add test method in appropriate class
3. Use consistent TestResult format
4. Include both success and error cases
5. Update this README with new coverage