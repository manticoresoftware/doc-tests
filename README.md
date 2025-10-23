# 🧪 Selenium UI Test Suite

Automated UI tests for the ManticoreSearch documentation website, supporting both local development and CI/CD workflows.

## 📋 Prerequisites

- Docker installed and running
- Python 3.9+ installed
- Git repository cloned locally

## 🚀 Quick Start

### 1. Start Selenium Container

```bash
docker run -d -p 4444:4444 -p 7900:7900 --platform linux/amd64 selenium/standalone-chrome:4
```

### 2. Setup Python Environment

```bash
# Create and activate virtual environment
python3 -m venv selenium_env
source selenium_env/bin/activate

# Install dependencies
pip install -r core/requirements.txt
```

### 3. Run Tests

```bash
# Run all tests
pytest manual/tests -v

# Run specific test
pytest manual/tests/test_manual_search.py -v

# Run with detailed output
pytest manual/tests -v -s
```

### 4. Watch Tests Execute (Optional)

1. Open browser to `http://localhost:7900`
2. Enter password: `secret`
3. Watch your tests run in real-time!

## 🔄 Subsequent Runs

```bash
# Start container (if not running)
docker run -d -p 4444:4444 -p 7900:7900 --platform linux/amd64 selenium/standalone-chrome:4

# Activate environment and run tests
source selenium_env/bin/activate
pytest manual/tests -v
deactivate
```

## 🧩 Writing Tests

Create new test files in `manual/tests/` using this template:

```python
import pytest
from selenium.webdriver.common.by import By
from core.base_test import BaseTest

@pytest.mark.usefixtures("setup_driver")
class TestNewFeature(BaseTest):
    def test_example(self):
        self.driver.get("https://manual.manticoresearch.com/")
        # Your test steps here
```

## 🐛 Debugging Tools

The `BaseTest` class provides powerful debugging tools for troubleshooting test failures.

### Screenshots
```python
# Take manual screenshots
self.take_screenshot("before_action")
self.take_screenshot("after_action")
```

- **Local**: Saved to `screenshots/` directory with timestamps
- **CI**: Automatically uploaded to GitHub Actions artifacts when tests fail

### Console Logs
```python
# Capture browser console logs
self.capture_console_logs("after_page_load")
```

### JavaScript Errors

JavaScript error detection works in two phases:

```python
# 1. START monitoring (install listener)
self.driver.get("https://example.com")
self.start_javascript_error_monitoring()  # Begin collecting errors

# 2. Perform actions that might cause errors
button.click()

# 3. END monitoring (retrieve collected errors)
self.print_javascript_errors("after_action")  # Pretty print errors

# Or get errors programmatically
errors = self.get_javascript_errors()  # Get raw error data
assert len(errors) == 0, f"JS errors: {errors}"
```

### Network Activity
```python
# Monitor AJAX/XHR requests
self.capture_network_logs("api_calls")

# Monitor all network activity
self.capture_network_logs("all_requests", xhr_only=False)
```

### Complete Debugging Example
```python
@pytest.mark.usefixtures("setup_driver")
class TestWithDebugging(BaseTest):
    def test_search_with_full_debugging(self):
        # Initial state
        self.take_screenshot("start")
        self.driver.get("https://manual.manticoresearch.com/")
        
        # START monitoring JS errors early
        self.start_javascript_error_monitoring()
        
        # Check page load
        self.capture_console_logs("page_load")
        self.print_javascript_errors("page_load")  # Check for early errors
        
        # Perform search
        search_input = self.driver.find_element(By.CLASS_NAME, "DocSearch-Input")
        search_input.send_keys("SELECT")
        self.capture_network_logs("search_request")
        
        # Final validation
        self.take_screenshot("final_state")
        errors = self.get_javascript_errors()  # END monitoring - get all errors
        if errors:
            pytest.fail(f"JavaScript errors: {errors}")
```

## 📊 CI/CD Integration

Tests run automatically on:
- Pull requests to `main` branch
- Daily scheduled runs

**Important**: Screenshots are only uploaded to GitHub Actions artifacts when tests **fail**.

## 📁 Project Structure

```
├── README.md                    # This guide
├── conftest.py                  # Pytest configuration
├── core/
│   ├── requirements.txt         # Python dependencies
│   ├── base_test.py            # Base test class with debugging tools
│   └── __init__.py
└── manual/
    ├── __init__.py
    └── tests/
        ├── __init__.py
        └── test_manual_search.py  # Example test
```

## 🎯 Tips & Best Practices

### Local Development
- Use visual mode (`http://localhost:7900`) to watch tests execute
- Add `time.sleep(2)` between actions for easier observation
- Take screenshots at key points to document test flow
- Monitor browser console for JavaScript errors

### Debugging Failed Tests
- Check screenshots in `screenshots/` directory (local) or GitHub artifacts (CI)
- Review console logs and JavaScript errors in test output
- Use network monitoring to verify API calls
- Run tests in visual mode to observe browser behavior

### Performance
- Use `xhr_only=True` (default) for network monitoring to reduce noise
- Take targeted screenshots rather than after every action
- Clear browser logs periodically in long tests