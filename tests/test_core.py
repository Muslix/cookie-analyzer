import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cookie_analyzer.core import is_internal_link, remove_duplicate_cookies
from cookie_analyzer.cookie_handler import classify_cookies

class TestCore(unittest.TestCase):
    def test_is_internal_link(self):
        """Test, ob interne Links korrekt erkannt werden."""
        self.assertTrue(is_internal_link("https://example.com", "https://example.com/page1"))
        self.assertTrue(is_internal_link("https://example.com/page1", "https://example.com/page2"))
        self.assertTrue(is_internal_link("https://example.com", "https://www.example.com"))
        self.assertFalse(is_internal_link("https://example.com", "https://another-site.com"))
        
    def test_remove_duplicate_cookies(self):
        """Test, ob doppelte Cookies korrekt entfernt werden."""
        cookies = [
            {"name": "test1", "domain": "example.com", "path": "/", "value": "value1"},
            {"name": "test1", "domain": "example.com", "path": "/", "value": "value2"},  # Duplikat
            {"name": "test2", "domain": "example.com", "path": "/", "value": "value3"},
            {"name": "test1", "domain": "sub.example.com", "path": "/", "value": "value4"}  # Anderer Domain, kein Duplikat
        ]
        
        unique_cookies = remove_duplicate_cookies(cookies)
        self.assertEqual(len(unique_cookies), 3)
        
    def test_classify_cookies(self):
        """Test, ob Cookies korrekt klassifiziert werden."""
        cookies = [
            {"name": "cookie1", "domain": "example.com", "path": "/"},
            {"name": "cookie2", "domain": "example.com", "path": "/"},
            {"name": "cookie3", "domain": "example.com", "path": "/"}
        ]
        
        cookie_database = [
            {"ID": "1", "Vendor": "Test", "Category": "Functional", "Cookie Name": "cookie1", 
             "Description": "Test cookie", "Wildcard match": False},
            {"ID": "2", "Vendor": "Test", "Category": "Analytics", "Cookie Name": "cookie2", 
             "Description": "Analytics cookie", "Wildcard match": False}
        ]
        
        classified = classify_cookies(cookies, cookie_database)
        
        self.assertEqual(len(classified["Strictly Necessary"]), 1)
        self.assertEqual(len(classified["Performance"]), 1)
        self.assertEqual(len(classified["Other"]), 1)
        
    @patch('cookie_analyzer.core.sync_playwright')
    def test_scan_single_page(self, mock_playwright):
        """Mock-Test für scan_single_page."""
        # Hier würde man den Playwright-Browser und die Cookies mocken
        # Dies ist ein Platzhalter für einen umfassenderen Test
        pass

if __name__ == '__main__':
    unittest.main()