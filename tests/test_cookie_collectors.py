"""
Tests für die Cookie-Collector-Klassen.
"""

import pytest
from unittest.mock import MagicMock, patch
from selenium import webdriver
from selenium.webdriver.common.by import By

from cookie_analyzer.crawler.selenium_crawler import (
    CookieCollector, IframeCookieCollector, YouTubeCookieCollector, EcommerceCookieCollector
)


@pytest.fixture
def mock_selenium_driver():
    """Fixture für einen Mock-Selenium-WebDriver."""
    mock_driver = MagicMock(spec=webdriver.Chrome)
    
    # Mock für get_cookies
    mock_driver.get_cookies.return_value = [
        {
            "name": "test_cookie",
            "value": "test_value",
            "domain": "example.com",
            "path": "/",
            "expiry": 1672531200,
            "secure": True,
            "httpOnly": True
        },
        {
            "name": "session_id",
            "value": "abc123",
            "domain": "example.com",
            "path": "/",
            "secure": True,
            "httpOnly": True
        }
    ]
    
    # Mock für execute_script
    mock_driver.execute_script.side_effect = lambda script, *args: {
        "return window._cookieMonitor.getCookies();": [
            {"name": "dynamic_cookie", "value": "dynamic_value"}
        ],
        # JS-Cookies
        """
                let allCookies = [];
                document.cookie.split(';').forEach(function(cookie) {
                    if (cookie.trim() !== '') {
                        let parts = cookie.trim().split('=');
                        let name = parts.shift();
                        let value = parts.join('=');
                        allCookies.push({
                            name: name.trim(),
                            value: value,
                            domain: document.domain,
                            path: '/',
                            source: 'document.cookie'
                        });
                    }
                });
                return allCookies;
            """: [
            {"name": "js_cookie", "value": "js_value", "domain": "example.com", "path": "/", "source": "document.cookie"}
        ],
        # iFrame-Cookies
        """
                        let frameCookies = [];
                        try {
                            document.cookie.split(';').forEach(function(cookie) {
                                if (cookie.trim() !== '') {
                                    let parts = cookie.trim().split('=');
                                    let name = parts.shift();
                                    let value = parts.join('=');
                                    frameCookies.push({
                                        name: name.trim(),
                                        value: value,
                                        domain: document.domain,
                                        path: '/',
                                        source: 'iframe'
                                    });
                                }
                            });
                        } catch (e) {
                            console.error("Fehler beim Extrahieren von iFrame-Cookies:", e);
                        }
                        return frameCookies;
                    """: [
            {"name": "iframe_cookie", "value": "iframe_value", "domain": "iframe.com", "path": "/", "source": "iframe"}
        ],
        # E-Commerce-Cookies
        """
                let allCookies = [];
                for (let key in window) {
                    if (typeof window[key] === 'object' && window[key] !== null) {
                        if (key.toLowerCase().includes('cookie') || 
                            key.toLowerCase().includes('storage') || 
                            key.toLowerCase().includes('tracking')) {
                            try {
                                allCookies.push({
                                    name: key,
                                    value: JSON.stringify(window[key]),
                                    domain: document.domain,
                                    source: 'global_object'
                                });
                            } catch (e) {
                            }
                        }
                    }
                }
                for (let i = 0; i < localStorage.length; i++) {
                    let key = localStorage.key(i);
                    if (key.toLowerCase().includes('cookie') || 
                        key.toLowerCase().includes('track') || 
                        key.toLowerCase().includes('cart') || 
                        key.toLowerCase().includes('session')) {
                        allCookies.push({
                            name: key,
                            value: localStorage.getItem(key),
                            domain: document.domain,
                            source: 'localStorage'
                        });
                    }
                }
                return allCookies;
            """: [
            {"name": "tracking_data", "value": "{\"userId\":\"123\"}", "domain": "example.com", "source": "global_object"},
            {"name": "cart_session", "value": "cart123", "domain": "example.com", "source": "localStorage"}
        ],
        # Default-Rückgabewert für andere Skripte
        "default": {}
    }.get(script, {})
    
    # Mock für find_elements
    mock_iframe = MagicMock()
    mock_iframe.get_attribute.return_value = "https://iframe.example.com"
    
    mock_video = MagicMock()
    
    mock_product = MagicMock()
    
    mock_driver.find_elements.side_effect = lambda by, selector: {
        "iframe": [mock_iframe, mock_iframe],
        "video": [mock_video],
        ".product, .item, .artikel, [class*='product'], [class*='artikel'], [id*='product']": [mock_product]
    }.get(selector, [])
    
    # Mock für page_source
    mock_driver.page_source = "<html><body>YouTube Video</body></html>"
    
    return mock_driver


def test_cookie_collector(mock_selenium_driver):
    """Testet die CookieCollector-Klasse."""
    # Teste die get_cookies-Methode
    cookies = CookieCollector.get_cookies(mock_selenium_driver)
    
    assert len(cookies) == 2
    assert cookies[0]["name"] == "test_cookie"
    assert cookies[0]["value"] == "test_value"
    assert cookies[0]["domain"] == "example.com"
    assert cookies[0]["source"] == "direct"
    
    # Teste die get_js_cookies-Methode
    js_cookies = CookieCollector.get_js_cookies(mock_selenium_driver)
    
    assert len(js_cookies) == 1
    assert js_cookies[0]["name"] == "js_cookie"
    assert js_cookies[0]["value"] == "js_value"
    assert js_cookies[0]["source"] == "document.cookie"
    
    # Teste mit Fehler in execute_script
    mock_selenium_driver.execute_script.side_effect = Exception("JavaScript-Fehler")
    error_js_cookies = CookieCollector.get_js_cookies(mock_selenium_driver)
    assert error_js_cookies == []


