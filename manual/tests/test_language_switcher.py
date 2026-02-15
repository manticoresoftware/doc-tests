import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.base_test import BaseTest


@pytest.mark.usefixtures("setup_driver")
class TestLanguageSwitcher(BaseTest):
    """Tests for language switching functionality on the documentation site."""

    BASE_URL = "https://manual.manticoresearch.com/"

    def test_switch_to_russian(self):
        """Verify switching language to Russian changes content and URL."""
        self.driver.get(self.BASE_URL)
        time.sleep(2)

        select = Select(self.driver.find_element(By.ID, "language-select"))
        select.select_by_value("ru")
        time.sleep(2)

        assert "/ru/" in self.driver.current_url, \
            f"URL should contain '/ru/', got: {self.driver.current_url}"

        h1 = self.driver.find_element(By.TAG_NAME, "h1")
        assert h1.text == "Введение", \
            f"H1 should be 'Введение', got: '{h1.text}'"


    def test_switch_to_chinese(self):
        """Verify switching language to Chinese changes content and URL."""
        self.driver.get(self.BASE_URL)
        time.sleep(2)

        select = Select(self.driver.find_element(By.ID, "language-select"))
        select.select_by_value("zh")
        time.sleep(2)

        assert "/zh/" in self.driver.current_url, \
            f"URL should contain '/zh/', got: {self.driver.current_url}"


    def test_switch_back_to_english(self):
        """Verify switching from Russian back to English restores content."""
        self.driver.get(self.BASE_URL)
        time.sleep(2)

        # Switch to Russian first
        select = Select(self.driver.find_element(By.ID, "language-select"))
        select.select_by_value("ru")
        time.sleep(2)

        assert "/ru/" in self.driver.current_url

        # Switch back to English
        select = Select(self.driver.find_element(By.ID, "language-select"))
        select.select_by_value("")
        time.sleep(2)

        assert "/ru/" not in self.driver.current_url, \
            f"URL should not contain '/ru/' after switching back, got: {self.driver.current_url}"

        h1 = self.driver.find_element(By.TAG_NAME, "h1")
        assert h1.text == "Introduction", \
            f"H1 should be 'Introduction', got: '{h1.text}'"


    def test_language_cookie_persists(self):
        """Verify that language selection is saved in cookie."""
        self.driver.get(self.BASE_URL)
        time.sleep(2)

        select = Select(self.driver.find_element(By.ID, "language-select"))
        select.select_by_value("ru")
        time.sleep(2)

        cookies = {c['name']: c['value'] for c in self.driver.get_cookies()}
        assert cookies.get('selected-language') == 'ru', \
            f"Cookie 'selected-language' should be 'ru', got: {cookies.get('selected-language')}"

        # Navigate to another page — language should persist
        self.driver.get("https://manual.manticoresearch.com/ru/Starting_the_server/Linux")
        time.sleep(2)

        select_after = Select(self.driver.find_element(By.ID, "language-select"))
        selected_option = select_after.first_selected_option
        assert selected_option.get_attribute("value") == "ru", \
            f"Language selector should still be 'ru', got: '{selected_option.get_attribute('value')}'"

