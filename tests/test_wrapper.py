"""
Tests für die Wrapper-Funktionen, die als öffentliche API des Cookie-Analyzers dienen.
"""

import pytest
from unittest.mock import patch, MagicMock
from cookie_analyzer.interface.wrapper import analyze_website, analyze_website_with_consent_stages
from cookie_analyzer.services.crawler_factory import CrawlerType


@pytest.fixture
def mock_cookie_analyzer():
    """Fixture zum Mocking des CookieAnalyzers."""
    with patch('cookie_analyzer.interface.wrapper.CookieAnalyzer') as mock_analyzer_class, \
         patch('cookie_analyzer.interface.wrapper.initialize_services') as mock_init_services:
        
        # Mock für die CookieAnalyzer-Instanz
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_website.return_value = (
            {"Analytics": [{"name": "test_cookie"}]},
            {"https://example.com": {"localStorage": {}, "sessionStorage": {}}}
        )
        mock_analyzer.analyze_website_with_consent_stages.return_value = (
            {"Analytics": [{"name": "test_cookie_pre"}]},
            {"https://example.com": {"localStorage": {}, "phase": "pre-consent"}},
            {"Analytics": [{"name": "test_cookie_post"}], "Marketing": [{"name": "_ga"}]},
            {"https://example.com": {"localStorage": {"consent": "true"}, "phase": "post-consent"}}
        )
        mock_analyzer_class.return_value = mock_analyzer
        
        yield mock_analyzer_class, mock_analyzer, mock_init_services


def test_analyze_website_wrapper(mock_cookie_analyzer):
    """Testet die analyze_website-Wrapper-Funktion."""
    mock_analyzer_class, mock_analyzer, mock_init_services = mock_cookie_analyzer
    
    # Test mit Standard-Parametern
    classified_cookies, storage_data = analyze_website(
        url="https://example.com",
        max_pages=3,
        database_path="/path/to/database.csv",
        use_async=False,
        use_selenium=True,
        interact_with_consent=True,
        headless=False,
        user_data_dir="/path/to/profile"
    )
    
    # Überprüfe, ob die Services initialisiert wurden
    mock_init_services.assert_called_once()
    
    # Überprüfe, ob die CookieAnalyzer-Klasse korrekt instanziiert wurde
    mock_analyzer_class.assert_called_once_with(
        crawler_type=CrawlerType.SELENIUM,
        interact_with_consent=True,
        headless=False,
        user_data_dir="/path/to/profile"
    )
    
    # Überprüfe, ob die Methode des Analyzers korrekt aufgerufen wurde
    mock_analyzer.analyze_website.assert_called_once_with(
        "https://example.com", 3, "/path/to/database.csv"
    )
    
    # Überprüfe die Rückgabewerte
    assert classified_cookies == {"Analytics": [{"name": "test_cookie"}]}
    assert storage_data == {"https://example.com": {"localStorage": {}, "sessionStorage": {}}}


def test_analyze_website_wrapper_async(mock_cookie_analyzer):
    """Testet die analyze_website-Wrapper-Funktion mit asynchronem Crawler."""
    mock_analyzer_class, mock_analyzer, mock_init_services = mock_cookie_analyzer
    
    # Test mit asynchronem Crawler
    analyze_website(
        url="https://example.com",
        use_async=True,
        use_selenium=False
    )
    
    # Überprüfe, ob die CookieAnalyzer-Klasse mit dem richtigen Crawler-Typ instanziiert wurde
    mock_analyzer_class.assert_called_once_with(
        crawler_type=CrawlerType.PLAYWRIGHT_ASYNC,
        interact_with_consent=True,
        headless=True,
        user_data_dir=None
    )


def test_analyze_website_with_consent_stages_wrapper(mock_cookie_analyzer):
    """Testet die analyze_website_with_consent_stages-Wrapper-Funktion."""
    mock_analyzer_class, mock_analyzer, mock_init_services = mock_cookie_analyzer
    
    # Test mit Standard-Parametern
    pre_cookies, pre_storage, post_cookies, post_storage = analyze_website_with_consent_stages(
        url="https://example.com",
        max_pages=2,
        database_path="/path/to/database.csv",
        headless=True,
        user_data_dir="/path/to/profile"
    )
    
    # Überprüfe, ob die Services initialisiert wurden
    mock_init_services.assert_called_once()
    
    # Überprüfe, ob die CookieAnalyzer-Klasse korrekt instanziiert wurde
    mock_analyzer_class.assert_called_once_with(
        crawler_type=CrawlerType.SELENIUM,
        interact_with_consent=True,
        headless=True,
        user_data_dir="/path/to/profile"
    )
    
    # Überprüfe, ob die Methode des Analyzers korrekt aufgerufen wurde
    mock_analyzer.analyze_website_with_consent_stages.assert_called_once_with(
        "https://example.com", 2, "/path/to/database.csv"
    )
    
    # Überprüfe die Rückgabewerte
    assert pre_cookies == {"Analytics": [{"name": "test_cookie_pre"}]}
    assert pre_storage == {"https://example.com": {"localStorage": {}, "phase": "pre-consent"}}
    assert post_cookies == {"Analytics": [{"name": "test_cookie_post"}], "Marketing": [{"name": "_ga"}]}
    assert post_storage == {"https://example.com": {"localStorage": {"consent": "true"}, "phase": "post-consent"}}