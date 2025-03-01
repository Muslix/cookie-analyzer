import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cookie_analyzer.core.analyzer import CookieAnalyzer, crawl_website, crawl_website_async
from cookie_analyzer.services.crawler_factory import CrawlerType

class TestCookieAnalyzer(unittest.TestCase):
    """Tests für den CookieAnalyzer."""
    
    @patch('cookie_analyzer.services.initializer.get_database_service')
    @patch('cookie_analyzer.services.initializer.get_cookie_classifier_service')
    @patch('cookie_analyzer.core.analyzer.crawl_website')
    def test_analyze_website(self, mock_crawl, mock_cookie_classifier, mock_db_service):
        """Test für die analyze_website Methode."""
        # Mock-Rückgabewerte und -Services konfigurieren
        mock_db_service.return_value.load_database.return_value = [{"Cookie Name": "test"}]
        mock_crawl.return_value = ({"classified": "cookies"}, {"storage": "data"})
        
        # CookieAnalyzer erstellen und die Website analysieren
        analyzer = CookieAnalyzer(CrawlerType.PLAYWRIGHT)
        result = analyzer.analyze_website("https://example.com", 1, "database.csv")
        
        # Überprüfen, dass die richtigen Methoden aufgerufen wurden
        mock_db_service.return_value.load_database.assert_called_once_with("database.csv")
        mock_crawl.assert_called_once()
        
        # Überprüfen des Ergebnisses
        self.assertEqual(result, ({"classified": "cookies"}, {"storage": "data"}))
    
    @patch('cookie_analyzer.services.initializer.get_database_service')
    @patch('cookie_analyzer.services.initializer.get_cookie_classifier_service')
    @patch('cookie_analyzer.core.analyzer.asyncio.run')
    def test_analyze_website_async(self, mock_asyncio_run, mock_cookie_classifier, mock_db_service):
        """Test für die asynchrone Website-Analyse."""
        # Mock-Rückgabewerte und -Services konfigurieren
        mock_db_service.return_value.load_database.return_value = [{"Cookie Name": "test"}]
        mock_asyncio_run.return_value = ({"classified": "cookies"}, {"storage": "data"})
        
        # CookieAnalyzer erstellen und die Website asynchron analysieren
        analyzer = CookieAnalyzer(CrawlerType.PLAYWRIGHT_ASYNC)
        result = analyzer.analyze_website("https://example.com", 1, "database.csv")
        
        # Überprüfen, dass die richtigen Methoden aufgerufen wurden
        mock_db_service.return_value.load_database.assert_called_once_with("database.csv")
        mock_asyncio_run.assert_called_once()
        
        # Überprüfen des Ergebnisses
        self.assertEqual(result, ({"classified": "cookies"}, {"storage": "data"}))
    
    @patch('cookie_analyzer.services.crawler_factory.get_crawler_service')
    @patch('cookie_analyzer.services.initializer.get_cookie_classifier_service')
    def test_crawl_website(self, mock_cookie_classifier, mock_get_crawler):
        """Test für die crawl_website Funktion."""
        # Mock-Crawler konfigurieren
        mock_crawler = MagicMock()
        mock_crawler.crawl.return_value = ([{"name": "test_cookie"}], {"local_storage": "data"})
        mock_get_crawler.return_value = mock_crawler
        
        # Mock-Cookie-Classifier konfigurieren
        mock_cookie_classifier.return_value.remove_duplicates.return_value = [{"name": "test_cookie"}]
        mock_cookie_classifier.return_value.classify_cookies.return_value = {"Strictly Necessary": [{"name": "test_cookie"}]}
        
        # Website crawlen
        result = crawl_website(
            "https://example.com", 
            max_pages=2, 
            cookie_database=[],
            crawler_type=CrawlerType.PLAYWRIGHT, 
            interact_with_consent=True, 
            headless=True
        )
        
        # Überprüfen, dass die richtigen Methoden aufgerufen wurden
        mock_get_crawler.assert_called_once()
        mock_crawler.crawl.assert_called_once()
        mock_cookie_classifier.return_value.remove_duplicates.assert_called_once()
        mock_cookie_classifier.return_value.classify_cookies.assert_called_once()
        
        # Überprüfen des Ergebnisses
        self.assertEqual(result, ({"Strictly Necessary": [{"name": "test_cookie"}]}, {"local_storage": "data"}))
    
    @patch('cookie_analyzer.services.crawler_factory.get_crawler_service')
    @patch('cookie_analyzer.services.initializer.get_cookie_classifier_service')
    async def test_crawl_website_async(self, mock_cookie_classifier, mock_get_crawler):
        """Test für die crawl_website_async Funktion."""
        # Mock-Crawler konfigurieren
        mock_crawler = MagicMock()
        mock_crawler.crawl_async = MagicMock()
        mock_crawler.crawl_async.return_value = ([{"name": "test_cookie"}], {"local_storage": "data"})
        mock_get_crawler.return_value = mock_crawler
        
        # Mock-Cookie-Classifier konfigurieren
        mock_cookie_classifier.return_value.remove_duplicates.return_value = [{"name": "test_cookie"}]
        mock_cookie_classifier.return_value.classify_cookies.return_value = {"Strictly Necessary": [{"name": "test_cookie"}]}
        
        # Website asynchron crawlen
        result = await crawl_website_async("https://example.com", max_pages=2, cookie_database=[])
        
        # Überprüfen, dass die richtigen Methoden aufgerufen wurden
        mock_get_crawler.assert_called_once()
        mock_crawler.crawl_async.assert_called_once()
        mock_cookie_classifier.return_value.remove_duplicates.assert_called_once()
        mock_cookie_classifier.return_value.classify_cookies.assert_called_once()
        
        # Überprüfen des Ergebnisses
        self.assertEqual(result, ({"Strictly Necessary": [{"name": "test_cookie"}]}, {"local_storage": "data"}))

# Dieser Test wird direkt von unittest.main ausgeführt, wenn die Datei direkt ausgeführt wird
if __name__ == '__main__':
    unittest.main()