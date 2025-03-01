"""
Basis-Protokolle für die Crawler-Implementierungen.
"""

from typing import Protocol, List, Dict, Any

class PageProtocol(Protocol):
    """Protokoll für eine Browser-Seite."""
    
    async def goto(self, url: str) -> None:
        """Navigiert zu einer URL."""
        ...
    
    async def evaluate(self, script: str) -> Any:
        """Führt JavaScript in der Seite aus und gibt das Ergebnis zurück."""
        ...
    
    async def close(self) -> None:
        """Schließt die Seite."""
        ...

class BrowserContextProtocol(Protocol):
    """Protokoll für einen Browser-Kontext."""
    
    async def new_page(self) -> PageProtocol:
        """Erstellt eine neue Seite im Browser-Kontext."""
        ...
    
    async def cookies(self) -> List[Dict[str, Any]]:
        """Gibt die Cookies des Browser-Kontexts zurück."""
        ...
    
    async def close(self) -> None:
        """Schließt den Browser-Kontext."""
        ...