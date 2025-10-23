import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from core.base_test import BaseTest


@pytest.mark.usefixtures("setup_driver")
class TestManualSearch(BaseTest):
    """Tests for ManticoreSearch documentation site."""

    def test_basesearch(self):
        """Test search functionality with installation query."""
        wait = WebDriverWait(self.driver, 30)

        # Enable Network domain for response body capture
        try:
            self.driver.execute_cdp_cmd('Network.enable', {})
        except Exception as e:
            print(f"Could not enable Network domain: {e}")

        # Navigate to website
        self.driver.get("https://manual.manticoresearch.com/")

        # Scroll to top
        self.driver.execute_script("window.scrollTo(0,0)")

        self.get_javascript_errors()
        # Wait for and click search input
        query_input = wait.until(EC.element_to_be_clickable((By.ID, "query")))
        query_input.click()
        query_input.send_keys("installation")

        self.take_screenshot("1search_filled_form")

        # Wait for search results to appear
        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".search-res-item")))
        except TimeoutException:
            # Take screenshot on failure to see what's actually on the page
            # Capture AJAX/search requests right after typing
            self.capture_network_logs("after_fail", xhr_only=False)
            self.capture_console_logs("JS logs")

            self.print_javascript_errors("JS errors")
            self.take_screenshot("search_timeout_failure")
            raise

        self.take_screenshot("2search_after_form")
        # Capture AJAX/search requests right after typing
        self.capture_network_logs("after_search_input", xhr_only=True)


        # Click first search result
        first_result = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".search-res-item:nth-child(1) a")))
        first_result.click()

        target_url = "https://manual.manticoresearch.com/Installation/Installation#Installation"
        try:
            wait.until(EC.url_to_be(target_url))
            assert self.driver.current_url == target_url, f"URL did not match expected: got {self.driver.current_url}, expected {target_url}"
        except TimeoutException as e:
            print(f"Timeout failed: {self.driver.current_url}")
            assert False, "URL did not change to the expected value within the timeout period."

        self.take_screenshot("3search_after_click")
        # At minimum, verify we successfully navigated after clicking search result
        page_title = self.driver.title
        assert page_title and "Installation" in page_title, f"Expected page title to contain 'Installation', got: {page_title}"

        # Check that the page content contains the RPM repository URL
        page_source = self.driver.page_source
        rpm_repo_url = "https://repo.manticoresearch.com/manticore-repo.noarch.rpm"
        assert rpm_repo_url in page_source, f"Expected to find RPM repo URL '{rpm_repo_url}' in page content"

        # Close browser
        self.driver.close()