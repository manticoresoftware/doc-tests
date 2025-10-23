import pytest
from selenium.webdriver.chrome.options import Options
from core.base_test import CustomRemoteWebDriver

def pytest_addoption(parser):
    parser.addoption(
        "--visual", 
        action="store_true", 
        default=False, 
        help="Run tests in visual mode (disable headless)"
    )

@pytest.fixture
def visual_mode(request):
    return request.config.getoption("--visual")

@pytest.fixture(autouse=True, scope="class")
def setup_driver(request):
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