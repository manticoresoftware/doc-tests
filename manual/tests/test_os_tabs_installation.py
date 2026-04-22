import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.base_test import BaseTest


@pytest.mark.usefixtures("setup_driver")
class TestOsTabsInstallation(BaseTest):
    """Tests for OS tab switching on the Installation page."""

    INSTALL_URL = "https://manual.manticoresearch.com/Installation/Installation"

    def _get_tab_block(self):
        """Find the OS tabs block on the Installation page."""
        self.driver.get(self.INSTALL_URL)
        time.sleep(2)

        # Find the lang-sel block that contains OS tabs (RHEL, Debian, etc.)
        blocks = self.driver.find_elements(By.CSS_SELECTOR, "div.lang-sel")
        for block in blocks:
            tabs = block.find_elements(By.CSS_SELECTOR, "li span.lang-text")
            tab_texts = [t.get_attribute("textContent").strip() for t in tabs]
            if any("RHEL" in t for t in tab_texts):
                return block
        pytest.fail("OS tabs block not found on Installation page")

    def _get_visible_body_text(self, block):
        """Get text content of the currently visible example-body."""
        example = block.find_element(By.XPATH, "./ancestor::div[contains(@class, 'example')]")
        bodies = example.find_elements(By.CSS_SELECTOR, ".example-body")
        for body in bodies:
            if body.is_displayed():
                return body.text.strip()
        return ""

    def _get_active_tab_text(self, block):
        """Get the text of the currently active tab."""
        active_li = block.find_element(By.CSS_SELECTOR, "li.active span.lang-text")
        return active_li.get_attribute("textContent").strip()

    def _click_tab(self, block, tab_text):
        """Click a tab by its text content."""
        old_content = self._get_visible_body_text(block)
        tabs = block.find_elements(By.CSS_SELECTOR, "li")
        for tab in tabs:
            span = tab.find_element(By.CSS_SELECTOR, "span.lang-text")
            if span.get_attribute("textContent").strip() == tab_text:
                self.driver.execute_script("arguments[0].click();", tab)
                # Wait for content to change (up to 5 seconds)
                for _ in range(10):
                    time.sleep(0.5)
                    new_content = self._get_visible_body_text(block)
                    if new_content != old_content:
                        tab_text = self._get_active_tab_text(block)
                        break
                self.driver.execute_script("arguments[0].click();", tab)
                time.sleep(0.5)
                return
        pytest.fail(f"Tab '{tab_text}' not found")

    def test_default_tab_is_rhel(self):
        """Verify that RHEL tab is active by default."""
        block = self._get_tab_block()

        active = self._get_active_tab_text(block)
        assert "RHEL" in active, \
            f"Default active tab should contain 'RHEL', got: '{active}'"

        content = self._get_visible_body_text(block)
        assert "yum install" in content, \
            f"RHEL tab should show yum install command, got: '{content[:100]}'"


    def test_switch_to_debian(self):
        """Verify switching to Debian tab shows apt/wget commands."""
        block = self._get_tab_block()

        self._click_tab(block, "Debian, Ubuntu, Mint")

        active = self._get_active_tab_text(block)
        assert "Debian" in active, \
            f"Active tab should contain 'Debian', got: '{active}'"

        content = self._get_visible_body_text(block)
        assert "wget" in content or "apt" in content, \
            f"Debian tab should show wget/apt commands, got: '{content[:100]}'"


    def test_switch_to_docker(self):
        """Verify switching to Docker tab shows docker commands."""
        block = self._get_tab_block()

        self._click_tab(block, "Docker")

        active = self._get_active_tab_text(block)
        assert "Docker" in active, \
            f"Active tab should be 'Docker', got: '{active}'"

        content = self._get_visible_body_text(block)
        assert "docker" in content.lower(), \
            f"Docker tab should show docker commands, got: '{content[:100]}'"


    def test_switch_to_macos(self):
        """Verify switching to MacOS tab shows brew commands."""
        block = self._get_tab_block()

        self._click_tab(block, "MacOS")

        active = self._get_active_tab_text(block)
        assert "MacOS" in active, \
            f"Active tab should be 'MacOS', got: '{active}'"

        content = self._get_visible_body_text(block)
        assert "brew" in content, \
            f"MacOS tab should show brew command, got: '{content[:100]}'"


    def test_switch_to_kubernetes(self):
        """Verify switching to Kubernetes tab shows helm commands."""
        block = self._get_tab_block()

        self._click_tab(block, "Kubernetes")

        active = self._get_active_tab_text(block)
        assert "Kubernetes" in active, \
            f"Active tab should be 'Kubernetes', got: '{active}'"

        content = self._get_visible_body_text(block)
        assert "helm" in content, \
            f"Kubernetes tab should show helm commands, got: '{content[:100]}'"


    def test_switching_tabs_changes_content(self):
        """Verify that switching between tabs actually changes visible content."""
        block = self._get_tab_block()

        # Explicitly select RHEL first
        self._click_tab(block, "RHEL, Centos, Alma, Amazon, Oracle")
        rhel_content = self._get_visible_body_text(block)

        # Switch to Docker
        self._click_tab(block, "Docker")
        docker_content = self._get_visible_body_text(block)

        assert rhel_content != docker_content, \
            "Content should change when switching between RHEL and Docker tabs"

        # Switch back to RHEL
        self._click_tab(block, "RHEL, Centos, Alma, Amazon, Oracle")
        rhel_again = self._get_visible_body_text(block)

        assert rhel_again == rhel_content, \
            "Content should be the same when switching back to RHEL"
