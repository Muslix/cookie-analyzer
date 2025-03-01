import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import tempfile
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cookie_analyzer.database.handler import DatabaseHandler
from cookie_analyzer.utils.config import Config

class TestDatabaseHandler(unittest.TestCase):
    """Tests für den DatabaseHandler."""
    
    def setUp(self):
        """Test-Setup."""
        self.handler = DatabaseHandler()
        self.mock_csv_content = """ID,Parent Organization,Vendor,Cookie Name,Value,Description,Expiration,Vendor Website,Privacy Policy,Wildcard match,Category
1,Test Org,Test Vendor,cookie1,test,Test cookie,30 days,http://example.com,http://example.com/privacy,1,Functional
2,Test Org,Test Vendor,cookie2,test2,Test cookie 2,1 year,http://example.com,http://example.com/privacy,0,Analytics
"""

    @patch('builtins.open', new_callable=mock_open)
    def test_load_database(self, mock_file):
        """Test für das Laden der Cookie-Datenbank."""
        mock_file.return_value.__enter__.return_value.read.return_value = self.mock_csv_content
        
        # Erstelle einen temporären Dateinamen
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_name = temp.name
        
        # Schreibe Testdaten in die temporäre Datei
        with open(temp_name, 'w') as f:
            f.write(self.mock_csv_content)
        
        try:
            # Lade die Datenbank aus der temporären Datei
            db = self.handler.load_database(temp_name)
            
            # Überprüfe die Ergebnisse
            self.assertEqual(len(db), 2)
            self.assertEqual(db[0]["Cookie Name"], "cookie1")
            self.assertEqual(db[0]["Category"], "Functional")
            self.assertTrue(db[0]["Wildcard match"])
            self.assertEqual(db[1]["Cookie Name"], "cookie2")
            self.assertEqual(db[1]["Category"], "Analytics")
            self.assertFalse(db[1]["Wildcard match"])
        finally:
            # Lösche die temporäre Datei
            os.unlink(temp_name)
    
    def test_find_cookie_info(self):
        """Test für das Finden von Cookie-Informationen."""
        mock_db = [
            {
                "Cookie Name": "cookie1",
                "Description": "Test cookie 1",
                "Category": "Functional",
                "Wildcard match": False
            },
            {
                "Cookie Name": "cookie*",
                "Description": "Test cookie wildcard",
                "Category": "Analytics",
                "Wildcard match": True
            },
            {
                "Cookie Name": "_ga",
                "Description": "Google Analytics",
                "Category": "Analytics",
                "Wildcard match": False
            }
        ]
        
        # Test für exakte Übereinstimmung
        result = self.handler.find_cookie_info("cookie1", mock_db)
        self.assertEqual(result["Description"], "Test cookie 1")
        self.assertEqual(result["Category"], "Functional")
        
        # Test für Wildcard-Übereinstimmung
        result = self.handler.find_cookie_info("cookie123", mock_db)
        self.assertEqual(result["Description"], "Test cookie wildcard")
        self.assertEqual(result["Category"], "Analytics")
        
        # Test für nicht gefundenen Cookie
        result = self.handler.find_cookie_info("unknown_cookie", mock_db)
        self.assertEqual(result["Description"], "Keine Beschreibung verfügbar.")
        self.assertEqual(result["Category"], "Unknown")
    
    @patch('requests.get')
    def test_update_database(self, mock_get):
        """Test für die Datenbankaktualisierung."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = self.mock_csv_content.encode('utf-8')
        mock_get.return_value = mock_response
        
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_name = temp.name
        
        try:
            # Mock das Laden der Datenbank
            with patch.object(self.handler, 'load_database', return_value=[{"Cookie Name": "test"}]):
                result = self.handler.update_database(temp_name, "https://example.com/db.csv")
                self.assertTrue(result)
                mock_get.assert_called_once_with("https://example.com/db.csv")
        finally:
            # Lösche die temporäre Datei
            if os.path.exists(temp_name):
                os.unlink(temp_name)

if __name__ == '__main__':
    unittest.main()