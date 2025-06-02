# MAS Frontend Selenium UI Tests

This directory contains comprehensive Selenium-based UI tests for the MAS (Multi-Agent System) frontend.

## Test Coverage

The test suite covers:

1. **Frontend Accessibility** - Verifies the frontend loads at http://localhost:3000
2. **WebSocket Connection** - Checks WebSocket connection status indicator
3. **Chat Interface** - Tests all chat UI elements are present and interactive
4. **Message Sending** - Verifies messages can be sent through the interface
5. **Agent Interactions** - Tests all 5 agents:
   - Greeter Agent
   - Weather Agent
   - RAG Agent
   - Academic WebSearch Agent
   - Academic NewResearch Agent
6. **UI Responsiveness** - Tests responsive design and hover interactions
7. **Agent Panel** - Verifies agent response panel functionality
8. **Error Handling** - Tests edge cases like empty messages
9. **Metrics Display** - Checks for timing and metrics displays
10. **Comprehensive Check** - Final validation of all components

## Prerequisites

1. **Chrome Browser** - Latest version of Google Chrome
2. **ChromeDriver** - Will be automatically managed by webdriver-manager
3. **Python 3.8+** - Required for running the tests
4. **Running Services**:
   - Frontend must be running at http://localhost:3000
   - Backend/WebSocket server must be running
   - MAS agents must be deployed and accessible

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Tests

### Run all tests:
```bash
python3 test_ui_selenium.py
```

### Run a specific test:
```bash
python3 test_ui_selenium.py test_01_frontend_accessibility
```

### Run with visible browser (not headless):
Edit `test_ui_selenium.py` and comment out line 35:
```python
# cls.chrome_options.add_argument("--headless")
```

### Run with pytest (alternative):
```bash
pytest test_ui_selenium.py -v
```

### Generate HTML report with pytest:
```bash
pytest test_ui_selenium.py --html=report.html --self-contained-html
```

## Test Output

The tests will:
- Print detailed progress for each test
- Check for JavaScript console errors
- Take screenshots on failures (saved in current directory)
- Provide a summary of component status

## Debugging Failed Tests

1. **Screenshots** - Check generated .png files for visual state
2. **Console Errors** - Each test reports JavaScript errors found
3. **Verbose Mode** - Tests run with verbosity=2 by default
4. **Browser Logs** - Console logs are captured and reported

## Common Issues

1. **WebSocket Connection Failed**
   - Ensure backend is running
   - Check WebSocket endpoint configuration
   - Verify no firewall blocking

2. **Elements Not Found**
   - Frontend may have changed - update selectors
   - Increase wait timeouts if needed
   - Check if components are lazy-loaded

3. **Agent Not Responding**
   - Verify MAS agents are deployed
   - Check agent endpoint configuration
   - Increase response timeout

4. **ChromeDriver Issues**
   - webdriver-manager should handle this automatically
   - If issues persist, manually download ChromeDriver

## Customization

- **Timeouts**: Adjust wait times in `_wait_for_element()` methods
- **Headless Mode**: Toggle in `setUpClass()` method
- **Base URL**: Change `self.base_url` in `setUp()` method
- **Agent Names**: Update agent name checks in agent interaction tests

## CI/CD Integration

The tests are designed to run in CI/CD pipelines:
- Headless mode enabled by default
- No manual intervention required
- Exit codes indicate success/failure
- Screenshots captured for debugging