import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from core.base_test import BaseTest


@pytest.mark.usefixtures("setup_driver")
class TestManualSearch(BaseTest):
    """Tests for ManticoreSearch documentation site."""

    def test_basesearch(self):
        """Test search functionality with installation query."""
        wait = WebDriverWait(self.driver, 30)

        # Navigate to website
        self.driver.get("https://manual.manticoresearch.com/")

        # Scroll to top
        self.driver.execute_script("window.scrollTo(0,0)")

        # Wait for and click search input
        query_input = wait.until(EC.element_to_be_clickable((By.ID, "query")))
        query_input.click()
        query_input.send_keys("installation")

        import time
        time.sleep(5)

        # Wait for search results to appear
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".search-res-item")))

        # Verify search results contain installation-related content
        search_results = self.driver.find_elements(By.CSS_SELECTOR, ".search-res-item")
        assert len(search_results) > 0, "No search results found"

        # Click first search result
        first_result = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".search-res-item:nth-child(1) a")))
        first_result.click()


        # Verify we navigated to a new page (URL should have changed)
        current_url = self.driver.current_url
        assert "manual.manticoresearch.com" in current_url, f"Expected to stay on manticore domain, got: {current_url}"


        target_url = "https://manual.manticoresearch.com/Installation/Installation#Installation"
        try:
            wait.until(EC.url_to_be(target_url))
            assert self.driver.current_url == target_url, f"URL did not match expected: got {self.driver.current_url}, expected {target_url}"
        except TimeoutException as e:
            print(f"Timeout failed: {self.driver.current_url}")
            assert False, "URL did not change to the expected value within the timeout period."


        # At minimum, verify we successfully navigated after clicking search result
        page_title = self.driver.title
        assert page_title and "Installation" in page_title, f"Expected page title to contain 'Installation', got: {page_title}"

        # Check that the page content contains the RPM repository URL
        page_source = self.driver.page_source
        rpm_repo_url = "https://repo.manticoresearch.com/manticore-repo.noarch.rpm"
        assert rpm_repo_url in page_source, f"Expected to find RPM repo URL '{rpm_repo_url}' in page content"

        # Close browser
        self.driver.close()
