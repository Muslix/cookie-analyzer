import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cookie_analyzer.handlers.cookie_handler import CookieHandler

class TestCookieHandler(unittest.TestCase):
    """Tests für den CookieHandler."""
    
    def setUp(self):
        """Test-Setup."""
        self.handler = CookieHandler()
        
        # Mock-Cookies für Tests
        self.mock_cookies = [
            {"name": "sessionid", "domain": "example.com", "value": "123"},
            {"name": "_ga", "domain": "example.com", "value": "GA1.2.123.456"},
            {"name": "_fbp", "domain": "example.com", "value": "fb.1.123.456"},
            {"name": "unknown", "domain": "example.com", "value": "test"}
        ]
        
        # Mock-Cookie-Datenbank
        self.mock_database = [
            {
                "Cookie Name": "sessionid", 
                "Description": "Session ID", 
                "Category": "Necessary"
            },
            {
                "Cookie Name": "_ga", 
                "Description": "Google Analytics", 
                "Category": "Analytics"
            }
        ]
        
    def test_classify_cookies(self):
        """Test für die Cookie-Klassifikation."""
        # Patche die find_cookie_info-Funktion, um sicherzustellen, dass wir die Datenbank verwenden
        with patch('cookie_analyzer.database.handler.find_cookie_info', side_effect=lambda name, db: next(
            (cookie for cookie in db if cookie["Cookie Name"] == name), 
            {"Description": "Keine Beschreibung verfügbar.", "Category": "Unknown"}
        )):
            classified = self.handler.classify_cookies(self.mock_cookies, self.mock_database)
            
            # Überprüfe die Ergebnisse
            self.assertEqual(len(classified["Strictly Necessary"]), 1)
            self.assertEqual(len(classified["Performance"]), 1)
            self.assertEqual(len(classified["Targeting"]), 1)
            self.assertEqual(len(classified["Other"]), 1)
            
            # Überprüfe die spezifischen Cookies in jeder Kategorie
            self.assertEqual(classified["Strictly Necessary"][0]["name"], "sessionid")
            self.assertEqual(classified["Performance"][0]["name"], "_ga")
            self.assertEqual(classified["Targeting"][0]["name"], "_fbp")
            self.assertEqual(classified["Other"][0]["name"], "unknown")
            
    def test_remove_duplicates(self):
        """Test für das Entfernen doppelter Cookies."""
        # Erstelle Cookies mit Duplikaten
        cookies_with_duplicates = [
            {"name": "test1", "domain": "example.com", "value": "1"},
            {"name": "test1", "domain": "example.com", "value": "2"},  # Duplikat
            {"name": "test2", "domain": "example.com", "value": "3"},
            {"name": "test1", "domain": "sub.example.com", "value": "4"}  # Kein Duplikat (andere Domain)
        ]
        
        # Entferne Duplikate
        unique_cookies = self.handler.remove_duplicates(cookies_with_duplicates)
        
        # Überprüfe die Ergebnisse
        self.assertEqual(len(unique_cookies), 3)
        
        # Stelle sicher, dass das erste Vorkommen beibehalten wird
        test1_cookies = [c for c in unique_cookies if c["name"] == "test1" and c["domain"] == "example.com"]
        self.assertEqual(len(test1_cookies), 1)
        self.assertEqual(test1_cookies[0]["value"], "1")
    
    def test_get_consent_categories(self):
        """Test für die Ermittlung der Consent-Kategorien."""
        with patch.object(self.handler, 'classify_cookies', return_value={
            "Strictly Necessary": [{"name": "session"}, {"name": "csrf"}],
            "Performance": [{"name": "_ga"}],
            "Targeting": [{"name": "_fbp"}, {"name": "ads"}],
            "Other": []
        }):
            categories = self.handler.get_consent_categories(self.mock_cookies)
            
            # Überprüfe die Ergebnisse
            self.assertEqual(categories["Strictly Necessary"], 2)
            self.assertEqual(categories["Performance"], 1)
            self.assertEqual(categories["Targeting"], 2)
            self.assertEqual(categories["Other"], 0)
    
    def test_identify_fingerprinting(self):
        """Test für die Erkennung von Fingerprinting-Techniken."""
        cookies = [
            {"name": "fingerprint", "domain": "example.com", "value": "abc123"},
            {"name": "visitorid", "domain": "example.com", "value": "long-random-value-0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"}
        ]
        
        local_storage = {
            "https://example.com": {
                "localStorage": {
                    "canvas_fingerprint": "base64-data-very-long-string",
                    "font_detection": "Arial,Helvetica,Times"
                }
            }
        }
        
        fingerprinting = self.handler.identify_fingerprinting(cookies, local_storage)
        
        # Überprüfe die Ergebnisse
        self.assertTrue(fingerprinting["persistent_identifiers"])
        self.assertTrue(fingerprinting["canvas_fingerprinting"])
        self.assertTrue(fingerprinting["font_fingerprinting"])
        self.assertFalse(fingerprinting["webrtc_fingerprinting"])

if __name__ == '__main__':
    unittest.main()