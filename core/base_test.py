import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class BaseTest:
    """Base class that sets up and tears down the Selenium WebDriver."""

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
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")
        else:
            options.add_argument("--headless")  # run without GUI
            
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
