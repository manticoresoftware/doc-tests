import pytest
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class BaseTest:
    """Base class that sets up and tears down the Selenium WebDriver."""

    def take_screenshot(self, name="screenshot"):
        """Take a screenshot and save it to screenshots directory."""
        if not hasattr(self, 'driver'):
            return
        
        # Create screenshots directory if it doesn't exist
        os.makedirs("screenshots", exist_ok=True)
        
        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/{name}_{timestamp}.png"
        
        try:
            self.driver.save_screenshot(filename)
            print(f"Screenshot saved: {filename}")
            return filename
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return None

    def capture_console_logs(self, label=""):
        """Capture and print browser console logs."""
        if not hasattr(self, 'driver'):
            return
        
        try:
            # Get browser logs
            logs = self.driver.get_log('browser')
            
            if logs:
                print(f"\n=== Browser Console Logs {label} ===")
                for log in logs:
                    level = log['level']
                    message = log['message']
                    timestamp = log['timestamp']
                    print(f"[{level}] {timestamp}: {message}")
                print("=== End Console Logs ===\n")
            else:
                print(f"No console logs found {label}")
                
        except Exception as e:
            print(f"Failed to capture console logs: {e}")

    def get_javascript_errors(self):
        """Get JavaScript errors by injecting error detection script."""
        if not hasattr(self, 'driver'):
            return []
        
        try:
            # Inject JavaScript to collect errors
            js_script = """
            if (!window.jsErrors) {
                window.jsErrors = [];
                window.addEventListener('error', function(e) {
                    window.jsErrors.push({
                        message: e.message,
                        filename: e.filename,
                        lineno: e.lineno,
                        colno: e.colno,
                        stack: e.error ? e.error.stack : 'No stack trace'
                    });
                });
            }
            return window.jsErrors;
            """
            
            errors = self.driver.execute_script(js_script)
            return errors or []
            
        except Exception as e:
            print(f"Failed to get JavaScript errors: {e}")
            return []

    def print_javascript_errors(self, label=""):
        """Print any JavaScript errors that have occurred."""
        errors = self.get_javascript_errors()
        
        if errors:
            print(f"\n=== JavaScript Errors {label} ===")
            for i, error in enumerate(errors, 1):
                print(f"Error {i}:")
                print(f"  Message: {error.get('message', 'Unknown')}")
                print(f"  File: {error.get('filename', 'Unknown')}")
                print(f"  Line: {error.get('lineno', 'Unknown')}")
                print(f"  Column: {error.get('colno', 'Unknown')}")
                print(f"  Stack: {error.get('stack', 'No stack trace')}")
                print()
            print("=== End JavaScript Errors ===\n")
        else:
            print(f"No JavaScript errors found {label}")

    @pytest.fixture(autouse=True, scope="class")
    def setup_driver(self, request):
        # Address of Selenium Grid or local standalone container
        selenium_grid_url = "http://localhost:4444/wd/hub"

        # Chrome options for CI
        options = Options()
        
        # Check for --visual flag
        visual_mode = request.config.getoption("--visual", default=False)
        
        if visual_mode:
            print("🖥️  Running in VISUAL mode - check VNC at http://localhost:7900 (password: secret)")
            options.add_argument("--start-maximized")
        else:
            options.add_argument("--headless")  # run without GUI

        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Create remote WebDriver connection
        driver = webdriver.Remote(
            command_executor=selenium_grid_url,
            options=options
        )

        # Attach driver to the test class (so we can use self.driver)
        request.cls.driver = driver
        yield

        # Close the browser when tests are done
        driver.quit()
