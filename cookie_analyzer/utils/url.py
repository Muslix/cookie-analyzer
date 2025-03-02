"""
URL-Validierungsfunktionen für den Cookie-Analyzer.
"""
import logging
from urllib.parse import urlparse, quote
import re

logger = logging.getLogger(__name__)

def validate_url(url: str) -> str:
    """
    Validiert eine URL und fügt das Schema hinzu, wenn es fehlt.
    
    Args:
        url: Die zu validierende URL
        
    Returns:
        Die validierte URL mit Schema oder None bei ungültiger URL
    """
    # Leere URL prüfen
    if not url or url.strip() == "":
        return None
        
    # Einfache Validierung für offensichtlich ungültige URLs
    if url in ["http://", "https://"]:
        return None
        
    # Nicht unterstützte Protokolle prüfen
    if url.startswith(('ftp://', 'mailto:', 'file://', 'httpss://')):
        return None

    # Erkenne ungültige Hostnamen ohne Punkt (außer localhost)
    if not "." in url and not "localhost" in url and not ":" in url:
        return None
        
    # Schema hinzufügen, wenn es fehlt
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    try:
        # Spaces in URL escapen
        if " " in url:
            # URL in Teile zerlegen, um nur den Pfad zu kodieren
            parsed = urlparse(url)
            if parsed.path and " " in parsed.path:
                # Pfad kodieren
                encoded_path = quote(parsed.path)
                # URL neu zusammensetzen
                scheme = f"{parsed.scheme}://" if parsed.scheme else ""
                netloc = parsed.netloc
                query = f"?{parsed.query}" if parsed.query else ""
                fragment = f"#{parsed.fragment}" if parsed.fragment else ""
                url = f"{scheme}{netloc}{encoded_path}{query}{fragment}"
        
        # Überprüfe, ob die URL syntaktisch gültig ist
        parsed = urlparse(url)
        
        # Erlaube localhost
        if parsed.netloc == "localhost" or parsed.netloc.startswith("localhost:"):
            return url
            
        # Erlaube IPv4-Adressen
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?$", parsed.netloc):
            return url
            
        # Erlaube IPv6-Adressen
        if parsed.netloc.startswith("[") and "]" in parsed.netloc:
            return url
            
        # Für normale Domains prüfen, ob ein Punkt enthalten ist
        if parsed.netloc and "." in parsed.netloc:
            return url
        
        # Wenn keine der obigen Bedingungen zutrifft, ist die URL ungültig
        return None
    except Exception as e:
        logger.error(f"Ungültige URL: {url} - {e}")
        return None