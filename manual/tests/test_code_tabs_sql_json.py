import pytest
import time
from selenium.webdriver.common.by import By
from core.base_test import BaseTest

OS_KEYWORDS = [
    'Ubuntu', 'Debian', 'Centos', 'RHEL', 'MacOS',
    'Windows', 'Docker', 'Kubernetes', 'Alma', 'Amazon', 'Oracle', 'Mint',
]


@pytest.mark.usefixtures("setup_driver")
class TestCodeTabsSqlJson(BaseTest):
    """Tests for SQL/HTTP/PHP code tab switching in documentation examples."""

    PAGE_URL = "https://manual.manticoresearch.com/Quick_start_guide"

    def _find_code_tab_blocks(self, tab_names):
        """Find all visible code lang-sel blocks containing specified tab names.

        Returns a list of WebElements. Excludes OS-related tab blocks.
        """
        blocks = self.driver.find_elements(By.CSS_SELECTOR, "div.lang-sel")
        result = []
        for block in blocks:
            example = block.find_element(
                By.XPATH, "./ancestor::div[contains(@class, 'example')]"
            )
            if not example.is_displayed():
                continue
            tabs = block.find_elements(
                By.CSS_SELECTOR, "ul.lang-tabs li span.lang-text"
            )
            tab_texts = [t.get_attribute("textContent").strip() for t in tabs]
            if any(kw in text for kw in OS_KEYWORDS for text in tab_texts):
                continue
            if all(name in tab_texts for name in tab_names):
                result.append(block)
        return result

    def _find_code_tab_block(self, tab_names):
        """Find the first visible code lang-sel block with specified tabs."""
        blocks = self._find_code_tab_blocks(tab_names)
        if not blocks:
            pytest.fail(f"Code tab block with tabs {tab_names} not found")
        return blocks[0]

    def _get_visible_body_text(self, block):
        """Get text of the currently visible example-body."""
        example = block.find_element(
            By.XPATH, "./ancestor::div[contains(@class, 'example')]"
        )
        bodies = example.find_elements(By.CSS_SELECTOR, ".example-body")
        for body in bodies:
            if body.is_displayed():
                return body.text.strip()
        return ""

    def _get_active_tab_text(self, block):
        """Get the text of the currently active tab."""
        active = block.find_element(
            By.CSS_SELECTOR, "li.active span.lang-text"
        )
        return active.get_attribute("textContent").strip()

    def _click_tab(self, block, text):
        """Click a tab by its text content."""
        tabs = block.find_elements(By.CSS_SELECTOR, "ul.lang-tabs li")
        for tab in tabs:
            span = tab.find_element(By.CSS_SELECTOR, "span.lang-text")
            if span.get_attribute("textContent").strip() == text:
                tab.click()
                time.sleep(2)
                return
        pytest.fail(f"Tab '{text}' not found in block")

    def test_default_tab_is_sql(self):
        """Verify that SQL is the default active tab in code examples."""
        self.driver.get(self.PAGE_URL)
        time.sleep(2)

        block = self._find_code_tab_block(["SQL", "HTTP"])
        active = self._get_active_tab_text(block)
        assert active == "SQL", f"Default active tab should be 'SQL', got: '{active}'"

    @pytest.mark.parametrize("tab_name", ["HTTP", "PHP", "Python"])
    def test_switch_to_tab(self, tab_name):
        """Verify switching to a specific tab activates it and shows different content."""
        self.driver.get(self.PAGE_URL)
        time.sleep(2)

        block = self._find_code_tab_block(["SQL", tab_name])

        self._click_tab(block, "SQL")
        sql_content = self._get_visible_body_text(block)

        self._click_tab(block, tab_name)

        active = self._get_active_tab_text(block)
        assert active == tab_name, f"Active tab should be '{tab_name}', got: '{active}'"

        content = self._get_visible_body_text(block)
        assert content, f"{tab_name} tab should have visible content"
        assert content != sql_content, f"{tab_name} content should differ from SQL content"

    def test_tab_content_changes_on_switch(self):
        """Verify that content changes when switching tabs and restores when switching back."""
        self.driver.get(self.PAGE_URL)
        time.sleep(2)

        block = self._find_code_tab_block(["SQL", "HTTP"])

        self._click_tab(block, "SQL")
        sql_content = self._get_visible_body_text(block)

        self._click_tab(block, "HTTP")
        http_content = self._get_visible_body_text(block)

        self._click_tab(block, "SQL")
        sql_again = self._get_visible_body_text(block)

        assert sql_content != http_content, \
            "SQL and HTTP content should be different"
        assert sql_content == sql_again, \
            "SQL content should be the same after switching back"

    def test_global_tab_sync(self):
        """Verify that switching a code tab in one block syncs all code blocks.

        The documentation site syncs tab selection globally — switching to HTTP
        in one block should switch all blocks to HTTP.
        """
        self.driver.get(self.PAGE_URL)
        time.sleep(2)

        code_blocks = self._find_code_tab_blocks(["SQL", "HTTP"])
        if len(code_blocks) < 2:
            pytest.skip("Need at least 2 visible SQL/HTTP code blocks")

        block1, block2 = code_blocks[0], code_blocks[1]

        self._click_tab(block1, "SQL")
        assert self._get_active_tab_text(block1) == "SQL"

        # Switch block1 to HTTP — block2 should sync automatically
        self._click_tab(block1, "HTTP")

        active2 = self._get_active_tab_text(block2)
        assert active2 == "HTTP", \
            f"Tab sync: block2 should also switch to HTTP, got: '{active2}'"
