"""
Interface-Definitionen für die Service-Komponenten.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Tuple, Protocol, Optional, runtime_checkable, Generic, TypeVar

logger = logging.getLogger(__name__)
T = TypeVar('T')

@runtime_checkable
class CookieDatabaseService(Protocol):
    """Interface for cookie database interactions."""
    
    def load_database(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Loads the cookie database."""
        ...
    
    def find_cookie_info(self, cookie_name: str, cookie_database: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Finds information about a cookie in the database."""
        ...
    
    def update_database(self, output_path: Optional[str] = None, url: Optional[str] = None) -> bool:
        """Updates the cookie database from a source."""
        ...

@runtime_checkable
class CookieClassifierService(Protocol):
    """Interface for cookie classification."""
    
    def classify_cookies(self, cookies: List[Dict[str, Any]], 
                        cookie_database: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Classifies cookies according to their purpose."""
        ...
    
    def remove_duplicates(self, cookies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Removes duplicate cookies from a list."""
        ...
    
    def get_consent_categories(self, cookies: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyzes cookies and returns the number of cookies per consent category."""
        ...
    
    def identify_fingerprinting(self, cookies: List[Dict[str, Any]], 
                              local_storage: Dict[str, Dict[str, str]]) -> Dict[str, bool]:
        """Identifies potential fingerprinting techniques."""
        ...

class CrawlerService(ABC, Generic[T]):
    """Base abstract class for all crawler services."""
    
    @abstractmethod
    def crawl(self) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """Crawls a website and collects cookies."""
        pass