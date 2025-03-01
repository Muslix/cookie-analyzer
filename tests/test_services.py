import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cookie_analyzer.services.provider import ServiceProvider
from cookie_analyzer.services.initializer import initialize_services, get_database_service, get_cookie_classifier_service
from cookie_analyzer.services.crawler_factory import CrawlerType, get_crawler_service
from cookie_analyzer.services.service_interfaces import CookieDatabaseService, CookieClassifierService, CrawlerService

class TestServiceProvider(unittest.TestCase):
    """Tests für den ServiceProvider."""

    def setUp(self):
        """Setze den ServiceProvider zurück vor jedem Test."""
        ServiceProvider._services = {}

    def test_register_and_get(self):
        """Test für die Registrierung und das Abrufen von Services."""
        # Erstelle einen Mock-Service
        mock_service = MagicMock()
        
        # Registriere den Service
        ServiceProvider.register("test_service", mock_service)
        
        # Rufe den Service ab
        retrieved_service = ServiceProvider.get("test_service")
        
        # Überprüfe, dass es derselbe Service ist
        self.assertIs(retrieved_service, mock_service)

    def test_get_nonexistent_service(self):
        """Test für das Abrufen eines nicht existierenden Services."""
        with self.assertRaises(KeyError):
            ServiceProvider.get("nonexistent_service")

class TestServiceInitializer(unittest.TestCase):
    """Tests für den ServiceInitializer."""

    def setUp(self):
        """Setze den ServiceProvider zurück vor jedem Test."""
        ServiceProvider._services = {}

    @patch('cookie_analyzer.database.handler.DatabaseHandler')
    @patch('cookie_analyzer.handlers.cookie_handler.CookieHandler')
    def test_initialize_services(self, mock_cookie_handler, mock_database_handler):
        """Test für die Initialisierung von Services."""
        # Mock-Instanzen erstellen
        mock_db_instance = mock_database_handler.return_value
        mock_cookie_handler_instance = mock_cookie_handler.return_value
        
        # Services initialisieren
        initialize_services()
        
        # Überprüfe, dass die Services registriert wurden
        self.assertIs(ServiceProvider._services["database"], mock_db_instance)
        self.assertIs(ServiceProvider._services["cookie_classifier"], mock_cookie_handler_instance)
    
    @patch('cookie_analyzer.services.provider.ServiceProvider.get')
    def test_get_database_service(self, mock_get):
        """Test für das Abrufen des DatabaseService."""
        # Mock-Service erstellen
        mock_service = MagicMock(spec=CookieDatabaseService)
        mock_get.return_value = mock_service
        
        # Service abrufen
        service = get_database_service()
        
        # Überprüfen, dass der richtige Service angefordert wurde
        mock_get.assert_called_once_with("database")
        self.assertIs(service, mock_service)
    
    @patch('cookie_analyzer.services.provider.ServiceProvider.get')
    def test_get_cookie_classifier_service(self, mock_get):
        """Test für das Abrufen des CookieClassifierService."""
        # Mock-Service erstellen
        mock_service = MagicMock(spec=CookieClassifierService)
        mock_get.return_value = mock_service
        
        # Service abrufen
        service = get_cookie_classifier_service()
        
        # Überprüfen, dass der richtige Service angefordert wurde
        mock_get.assert_called_once_with("cookie_classifier")
        self.assertIs(service, mock_service)

class TestCrawlerFactory(unittest.TestCase):
    """Tests für die CrawlerFactory."""
    
    @patch('cookie_analyzer.crawler.cookie_crawler.CookieCrawler')
    @patch('cookie_analyzer.crawler.async_crawler.AsyncCookieCrawler')
    @patch('cookie_analyzer.crawler.selenium_crawler.SeleniumCookieCrawler')
    def test_get_crawler_service(self, mock_selenium, mock_async, mock_standard):
        """Test für das Erstellen von Crawler-Instanzen."""
        # Mock-Instanzen erstellen
        mock_standard_instance = mock_standard.return_value
        mock_async_instance = mock_async.return_value
        mock_selenium_instance = mock_selenium.return_value
        
        # Teste die verschiedenen Crawler-Typen
        
        # Standard Playwright Crawler
        crawler = get_crawler_service("https://example.com", crawler_type=CrawlerType.PLAYWRIGHT)
        mock_standard.assert_called_once()
        self.assertIs(crawler, mock_standard_instance)
        
        # Async Playwright Crawler
        crawler = get_crawler_service("https://example.com", crawler_type=CrawlerType.PLAYWRIGHT_ASYNC)
        mock_async.assert_called_once()
        self.assertIs(crawler, mock_async_instance)
        
        # Selenium Crawler
        crawler = get_crawler_service("https://example.com", crawler_type=CrawlerType.SELENIUM)
        mock_selenium.assert_called_once()
        self.assertIs(crawler, mock_selenium_instance)

if __name__ == '__main__':
    unittest.main()