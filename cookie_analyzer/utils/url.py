"""
URL-Validierungsfunktionen für den Cookie-Analyzer.
"""

import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def validate_url(url: str) -> str:
    """
    Validiert eine URL und fügt das Schema hinzu, wenn es fehlt.
    
    Args:
        url: Die zu validierende URL
        
    Returns:
        Die validierte URL mit Schema oder leerer String bei ungültiger URL
    """
    # Schema hinzufügen, wenn es fehlt
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    try:
        parsed = urlparse(url)
        if parsed.netloc:
            return url
        return ""
    except Exception as e:
        logger.error(f"Ungültige URL: {url} - {e}")
        return ""