import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from core.base_test import BaseTest


@pytest.mark.usefixtures("setup_driver")
class TestOsTabsInstallation(BaseTest):
    """Tests for OS tab switching on the Installation page."""

    INSTALL_URL = "https://manual.manticoresearch.com/Installation/Installation"
    UNIX_QUICK_INSTALLER_TAB = "RHEL, Centos, Alma, Amazon, Oracle, Debian, Ubuntu, Mint, MacOS"

    def _load_installation_page(self):
        """Load the Installation page with tab state reset for test isolation."""
        self.driver.get(self.INSTALL_URL)
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
        self.driver.get(self.INSTALL_URL)
        time.sleep(2)

    def _get_tab_block(self):
        """Find the OS tabs block on the Installation page."""
        self._load_installation_page()

        # Find the lang-sel block that contains the Installation OS tabs.
        blocks = self.driver.find_elements(By.CSS_SELECTOR, "div.lang-sel")
        for block in blocks:
            tabs = block.find_elements(By.CSS_SELECTOR, "li span.lang-text")
            tab_texts = [t.get_attribute("textContent").strip() for t in tabs]
            if (
                any("RHEL" in t for t in tab_texts)
                and "Windows" in tab_texts
                and "Docker" in tab_texts
                and "Kubernetes" in tab_texts
            ):
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
        tabs = block.find_elements(By.CSS_SELECTOR, "li")
        target_tab = None

        for tab in tabs:
            span = tab.find_element(By.CSS_SELECTOR, "span.lang-text")
            if span.get_attribute("textContent").strip() == tab_text:
                target_tab = tab
                break

        if target_tab is None:
            pytest.fail(f"Tab '{tab_text}' not found")

        # If requested tab is already the active tab, no-op to avoid unnecessary re-clicks.
        if self._get_active_tab_text(block) == tab_text:
            return

        old_content = self._get_visible_body_text(block)

        def tab_switched():
            new_content = self._get_visible_body_text(block)
            return (
                self._get_active_tab_text(block) == tab_text
                and new_content != old_content
                and bool(new_content)
            )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            target_tab,
        )

        # Use native click first; if it silently does not switch tabs, retry with JS.
        try:
            target_tab.click()
        except Exception:
            pass

        wait = WebDriverWait(self.driver, 10)
        try:
            wait.until(lambda _: tab_switched())
            return
        except Exception:
            self.driver.execute_script("arguments[0].click();", target_tab)

        wait.until(lambda _: tab_switched())


    def test_default_tab_is_unix_quick_installer(self):
        """Verify that the combined Unix/macOS tab is active by default."""
        block = self._get_tab_block()

        active = self._get_active_tab_text(block)
        assert active == self.UNIX_QUICK_INSTALLER_TAB, \
            f"Default active tab should be the combined quick-installer tab, got: '{active}'"

        content = self._get_visible_body_text(block)
        assert "curl https://manticoresearch.com | sh" in content, \
            f"Quick installer tab should show curl installer command, got: '{content[:100]}'"
        assert "curl https://manticoresearch.com | sh -s help" in content, \
            f"Quick installer tab should show help command, got: '{content[:100]}'"
        assert "separate packages" in content, \
            f"Quick installer tab should link to separate packages, got: '{content[:100]}'"


    def test_switch_to_windows(self):
        """Verify switching to Windows tab shows Windows installer instructions."""
        block = self._get_tab_block()

        self._click_tab(block, "Windows")

        active = self._get_active_tab_text(block)
        assert "Windows" in active, \
            f"Active tab should be 'Windows', got: '{active}'"

        content = self._get_visible_body_text(block)
        assert "Download the Manticore Search Installer" in content, \
            f"Windows tab should show installer instructions, got: '{content[:100]}'"
        assert "preconfigured manticore.conf" in content, \
            f"Windows tab should mention the preconfigured config, got: '{content[:100]}'"


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

        # Explicitly select the combined Unix/macOS quick-installer tab first.
        self._click_tab(block, self.UNIX_QUICK_INSTALLER_TAB)
        quick_installer_content = self._get_visible_body_text(block)

        # Switch to Docker.
        self._click_tab(block, "Docker")
        docker_content = self._get_visible_body_text(block)

        assert quick_installer_content != docker_content, \
            "Content should change when switching between the quick-installer and Docker tabs"

        # Switch back to the quick-installer tab.
        self._click_tab(block, self.UNIX_QUICK_INSTALLER_TAB)
        quick_installer_again = self._get_visible_body_text(block)

        assert quick_installer_again == quick_installer_content, \
            "Content should be the same when switching back to the quick-installer tab"
