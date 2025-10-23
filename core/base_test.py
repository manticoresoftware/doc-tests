import pytest
import os
import json
from datetime import datetime
from copy import deepcopy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.command import Command


class CustomRemoteWebDriver(webdriver.Remote):
    """Custom Remote WebDriver with console logging support for Selenium 4."""
    
    @property
    def log_types(self):
        try:
            # local Chrome
            return super().log_types
        except AttributeError:
            # remote Chrome
            return self.execute(Command.GET_AVAILABLE_LOG_TYPES)['value']
    
    def get_log(self, log_type):
        try:
            # local Chrome
            log = super().get_log(log_type)
        except AttributeError:
            # remote Chrome
            log = self.execute(Command.GET_LOG, {"type": log_type})['value']
        return log


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

    def capture_network_logs(self, label="", xhr_only=True):
        """Capture and print network requests and responses from performance logs."""
        if not hasattr(self, 'driver'):
            return []
        
        try:
            logs = self.driver.get_log('performance')
            requests = {}
            responses = {}
            response_bodies = {}
            
            for log in logs:
                message = json.loads(log['message'])
                method = message['message']['method']
                
                if method == 'Network.requestWillBeSent':
                    params = message['message']['params']
                    request_id = params['requestId']
                    url = params['request']['url']
                    
                    # Filter for XHR/AJAX requests if xhr_only is True
                    initiator = params.get('initiator', {})
                    initiator_type = initiator.get('type', '')
                    
                    if xhr_only:
                        # Include only actual AJAX requests or search API calls (no JS files)
                        is_ajax = (
                            initiator_type in ['xmlhttprequest', 'fetch'] or
                            (initiator_type == 'script' and '/search' in url.lower() and not url.endswith('.js') and '?' not in url.split('/')[-1])
                        )
                        
                        if not is_ajax:
                            continue
                    
                    requests[request_id] = {
                        'url': url,
                        'method': params['request']['method'],
                        'initiator': initiator_type,
                        'request_id': request_id
                    }
                
                elif method == 'Network.responseReceived':
                    params = message['message']['params']
                    request_id = params['requestId']
                    
                    if request_id in requests:
                        responses[request_id] = {
                            'status': params['response']['status'],
                            'statusText': params['response']['statusText'],
                            'mimeType': params['response'].get('mimeType', ''),
                            'headers': params['response'].get('headers', {})
                        }
                
                elif method == 'Network.loadingFinished':
                    params = message['message']['params']
                    request_id = params['requestId']
                    
                    if request_id in requests and request_id in responses:
                        # Try to get response body using Chrome DevTools Protocol
                        try:
                            # Enable Network domain first
                            self.driver.execute_cdp_cmd('Network.enable', {})
                            
                            # Get response body
                            response = self.driver.execute_cdp_cmd('Network.getResponseBody', {
                                'requestId': request_id
                            })
                            
                            if 'body' in response:
                                body = response['body']
                                if response.get('base64Encoded', False):
                                    import base64
                                    body = base64.b64decode(body).decode('utf-8', errors='ignore')
                                response_bodies[request_id] = body
                        except Exception as e:
                            response_bodies[request_id] = f"(Could not capture body: {str(e)})"
            
            if requests:
                print(f"\n=== {'XHR/AJAX ' if xhr_only else ''}Network Activity {label} ===")
                for req_id, req_data in requests.items():
                    initiator = req_data['initiator'].upper()
                    method = req_data['method']
                    url = req_data['url']
                    
                    print(f"REQUEST: {initiator} {method} {url}")
                    
                    if req_id in responses:
                        resp = responses[req_id]
                        print(f"RESPONSE: {resp['status']} {resp['statusText']}")
                        print(f"MIME TYPE: {resp['mimeType']}")
                        
                        if req_id in response_bodies:
                            body = response_bodies[req_id]
                            if len(body) > 500:
                                print(f"BODY: {body[:500]}... (truncated)")
                            else:
                                print(f"BODY: {body}")
                        else:
                            print("BODY: (no body captured)")
                    else:
                        print("RESPONSE: (no response captured)")
                    print("-" * 50)
                print("=== End Network Activity ===\n")
            else:
                print(f"No {'XHR/AJAX ' if xhr_only else ''}network activity found {label}")
            
            return list(requests.values())
        except Exception as e:
            print(f"Failed to capture network logs: {e}")
            return []

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
        else:
            options.add_argument("--headless")  # run without GUI

        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Enable logging
        options.set_capability('goog:loggingPrefs', {
            'browser': 'ALL',
            'performance': 'ALL'
        })

        # Create custom remote WebDriver connection with logging support
        driver = CustomRemoteWebDriver(
            command_executor=selenium_grid_url,
            options=options
        )

        # Attach driver to the test class (so we can use self.driver)
        request.cls.driver = driver
        yield

        # Close the browser when tests are done
        driver.quit()
