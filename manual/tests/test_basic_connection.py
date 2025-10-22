import pytest
from selenium.webdriver.common.by import By
from core.base_test import BaseTest


@pytest.mark.usefixtures("setup_driver")
class TestBasicConnection(BaseTest):
    """Basic connectivity test for Selenium setup."""

    def test_website_loads(self):
        """Verify that the website loads successfully."""
        # Step 1: Open the website
        self.driver.get("https://manual.manticoresearch.com/")
        
        # Step 2: Check that the page title is not empty
        title = self.driver.title
        assert title, "Page title should not be empty"
        
        # Step 3: Check that we can get the page source
        page_source = self.driver.page_source
        assert "manticore" in page_source.lower() or "search" in page_source.lower(), "Page should contain relevant content"