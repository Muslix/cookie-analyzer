"""
Tests für die URL-Validierungs-Funktionen.
"""

import pytest
from cookie_analyzer.utils.url import validate_url


def test_validate_url_with_valid_urls():
    """Testet die URL-Validierung mit gültigen URLs."""
    valid_urls = [
        "https://www.example.com",
        "http://example.com",
        "https://sub.domain.example.co.uk/path?query=value#fragment",
        "http://localhost:8080",
        "https://192.168.1.1"
    ]
    
    for url in valid_urls:
        assert validate_url(url) == url
        
    # URLs ohne Schema sollten https:// bekommen
    assert validate_url("example.com") == "https://example.com"
    assert validate_url("www.example.com") == "https://www.example.com"


def test_validate_url_with_invalid_urls():
    """Testet die URL-Validierung mit ungültigen URLs."""
    invalid_urls = [
        "",
        "not-a-url",
        "http://",
        "https://",
        "ftp://example.com",  # Nicht unterstütztes Protokoll
        "httpss://example.com"  # Nicht unterstütztes Protokoll
    ]
    
    for url in invalid_urls:
        assert validate_url(url) is None


def test_validate_url_with_special_cases():
    """Testet die URL-Validierung mit speziellen Fällen."""
    # Unicode-Domains
    assert validate_url("http://例子.测试") == "http://例子.测试"
    
    # URLs mit Benutzername und Passwort sollten akzeptiert werden
    assert validate_url("http://user:pass@example.com") == "http://user:pass@example.com"
    
    # URLs mit Leerzeichen sollten codiert werden
    assert validate_url("https://example.com/path with spaces") == "https://example.com/path%20with%20spaces"
    
    # IPv6-Adresse
    assert validate_url("http://[2001:db8:85a3:8d3:1319:8a2e:370:7348]") == "http://[2001:db8:85a3:8d3:1319:8a2e:370:7348]"