"""
Tests für die Kernfunktionalität des Cookie-Analyzers.
"""

import pytest
from unittest.mock import patch, MagicMock

from cookie_analyzer.core.analyzer import CookieAnalyzer, crawl_website
from cookie_analyzer.services.crawler_factory import CrawlerType


@pytest.fixture
def mock_analyzer_dependencies():
    """Fixture zum Mocking aller Abhängigkeiten des CookieAnalyzers."""
    with patch('cookie_analyzer.core.analyzer.get_database_service') as mock_db_service, \
         patch('cookie_analyzer.core.analyzer.get_cookie_classifier_service') as mock_classifier_service, \
         patch('cookie_analyzer.core.analyzer.get_crawler_service') as mock_crawler_service:
            
        # Mock für den Datenbank-Service
        mock_db = MagicMock()
        mock_db.load_database.return_value = [
            {"name": "test_cookie", "category": "Analytics"},
            {"name": "_ga", "category": "Marketing"}
        ]
        mock_db_service.return_value = mock_db
        
        # Mock für den Cookie-Classifier
        mock_classifier = MagicMock()
        mock_classifier.remove_duplicates.side_effect = lambda cookies: cookies
        mock_classifier.classify_cookies.return_value = {
            "Analytics": [{"name": "test_cookie"}],
            "Marketing": [{"name": "_ga"}]
        }
        mock_classifier_service.return_value = mock_classifier
        
        # Mock für den Crawler-Service
        mock_crawler = MagicMock()
        mock_crawler.crawl.return_value = (
            [{"name": "test_cookie"}, {"name": "_ga"}],
            {"https://example.com": {"localStorage": {}, "sessionStorage": {}}}
        )
        mock_crawler.scan_single_page.return_value = (
            [{"name": "test_cookie_pre"}],
            {"https://example.com": {"localStorage": {}, "sessionStorage": {}}},
            [{"name": "test_cookie_post"}, {"name": "_ga_post"}],
            {"https://example.com": {"localStorage": {"consent": "true"}, "sessionStorage": {}}}
        )
        mock_crawler_service.return_value = mock_crawler
        
        yield mock_db_service, mock_classifier_service, mock_crawler_service, mock_crawler


def test_cookie_analyzer_init():
    """Testet die Initialisierung des CookieAnalyzers."""
    analyzer = CookieAnalyzer(
        crawler_type=CrawlerType.SELENIUM,
        interact_with_consent=False,
        headless=False,
        user_data_dir="/path/to/profile"
    )
    
    assert analyzer.crawler_type == CrawlerType.SELENIUM
    assert analyzer.interact_with_consent is False
    assert analyzer.headless is False
    assert analyzer.user_data_dir == "/path/to/profile"


def test_analyze_website(mock_analyzer_dependencies):
    """Testet die analyze_website-Methode des CookieAnalyzers."""
    mock_db_service, mock_classifier_service, mock_crawler_service, mock_crawler = mock_analyzer_dependencies
    
    analyzer = CookieAnalyzer(
        crawler_type=CrawlerType.PLAYWRIGHT,
        interact_with_consent=True,
        headless=True
    )
    
    # Test mit Standard-Parametern
    classified_cookies, storage_data = analyzer.analyze_website(
        url="https://example.com",
        max_pages=1
    )
    
    # Überprüfe, ob die Methoden der Mocks korrekt aufgerufen wurden
    mock_db_service.return_value.load_database.assert_called_once()
    mock_crawler_service.assert_called_once_with(
        start_url="https://example.com",
        max_pages=1,
        crawler_type=CrawlerType.PLAYWRIGHT,
        interact_with_consent=True,
        headless=True,
        user_data_dir=None
    )
    mock_crawler.crawl.assert_called_once()
    mock_classifier_service.return_value.remove_duplicates.assert_called_once()
    mock_classifier_service.return_value.classify_cookies.assert_called_once()
    
    # Überprüfe die Rückgabewerte
    assert classified_cookies == {
        "Analytics": [{"name": "test_cookie"}],
        "Marketing": [{"name": "_ga"}]
    }
    assert storage_data == {"https://example.com": {"localStorage": {}, "sessionStorage": {}}}


def test_analyze_website_with_consent_stages(mock_analyzer_dependencies):
    """Testet die analyze_website_with_consent_stages-Methode des CookieAnalyzers."""
    mock_db_service, mock_classifier_service, mock_crawler_service, mock_crawler = mock_analyzer_dependencies
    
    analyzer = CookieAnalyzer(
        crawler_type=CrawlerType.SELENIUM,
        interact_with_consent=True,
        headless=True
    )
    
    # Test mit zweistufiger Analyse
    pre_cookies, pre_storage, post_cookies, post_storage = analyzer.analyze_website_with_consent_stages(
        url="https://example.com",
        max_pages=1
    )
    
    # Überprüfe, ob die Methoden der Mocks korrekt aufgerufen wurden
    mock_db_service.return_value.load_database.assert_called_once()
    mock_crawler_service.assert_called_once_with(
        start_url="https://example.com",
        max_pages=1,
        crawler_type=CrawlerType.SELENIUM,
        interact_with_consent=True,
        headless=True,
        user_data_dir=None
    )
    mock_crawler.scan_single_page.assert_called_once()
    
    # Der Classifier wird dreimal aufgerufen: zweimal für die vorhandenen Cookies und einmal für neue Cookies
    assert mock_classifier_service.return_value.classify_cookies.call_count >= 2
    
    # Überprüfe die Phasen-Eigenschaften in den Storage-Daten
    assert pre_storage["https://example.com"].get("phase") == "pre-consent"
    assert post_storage["https://example.com"].get("phase") == "post-consent"


def test_crawl_website_function(mock_analyzer_dependencies):
    """Testet die crawl_website-Funktion."""
    mock_db_service, mock_classifier_service, mock_crawler_service, mock_crawler = mock_analyzer_dependencies
    
    # Test mit Standard-Parametern
    cookie_database = [{"name": "test_cookie", "category": "Analytics"}]
    classified_cookies, storage_data = crawl_website(
        url="https://example.com",
        max_pages=2,
        cookie_database=cookie_database,
        crawler_type=CrawlerType.SELENIUM,
        interact_with_consent=False,
        headless=True
    )
    
    # Überprüfe, ob die Methoden der Mocks korrekt aufgerufen wurden
    mock_crawler_service.assert_called_once_with(
        start_url="https://example.com",
        max_pages=2,
        crawler_type=CrawlerType.SELENIUM,
        interact_with_consent=False,
        headless=True,
        user_data_dir=None
    )
    mock_crawler.crawl.assert_called_once()
    
    # Überprüfe die Rückgabewerte
    assert classified_cookies == {
        "Analytics": [{"name": "test_cookie"}],
        "Marketing": [{"name": "_ga"}]
    }
    assert storage_data == {"https://example.com": {"localStorage": {}, "sessionStorage": {}}}