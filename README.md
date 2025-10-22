# 🧪 Selenium UI Test Suite - Local Testing Guide

This guide explains how to run Selenium UI tests locally for the ManticoreSearch documentation website.

## 📋 Prerequisites

- Docker installed and running
- Python 3.9+ installed
- Git repository cloned locally

## 🚀 Quick Start

### 1. Start Selenium Chrome Container

#### **Headless Mode (Default)**

**For Intel/AMD64 systems:**
```bash
docker run -d -p 4444:4444 selenium/standalone-chrome:4
```

**For Apple Silicon (ARM64) systems:**
```bash
docker run -d -p 4444:4444 --platform linux/amd64 selenium/standalone-chrome:4
```

#### **Visual Mode with VNC (See Browser Actions)**

**For Intel/AMD64 systems:**
```bash
docker run -d -p 4444:4444 -p 7900:7900 selenium/standalone-chrome:4
```

**For Apple Silicon (ARM64) systems:**
```bash
docker run -d -p 4444:4444 -p 7900:7900 --platform linux/amd64 selenium/standalone-chrome:4
```

**To watch test execution:**
1. Open browser to `http://localhost:7900`
2. Enter password: `secret`
3. You'll see Chrome browser inside container
4. Run your tests with flag `--visual` and watch them execute live!


### 2. Set Up Virtual Environment

Navigate to the selenium test directory and create a virtual environment:

```bash
# Create virtual environment
python3 -m venv selenium_env

# Activate virtual environment
source selenium_env/bin/activate

# You should see (selenium_env) in your prompt
```

### 3. Install Test Dependencies

With the virtual environment activated:

```bash
# Install dependencies
pip install -r core/requirements.txt
```

### 4. Run the Tests

From the root directory with virtual environment activated:

```bash
# Run all Selenium tests
pytest manual/tests -v

# Run specific test file
pytest manual/tests/test_manual_search.py -v

# Run with detailed output
pytest manual/tests -v -s
```

### 5. Deactivate Virtual Environment

When done testing:

```bash
deactivate
```

## 🔄 Subsequent Test Runs

For future test sessions, you only need to:

```bash
# 1. Start Selenium container (if not running)
# Headless mode:
docker run -d -p 4444:4444 --platform linux/amd64 selenium/standalone-chrome:4
# Visual mode (with VNC viewer):
docker run -d -p 4444:4444 -p 7900:7900 --platform linux/amd64 selenium/standalone-chrome:4

# 2. Activate existing virtual environment
source selenium_env/bin/activate

# 3. Run tests
pytest manual/tests -v

# 4. Deactivate when done
deactivate
```

## 🖥️ Visual Testing (Watch Browser Actions)

### Enable Visual Mode

To see browser actions during test execution:

#### 1. Stop Current Container
```bash
docker stop $(docker ps -q --filter ancestor=selenium/standalone-chrome:4)
```

#### 2. Start VNC-Enabled Container
```bash
# For Apple Silicon (ARM64):
docker run -d -p 4444:4444 -p 7900:7900 --platform linux/amd64 selenium/standalone-chrome:4

# For Intel/AMD64:
docker run -d -p 4444:4444 -p 7900:7900 selenium/standalone-chrome:4
```

#### 3. Watch Tests Execute
1. Open browser to: `http://localhost:7900`
2. Enter password: `secret`
3. Run your tests - you'll see Chrome browser actions live!

## 🧩 Adding New Tests

1. Create new test file in `manual/tests/`
2. Use this template:

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

3. Run the new test (from the root directory with venv activated):

```bash
pytest manual/tests/test_new_feature.py -v
```
## 📁 Directory Structure

After setup, your directory structure will look like:

```
├── README.md                  # This guide
├── conftest.py                # Allows to run in visual mode
├── core/
│   ├── requirements.txt       # Dependencies
│   ├── base_test.py          # WebDriver setup
│   └── __init__.py           # Package file
└── manual/
    ├── __init__.py           # Package file
    └── tests/
        ├── __init__.py       # Package file
        └── test_manual_search.py  # Test file
```

## 🚀 Quick Command Reference

### **Headless Testing (Default)**
```bash
# Start container
docker run -d -p 4444:4444 --platform linux/amd64 selenium/standalone-chrome:4

python3 -m venv selenium_env
source selenium_env/bin/activate
pip install -r core/requirements.txt
pytest manual/tests -v
```

### **Visual Testing (Watch Browser)**
```bash
# Start VNC-enabled container
docker run -d -p 4444:4444 -p 7900:7900 --platform linux/amd64 selenium/standalone-chrome:4

# Open VNC viewer: http://localhost:7900 (password: secret)
# Run tests and watch live!
source selenium_env/bin/activate
pytest manual/tests -v
```