def test_iframe_cookie_collector(mock_selenium_driver):
    """Testet die IframeCookieCollector-Klasse."""
    # Mock für switch_to
    mock_selenium_driver.switch_to = MagicMock()
    
    iframe_cookies = IframeCookieCollector.get_iframe_cookies(mock_selenium_driver)
    
    # Überprüfe, ob der Collector iFrames identifiziert hat
    mock_selenium_driver.find_elements.assert_any_call(By.TAG_NAME, "iframe")
    
    # Prüfe, ob zu den iFrames gewechselt wurde
    assert mock_selenium_driver.switch_to.frame.call_count == 2
    assert mock_selenium_driver.switch_to.default_content.call_count == 2
    
    # Überprüfe die Ergebnisse
    assert len(iframe_cookies) == 2  # Zwei iFrames mit jeweils einem Cookie
    for cookie in iframe_cookies:
        assert cookie["name"] == "iframe_cookie"
        assert cookie["value"] == "iframe_value"
        assert cookie["source"] == "iframe"
        assert "iframe_src" in cookie
        assert cookie["iframe_src"] == "https://iframe.example.com"


def test_youtube_cookie_collector(mock_selenium_driver):
    """Testet die YouTubeCookieCollector-Klasse."""
    # Bereite spezifische Cookie-Rückgabewerte für YouTube vor
    mock_selenium_driver.get_cookies.side_effect = [
        # Erste Rückgabe: Standard-Cookies
        [
            {
                "name": "YSC",
                "value": "video_id",
                "domain": "youtube.com",
                "path": "/",
                "expiry": 1672531200,
                "secure": True,
                "httpOnly": True
            },
            {
                "name": "VISITOR_INFO1_LIVE",
                "value": "visitor_id",
                "domain": "youtube.com",
                "path": "/",
                "expiry": 1704067200,
                "secure": True,
                "httpOnly": True
            }
        ],
        # Zweite Rückgabe: Nach Video-Interaktion
        [
            {
                "name": "YSC",
                "value": "video_id",
                "domain": "youtube.com",
                "path": "/",
                "expiry": 1672531200,
                "secure": True,
                "httpOnly": True
            },
            {
                "name": "VISITOR_INFO1_LIVE",
                "value": "visitor_id",
                "domain": "youtube.com",
                "path": "/",
                "expiry": 1704067200,
                "secure": True,
                "httpOnly": True
            },
            {
                "name": "PREF",
                "value": "f6=40000000",
                "domain": "youtube.com",
                "path": "/",
                "expiry": 1704067200,
                "secure": True,
                "httpOnly": False
            }
        ]
    ]
    
    youtube_cookies = YouTubeCookieCollector.get_youtube_cookies(mock_selenium_driver)
    
    # Überprüfe, ob der Collector Videos identifiziert hat
    mock_selenium_driver.find_elements.assert_any_call(By.TAG_NAME, "video")
    
    # Überprüfe die Ergebnisse
    assert len(youtube_cookies) == 3  # 2 initiale Cookies + 1 neuer Cookie nach Interaktion
    
    # Überprüfe die Cookie-Namen
    youtube_cookie_names = {cookie["name"] for cookie in youtube_cookies}
    assert "YSC" in youtube_cookie_names
    assert "VISITOR_INFO1_LIVE" in youtube_cookie_names
    assert "PREF" in youtube_cookie_names
    
    # Überprüfe, ob alle Cookies die richtige Domain haben
    for cookie in youtube_cookies:
        assert cookie["domain"] == "youtube.com"
        assert "source" in cookie
        assert "youtube" in cookie["source"]


def test_ecommerce_cookie_collector(mock_selenium_driver):
    """Testet die EcommerceCookieCollector-Klasse."""
    # Mock für ActionChains
    with patch('cookie_analyzer.crawler.selenium_crawler.webdriver.ActionChains') as mock_actions_class:
        mock_actions = MagicMock()
        mock_actions_class.return_value = mock_actions
        
        ecommerce_cookies = EcommerceCookieCollector.get_ecommerce_cookies(mock_selenium_driver)
        
        # Überprüfe, ob der Collector Produkt-Elemente identifiziert hat
        mock_selenium_driver.find_elements.assert_any_call(By.CSS_SELECTOR, 
            ".product, .item, .artikel, [class*='product'], [class*='artikel'], [id*='product']")
        
        # Überprüfe, ob mit den Produkten interagiert wurde
        assert mock_actions.move_to_element.called
        assert mock_actions.perform.called
        
        # Überprüfe die Ergebnisse
        assert len(ecommerce_cookies) >= 2  # Mindestens die zwei eCommerce-spezifischen Cookies
        
        # Überprüfe, ob die wichtigsten eCommerce-Cookies vorhanden sind
        ecommerce_cookie_names = {cookie["name"] for cookie in ecommerce_cookies}
        assert "tracking_data" in ecommerce_cookie_names
        assert "cart_session" in ecommerce_cookie_names