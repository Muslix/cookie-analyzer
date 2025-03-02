"""
Tests für den Cookie-Classifier.
"""

import pytest
from unittest.mock import patch
from cookie_analyzer.handlers.cookie_classifier import CookieClassifier


def test_classify_cookies(mock_database, mock_cookies):
    """Testet die Klassifizierung von Cookies nach Kategorien."""
    classifier = CookieClassifier()
    
    classified_cookies = classifier.classify_cookies(mock_cookies, mock_database)
    
    # Überprüfe, ob die Ergebnisse ein Dictionary sind
    assert isinstance(classified_cookies, dict)
    
    # Überprüfe, ob die erwarteten Kategorien vorhanden sind
    assert "Analytics" in classified_cookies
    assert "Marketing" in classified_cookies
    assert "Necessary" in classified_cookies
    assert "Unbekannt" in classified_cookies
    
    # Überprüfe, ob die Cookies korrekt klassifiziert wurden
    analytics_cookies = classified_cookies["Analytics"]
    marketing_cookies = classified_cookies["Marketing"]
    necessary_cookies = classified_cookies["Necessary"]
    unknown_cookies = classified_cookies["Unbekannt"]
    
    # Erwartete Cookies in jeder Kategorie
    assert any(cookie["name"] == "test_cookie" for cookie in analytics_cookies)
    assert any(cookie["name"] == "_ga" for cookie in marketing_cookies)
    assert any(cookie["name"] == "fr" for cookie in marketing_cookies)
    assert any(cookie["name"] == "session_id" for cookie in necessary_cookies)


def test_remove_duplicates(mock_cookies):
    """Testet das Entfernen von Duplikaten aus der Cookie-Liste."""
    classifier = CookieClassifier()
    
    # Erstelle Duplikate
    duplicates = mock_cookies + [
        # Doppelter Eintrag für test_cookie
        {
            "name": "test_cookie",
            "value": "different_value",
            "domain": "example.com",
            "path": "/",
            "expires": 1672531200,
            "secure": True,
            "httpOnly": True
        }
    ]
    
    # Entferne Duplikate
    unique_cookies = classifier.remove_duplicates(duplicates)
    
    # Stelle sicher, dass die Anzahl der einzigartigen Cookies korrekt ist
    assert len(unique_cookies) == len(mock_cookies)
    
    # Stelle sicher, dass jeder Cookie-Name nur einmal vorkommt
    cookie_names = [cookie["name"] for cookie in unique_cookies]
    assert len(cookie_names) == len(set(cookie_names))


def test_find_cookie_info():
    """Testet die Suche nach Cookie-Informationen in der Datenbank."""
    classifier = CookieClassifier()
    
    # Erstelle eine Test-Datenbank
    test_db = [
        {
            "name": "test_cookie",
            "category": "Analytics",
            "vendor": "Test Vendor",
            "description": "Test Description"
        },
        {
            "name": "wildcard_*_cookie",
            "category": "Marketing",
            "vendor": "Wildcard Vendor",
            "description": "Wildcard Description",
            "wildcard": "1"
        }
    ]
    
    # Teste mit exaktem Match
    exact_match = classifier.find_cookie_info("test_cookie", test_db)
    assert exact_match is not None
    assert exact_match["category"] == "Analytics"
    
    # Teste mit Wildcard-Match
    wildcard_match = classifier.find_cookie_info("wildcard_123_cookie", test_db)
    assert wildcard_match is not None
    assert wildcard_match["category"] == "Marketing"
    
    # Teste mit nicht vorhandenem Cookie
    no_match = classifier.find_cookie_info("nonexistent_cookie", test_db)
    assert no_match is None


def test_classify_with_heuristics():
    """Testet die heuristische Klassifizierung von Cookies."""
    classifier = CookieClassifier()
    
    # Cookies, die anhand von Heuristiken klassifiziert werden sollten
    heuristic_cookies = [
        # Session-Cookie
        {
            "name": "session_token",
            "value": "abc123",
            "domain": "example.com",
            "expires": -1
        },
        # Analytics-Cookie (Google Analytics)
        {
            "name": "_gat",
            "value": "1",
            "domain": "google-analytics.com"
        },
        # Marketing-Cookie (Facebook)
        {
            "name": "fbp",
            "value": "fb.1.1234567890",
            "domain": "facebook.com"
        },
        # Preference-Cookie
        {
            "name": "theme_preference",
            "value": "dark"
        }
    ]
    
    # Klassifiziere mit leerer Datenbank, um nur Heuristiken zu verwenden
    classified = classifier.classify_cookies(heuristic_cookies, [])
    
    # Überprüfe, ob die Cookies basierend auf Heuristiken korrekt klassifiziert wurden
    assert any(cookie["name"] == "session_token" for cookie in classified.get("Necessary", []))
    assert any(cookie["name"] == "_gat" for cookie in classified.get("Analytics", []))
    assert any(cookie["name"] == "fbp" for cookie in classified.get("Marketing", []))
    
    # Präferenz-Cookies sollten als Preferences klassifiziert werden
    assert any(cookie["name"] == "theme_preference" for cookie in classified.get("Preferences", []))


def test_identify_fingerprinting():
    """Testet die Erkennung von Fingerprinting-Techniken."""
    classifier = CookieClassifier()
    
    cookies = [
        {
            "name": "canvas_fp",
            "value": "hash_value",
            "domain": "example.com"
        }
    ]
    
    storage = {
        "https://example.com": {
            "localStorage": {
                "device_fingerprint": "device_id_12345",
                "fpjs_id": "fingerprint_value"
            },
            "sessionStorage": {}
        }
    }
    
    fingerprinting = classifier.identify_fingerprinting(cookies, storage)
    
    # Überprüfe, ob Fingerprinting erkannt wurde
    assert isinstance(fingerprinting, dict)
    assert any(fingerprinting.values())