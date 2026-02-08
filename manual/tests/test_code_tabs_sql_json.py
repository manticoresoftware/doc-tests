import pytest
import time
from selenium.webdriver.common.by import By
from core.base_test import BaseTest


@pytest.mark.usefixtures("setup_driver")
class TestCodeTabsSqlJson(BaseTest):
    """Tests for SQL/HTTP/PHP code tab switching in documentation examples."""

    PAGE_URL = "https://manual.manticoresearch.com/Quick_start_guide"

    def _find_code_tab_block_element(self, tab_names):
        """Find a visible code lang-sel block containing all specified tab names.

        Returns the WebElement directly from JS to avoid index mismatch issues.
        Excludes OS-related tab blocks.
        """
        element = self.driver.execute_script("""
            var targetNames = arguments[0];
            var osKeywords = ['Ubuntu', 'Debian', 'Centos', 'RHEL', 'MacOS',
                              'Windows', 'Docker', 'Kubernetes', 'Alma', 'Amazon', 'Oracle', 'Mint'];
            var blocks = document.querySelectorAll('div.lang-sel');
            for (var i = 0; i < blocks.length; i++) {
                var example = blocks[i].closest('.example');
                if (!example) continue;
                if (getComputedStyle(example).display === 'none') continue;
                // Get tab texts from ul.lang-tabs only (not from select)
                var ul = blocks[i].querySelector('ul.lang-tabs');
                if (!ul) continue;
                var lis = ul.querySelectorAll('li');
                var texts = [];
                for (var j = 0; j < lis.length; j++) {
                    var span = lis[j].querySelector('span.lang-text');
                    var t = span ? span.textContent.trim() : '';
                    if (t) texts.push(t);
                }
                // Skip OS tab blocks
                var isOsBlock = false;
                for (var o = 0; o < osKeywords.length; o++) {
                    for (var t2 = 0; t2 < texts.length; t2++) {
                        if (texts[t2].indexOf(osKeywords[o]) !== -1) {
                            isOsBlock = true; break;
                        }
                    }
                    if (isOsBlock) break;
                }
                if (isOsBlock) continue;
                // Check all target tabs exist
                var allFound = true;
                for (var k = 0; k < targetNames.length; k++) {
                    if (texts.indexOf(targetNames[k]) === -1) {
                        allFound = false; break;
                    }
                }
                if (allFound) return blocks[i];
            }
            return null;
        """, tab_names)

        if element is None:
            pytest.fail(f"Code tab block with tabs {tab_names} not found")
        return element

    def _get_visible_body_text(self, block):
        """Get text of the currently visible example-body."""
        return self.driver.execute_script("""
            var example = arguments[0].closest('.example');
            if (!example) return '';
            var bodies = example.querySelectorAll('.example-body');
            for (var i = 0; i < bodies.length; i++) {
                if (getComputedStyle(bodies[i]).display !== 'none')
                    return bodies[i].textContent.trim();
            }
            return '';
        """, block)

    def _get_active_tab_text(self, block):
        """Get the text of the currently active tab."""
        return self.driver.execute_script("""
            var ul = arguments[0].querySelector('ul.lang-tabs');
            if (!ul) return '';
            var active = ul.querySelector('li.active span.lang-text');
            return active ? active.textContent.trim() : '';
        """, block)

    def _click_tab(self, block, text):
        """Click a tab by text via JS (works even if tab is hidden by CSS overflow)."""
        clicked = self.driver.execute_script("""
            var block = arguments[0];
            var targetText = arguments[1];
            block.scrollIntoView({block: 'center'});
            var ul = block.querySelector('ul.lang-tabs');
            if (!ul) return false;
            var lis = ul.querySelectorAll('li');
            for (var i = 0; i < lis.length; i++) {
                var span = lis[i].querySelector('span.lang-text');
                if (span && span.textContent.trim() === targetText) {
                    lis[i].click();
                    return true;
                }
            }
            return false;
        """, block, text)
        if not clicked:
            pytest.fail(f"Tab '{text}' not found in block")
        time.sleep(2)

    def test_default_tab_is_sql(self):
        """Verify that SQL is the default active tab in code examples."""
        self.driver.get(self.PAGE_URL)
        time.sleep(2)

        block = self._find_code_tab_block_element(["SQL", "HTTP"])
        active = self._get_active_tab_text(block)
        assert active == "SQL", f"Default active tab should be 'SQL', got: '{active}'"

        self.take_screenshot("code_tab_default")

    def test_switch_sql_to_http(self):
        """Verify switching from SQL to HTTP tab changes code content."""
        self.driver.get(self.PAGE_URL)
        time.sleep(2)

        block = self._find_code_tab_block_element(["SQL", "HTTP"])

        # Ensure SQL is active
        self._click_tab(block, "SQL")
        sql_content = self._get_visible_body_text(block)
        assert sql_content, "SQL tab should have visible content"

        # Switch to HTTP
        self._click_tab(block, "HTTP")

        active = self._get_active_tab_text(block)
        assert active == "HTTP", f"Active tab should be 'HTTP', got: '{active}'"

        http_content = self._get_visible_body_text(block)
        assert http_content, "HTTP tab should have visible content"
        assert http_content != sql_content, "HTTP content should differ from SQL content"

        self.take_screenshot("code_tab_http")

    def test_switch_to_php(self):
        """Verify switching to PHP tab shows PHP code."""
        self.driver.get(self.PAGE_URL)
        time.sleep(2)

        block = self._find_code_tab_block_element(["SQL", "PHP"])
        self._click_tab(block, "PHP")

        active = self._get_active_tab_text(block)
        assert active == "PHP", f"Active tab should be 'PHP', got: '{active}'"

        content = self._get_visible_body_text(block)
        assert "php" in content.lower() or "$" in content or "require" in content, \
            f"PHP tab should show PHP code, got: '{content[:100]}'"

        self.take_screenshot("code_tab_php")

    def test_switch_to_python(self):
        """Verify switching to Python tab shows Python code."""
        self.driver.get(self.PAGE_URL)
        time.sleep(2)

        block = self._find_code_tab_block_element(["SQL", "Python"])
        self._click_tab(block, "Python")

        active = self._get_active_tab_text(block)
        assert active == "Python", f"Active tab should be 'Python', got: '{active}'"

        content = self._get_visible_body_text(block)
        assert "import" in content or "manticoresearch" in content, \
            f"Python tab should show Python code, got: '{content[:100]}'"

        self.take_screenshot("code_tab_python")

    def test_tab_content_changes_on_switch(self):
        """Verify that content actually changes when switching between tabs."""
        self.driver.get(self.PAGE_URL)
        time.sleep(2)

        block = self._find_code_tab_block_element(["SQL", "HTTP"])

        # Explicitly set to SQL first
        self._click_tab(block, "SQL")

        # Re-fetch block after global tab sync (page may re-render)
        block = self._find_code_tab_block_element(["SQL", "HTTP"])
        sql_content = self._get_visible_body_text(block)

        # Switch to HTTP
        self._click_tab(block, "HTTP")
        block = self._find_code_tab_block_element(["SQL", "HTTP"])
        http_content = self._get_visible_body_text(block)

        # Switch back to SQL
        self._click_tab(block, "SQL")
        block = self._find_code_tab_block_element(["SQL", "HTTP"])
        sql_again = self._get_visible_body_text(block)

        assert sql_content != http_content, \
            "SQL and HTTP content should be different"
        assert sql_content == sql_again, \
            "SQL content should be the same after switching back"

    def test_global_tab_sync(self):
        """Verify that switching a code tab syncs across all code blocks.

        The documentation site intentionally syncs tab selection globally
        (e.g. switching to HTTP in one block switches all blocks to HTTP).
        """
        self.driver.get(self.PAGE_URL)
        time.sleep(2)

        # Find two code blocks that both have SQL and HTTP
        elements = self.driver.execute_script("""
            var osKeywords = ['Ubuntu', 'Debian', 'Centos', 'RHEL', 'MacOS',
                              'Windows', 'Docker', 'Kubernetes', 'Alma', 'Amazon', 'Oracle', 'Mint'];
            var blocks = document.querySelectorAll('div.lang-sel');
            var found = [];
            for (var i = 0; i < blocks.length; i++) {
                var example = blocks[i].closest('.example');
                if (!example || getComputedStyle(example).display === 'none') continue;
                var ul = blocks[i].querySelector('ul.lang-tabs');
                if (!ul) continue;
                var lis = ul.querySelectorAll('li');
                var texts = [];
                for (var j = 0; j < lis.length; j++) {
                    var span = lis[j].querySelector('span.lang-text');
                    var t = span ? span.textContent.trim() : '';
                    if (t) texts.push(t);
                }
                var isOs = texts.some(function(t) {
                    return osKeywords.some(function(kw) { return t.indexOf(kw) !== -1; });
                });
                if (isOs) continue;
                if (texts.indexOf('SQL') !== -1 && texts.indexOf('HTTP') !== -1)
                    found.push(blocks[i]);
                if (found.length >= 2) break;
            }
            return found;
        """)

        if len(elements) < 2:
            pytest.skip("Need at least 2 visible SQL/HTTP code blocks")

        block1, block2 = elements[0], elements[1]

        # Ensure both on SQL
        self._click_tab(block1, "SQL")
        assert self._get_active_tab_text(block1) == "SQL"

        # Switch block1 to HTTP
        self._click_tab(block1, "HTTP")

        # Block2 should also switch to HTTP (global sync)
        active2 = self._get_active_tab_text(block2)
        assert active2 == "HTTP", \
            f"Tab sync: Block2 should also switch to HTTP, got: '{active2}'"
