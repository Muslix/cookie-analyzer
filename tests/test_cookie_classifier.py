"""
CookieHandler-Klasse zur Verarbeitung und Klassifizierung von Cookies.
"""

import logging
from typing import Dict, List, Any, Set

from .cookie_classifier import CookieClassifier

logger = logging.getLogger(__name__)

class CookieHandler:
    """Handles cookie classification and processing operations."""
    
    def __init__(self):
        """Initialisiert den CookieHandler."""
        self.classifier = CookieClassifier()
    
    def classify_cookies(self, cookies: List[Dict[str, Any]], 
                        cookie_database: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Klassifiziert Cookies und ergänzt Informationen aus der Cookie-Datenbank.
        
        Args:
            cookies: Liste der zu klassifizierenden Cookies
            cookie_database: Die Cookie-Datenbank mit Klassifikationsinformationen
            
        Returns:
            Dictionary mit klassifizierten Cookies nach Kategorien
        """
        from ..database.handler import find_cookie_info
        
        classified = {
            "Strictly Necessary": [],
            "Performance": [],
            "Targeting": [],
            "Other": []
        }
        
        for cookie in cookies:
            # 1. Versuche Klassifizierung über Datenbank
            cookie_info = find_cookie_info(cookie["name"], cookie_database)
            db_category = cookie_info.get("Category", "Unknown")
            
            cookie.update({
                "description": cookie_info.get("Description", "Keine Beschreibung verfügbar."),
                "category": db_category,
            })
            
            # 2. Falls keine Datenbank-Kategorie oder unbekannt, verwende regelbasierte Klassifizierung
            if db_category == "Unknown" or db_category == "Other":
                rule_category = CookieClassifier.classify_by_rule(cookie)
                cookie["category"] = rule_category
                if rule_category != "Other":
                    cookie["classification_method"] = "rule-based"
                    logger.info(f"Cookie '{cookie['name']}' durch Regeln als '{rule_category}' klassifiziert")
            else:
                cookie["classification_method"] = "database"
            
            # 3. Füge den Cookie der entsprechenden Kategorie hinzu
            category = cookie["category"]
            
            if category.lower() == "functional" or category.lower() == "necessary" or category == "Strictly Necessary":
                classified["Strictly Necessary"].append(cookie)
            elif category.lower() == "analytics" or category == "Performance":
                classified["Performance"].append(cookie)
            elif category.lower() == "marketing" or category == "Targeting":
                classified["Targeting"].append(cookie)
            else:
                classified["Other"].append(cookie)
        
        return classified
    
    def remove_duplicates(self, cookies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Entfernt doppelte Cookies aus einer Liste. Cookies werden als doppelt betrachtet,
        wenn sie den gleichen Namen und die gleiche Domain haben.
        
        Args:
            cookies: Liste von Cookie-Dictionaries
            
        Returns:
            Liste ohne doppelte Cookies
        """
        unique_cookies = {}
        
        for cookie in cookies:
            key = (cookie.get('name', ''), cookie.get('domain', ''))
            if key not in unique_cookies:
                unique_cookies[key] = cookie
        
        return list(unique_cookies.values())
    
    def get_consent_categories(self, cookies: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Analysiert Cookies und ordnet sie Consent-Kategorien zu.
        Gibt die Anzahl der Cookies pro Kategorie zurück.
        
        Args:
            cookies: Liste von Cookie-Dictionaries
            
        Returns:
            Dictionary mit Anzahl der Cookies pro Kategorie
        """
        categories = {
            "Strictly Necessary": 0,
            "Performance": 0,
            "Targeting": 0,
            "Other": 0
        }
        
        classified = self.classify_cookies(cookies, [])  # Leere Datenbank -> nur regelbasierte Klassifizierung
        
        for category, cookie_list in classified.items():
            categories[category] = len(cookie_list)
        
        return categories
    
    def identify_fingerprinting(self, cookies: List[Dict[str, Any]], 
                               local_storage: Dict[str, Dict[str, str]]) -> Dict[str, bool]:
        """
        Identifiziert potenzielle Fingerprinting-Techniken.
        
        Args:
            cookies: Liste von Cookie-Dictionaries
            local_storage: Dictionary mit Local Storage-Daten
            
        Returns:
            Dictionary mit erkannten Fingerprinting-Techniken
        """
        import re
        
        fingerprinting = {
            "canvas_fingerprinting": False,
            "font_fingerprinting": False,
            "webrtc_fingerprinting": False,
            "battery_api": False,
            "device_enumeration": False,
            "persistent_identifiers": False
        }
        
        # Prüfe Cookies nach typischen Fingerprinting-Bezeichnern
        fingerprinting_patterns = [
            r"canvas", r"fp2?", r"fingerprint", r"visitorid", r"deviceid",
            r"uniqueid", r"visitor", r"machine", r"(?:u|v|m|d|s)id"
        ]
        
        # Prüfe LocalStorage nach Fingerprinting-Indikatoren
        storage_fingerprinting_patterns = [
            "canvas", "fingerprint", "deviceid", "browserhash", "clientid",
            "uniqueid", "deviceprint", "fp2"
        ]
        
        # Suche nach Fingerprinting-Mustern in Cookies
        for cookie in cookies:
            name = cookie.get("name", "").lower()
            value = str(cookie.get("value", "")).lower()
            
            if any(re.search(pattern, name, re.IGNORECASE) for pattern in fingerprinting_patterns):
                fingerprinting["persistent_identifiers"] = True
            
            # Lange, kryptische Werte können auf Fingerprinting hindeuten
            if len(value) > 50 and re.search(r'^[a-zA-Z0-9+/]{50,}={0,2}$', value):
                fingerprinting["persistent_identifiers"] = True
        
        # Suche nach Fingerprinting-Indikatoren im LocalStorage
        for url, storage in local_storage.items():
            local_store = storage.get("localStorage", {})
            
            for key, value in local_store.items():
                key_lower = key.lower()
                if any(pattern in key_lower for pattern in storage_fingerprinting_patterns):
                    fingerprinting["persistent_identifiers"] = True
                
                # Canvas-Fingerprinting speichert oft Base64-kodierte Daten
                if ("canvas" in key_lower and len(str(value)) > 500) or "canvasfingerprint" in key_lower:
                    fingerprinting["canvas_fingerprinting"] = True
                
                # Font-Fingerprinting
                if "font" in key_lower and ("fingerprint" in key_lower or "detection" in key_lower):
                    fingerprinting["font_fingerprinting"] = True
                
                # WebRTC-Fingerprinting
                if "webrtc" in key_lower or "rtcfingerprint" in key_lower:
                    fingerprinting["webrtc_fingerprinting"] = True
        
        return fingerprinting

# Legacy functions for backward compatibility
def classify_cookies(cookies: List[Dict[str, Any]], cookie_database: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Legacy function for backward compatibility."""
    handler = CookieHandler()
    return handler.classify_cookies(cookies, cookie_database)

def remove_duplicate_cookies(cookies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Legacy function for backward compatibility."""
    handler = CookieHandler()
    return handler.remove_duplicates(cookies)