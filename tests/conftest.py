"""
Test-Konfiguration und gemeinsame Fixtures für Cookie-Analyzer-Tests.
"""

import os
import sys
import pytest
from typing import Dict, List, Any, Tuple
from unittest.mock import MagicMock, patch

# Stellen Sie sicher, dass das Hauptmodul im Pfad ist
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cookie_analyzer.services.initializer import initialize_services
from cookie_analyzer.services.crawler_factory import CrawlerType


@pytest.fixture(scope="session", autouse=True)
def init_services():
    """Initialisiert die Services vor allen Tests."""
    initialize_services()


@pytest.fixture
def mock_database():
    """Fixture für eine Mock-Cookie-Datenbank."""
    return [
        {
            "id": "test-id-1",
            "vendor": "Test Vendor",
            "category": "Analytics",
            "name": "test_cookie",
            "value": "",
            "description": "Test cookie for analytics",
            "expiration": "1 year",
            "domain": "example.com",
            "url": "https://example.com/privacy",
            "wildcard": "0"
        },
        {
            "id": "test-id-2",
            "vendor": "Google",
            "category": "Marketing",
            "name": "_ga",
            "value": "",
            "description": "Google Analytics cookie",
            "expiration": "2 years",
            "domain": "google.com",
            "url": "https://policies.google.com/privacy",
            "wildcard": "0"
        },
        {
            "id": "test-id-3",
            "vendor": "Facebook",
            "category": "Marketing",
            "name": "fr",
            "value": "",
            "description": "Facebook tracking cookie",
            "expiration": "3 months",
            "domain": "facebook.com",
            "url": "https://www.facebook.com/policy/cookies/",
            "wildcard": "0"
        },
        {
            "id": "test-id-4",
            "vendor": "Generic",
            "category": "Necessary",
            "name": "session_id",
            "value": "",
            "description": "Session identifier",
            "expiration": "Session",
            "domain": "",
            "url": "",
            "wildcard": "0"
        },
        {
            "id": "test-id-5",
            "vendor": "YouTube",
            "category": "Marketing",
            "name": "YSC",
            "value": "",
            "description": "YouTube session cookie",
            "expiration": "Session",
            "domain": "youtube.com",
            "url": "https://policies.google.com/privacy",
            "wildcard": "0"
        }
    ]


@pytest.fixture
def mock_cookies():
    """Fixture für eine Liste von Test-Cookies."""
    return [
        {
            "name": "test_cookie",
            "value": "test_value",
            "domain": "example.com",
            "path": "/",
            "expires": 1672531200,  # 2023-01-01
            "secure": True,
            "httpOnly": True
        },
        {
            "name": "_ga",
            "value": "GA1.2.1234567890.1609459200",
            "domain": "google.com",
            "path": "/",
            "expires": 1704067200,  # 2024-01-01
            "secure": False,
            "httpOnly": False
        },
        {
            "name": "fr",
            "value": "random_value",
            "domain": "facebook.com",
            "path": "/",
            "expires": 1641081600,  # 2022-01-02
            "secure": True,
            "httpOnly": True
        },
        {
            "name": "session_id",
            "value": "user_session_123",
            "domain": "example.com",
            "path": "/",
            "expires": -1,  # Session
            "secure": True,
            "httpOnly": True
        }
    ]


@pytest.fixture
def mock_storage():
    """Fixture für Mock-Storage-Daten."""
    return {
        "https://example.com": {
            "localStorage": {
                "theme": "dark",
                "language": "de",
                "user_preferences": '{"notifications": true, "newsletter": false}'
            },
            "sessionStorage": {
                "recent_search": "laptop",
                "cart_id": "cart_12345"
            },
            "dynamicCookies": []
        }
    }


@pytest.fixture
def mock_crawler():
    """Fixture für einen Mock-Crawler."""
    crawler = MagicMock()
    crawler.crawl.return_value = ([], {})
    return crawler


@pytest.fixture
def mock_crawler_factory():
    """Fixture für eine Mock-Crawler-Factory."""
    with patch('cookie_analyzer.services.crawler_factory.get_crawler_service') as mock_factory:
        yield mock_factory