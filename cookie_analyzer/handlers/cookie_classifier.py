"""
Cookie-Classifier für die Klassifizierung von Cookies basierend auf Regeln und Datenbank-Einträgen.
"""

import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class CookieClassifier:
    """Klasse zur Cookie-Klassifizierung anhand von Regelwerken."""
    
    # Cookie-Kategorien
    CATEGORIES = {
        "NECESSARY": "Strictly Necessary",
        "FUNCTIONAL": "Functional",
        "PERFORMANCE": "Performance",
        "ANALYTICS": "Performance",  # Analytics wird als Performance-Kategorie betrachtet
        "TARGETING": "Targeting",
        "OTHER": "Other"
    }
    
    # Domain-basierte Klassifikation
    DOMAIN_RULES = {
        "google-analytics.com": "Performance",
        "analytics": "Performance",
        "googletagmanager.com": "Performance",
        "doubleclick.net": "Targeting",
        "facebook.com": "Targeting",
        "fb.com": "Targeting",
        "bing.com": "Targeting",
        "twitter.com": "Targeting",
        "linkedin.com": "Targeting",
        "youtube.com": "Targeting"
    }
    
    # Name-basierte Klassifikation
    NAME_RULES = {
        # Session und notwendige Cookies
        r"^(sess|session|PHPSESSID|wordpress_logged_in|wp-settings|auth|secure|csrf|xsrf|_token)": "Strictly Necessary",
        r"^(consent|cookie_consent|cc_|cookieconsent|privacy)": "Strictly Necessary",
        r"^(cf_|cloudflare)": "Strictly Necessary",

        # Funktionale Cookies
        r"^(prefs|preferences|language|lang|region|country|timezone|_locale)": "Functional",
        r"^(settings|config|theme|layout|view|display)": "Functional",

        # Analytics und Performance
        r"^(_ga|_gid|_gat|_utm|__utm|_pk_|pk_|piwik|matomo|sc_|_hjid|_hjSessionUser)": "Performance",
        r"(analytics|metric|collect|track|visit|stats|event|perf)": "Performance",

        # Targeting und Werbung
        r"^(_fbp|_fbc|fr|tr|_gcl_|_uetsid|_uetvid|_pinterest|lidc|bcookie)": "Targeting",
        r"(adv|ads|banner|campaign|promo|recommendation|retarget|affiliate|market|special)": "Targeting",
    }
    
    # Keyword-basierte Klassifikation (in Namen oder Werten)
    KEYWORD_RULES = {
        # Session und notwendige Cookies
        "session": "Strictly Necessary",
        "csrf": "Strictly Necessary",
        "security": "Strictly Necessary",
        "language": "Strictly Necessary",  # Spracheinstellung ist notwendig für die Funktionalität
        "preference": "Strictly Necessary",
        "necessary": "Strictly Necessary",
        
        # Funktionale Cookies
        "functional": "Functional",
        "settings": "Functional",
        "preferences": "Functional",
        "customization": "Functional",
        
        # Analytics und Performance
        "analytics": "Performance",
        "statistics": "Performance",
        "stats": "Performance",
        "performance": "Performance",
        "tracking": "Performance",
        "measure": "Performance",
        
        # Targeting und Werbung
        "advertising": "Targeting",
        "advert": "Targeting",
        "targeting": "Targeting",
        "remarketing": "Targeting",
        "campaign": "Targeting",
        "partner": "Targeting",
        "affiliate": "Targeting",
    }
    
    @classmethod
    def classify_by_rule(cls, cookie: Dict[str, Any]) -> str:
        """
        Klassifiziert ein Cookie basierend auf Regeln.
        
        Args:
            cookie: Das zu klassifizierende Cookie
            
        Returns:
            Die Kategorie des Cookies
        """
        name = cookie.get('name', '')
        domain = cookie.get('domain', '')
        value = cookie.get('value', '')
        
        # 1. Domain-basierte Regeln
        for domain_pattern, category in cls.DOMAIN_RULES.items():
            if domain_pattern in domain:
                return category
        
        # 2. Name-basierte Regeln mit regulären Ausdrücken
        for pattern, category in cls.NAME_RULES.items():
            if re.search(pattern, name, re.IGNORECASE):
                return category
        
        # 3. Keyword-basierte Regeln
        for keyword, category in cls.KEYWORD_RULES.items():
            if keyword in name.lower() or (value and keyword in value.lower()):
                return category
        
        # 4. Heuristiken basierend auf anderen Cookie-Eigenschaften
        
        # 4.1 Session-Cookies ohne Ablaufdatum sind wahrscheinlich notwendig
        if cookie.get('session', False):
            return "Strictly Necessary"
        
        # 4.2 Cookies mit zufällig aussehenden kurzen Namen sind oft Analytics
        if len(name) <= 4 and re.search(r'[0-9a-z]{2,4}', name):
            return "Performance"
        
        # 4.3 Cookies mit sehr langer Lebensdauer sind oft Tracking/Targeting
        if cookie.get('expires') and isinstance(cookie['expires'], (int, float)) and cookie['expires'] > 86400 * 30:  # > 30 Tage
            return "Targeting"
        
        # 5. Fallback: Unbekannt
        return "Other"
    
    @staticmethod
    def map_database_category(category: str) -> str:
        """
        Mappt eine Kategorie aus der Datenbank auf eine der Standardkategorien.
        
        Args:
            category: Die zu mappende Kategorie
            
        Returns:
            Die gemappte Standardkategorie
        """
        category = category.lower()
        
        if any(keyword in category for keyword in ['essential', 'necessary', 'erforderlich']):
            return "Strictly Necessary"
        
        if any(keyword in category for keyword in ['functional', 'preference', 'preferenz']):
            return "Functional"
        
        if any(keyword in category for keyword in ['analytic', 'statistic', 'performance']):
            return "Performance"
        
        if any(keyword in category for keyword in ['targeting', 'advertisement', 'werbung', 'marketing']):
            return "Targeting"
        
        return "Other"
    
    @staticmethod
    def remove_duplicates(cookies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Entfernt doppelte Cookies aus einer Liste.
        
        Args:
            cookies: Die zu bereinigende Cookie-Liste
            
        Returns:
            Eine Liste ohne doppelte Cookies
        """
        unique_cookies = {}
        for cookie in cookies:
            key = (cookie.get('name', ''), cookie.get('domain', ''), cookie.get('path', '/'))
            if key not in unique_cookies:
                unique_cookies[key] = cookie
            
        return list(unique_cookies.values())
    
    def classify_cookies(self, cookies: List[Dict[str, Any]], database: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Klassifiziert eine Liste von Cookies mithilfe einer Datenbank und Regeln.
        
        Args:
            cookies: Die zu klassifizierenden Cookies
            database: Eine Cookie-Datenbank zum Nachschlagen
            
        Returns:
            Ein Dictionary mit den klassifizierten Cookies nach Kategorien
        """
        from ..database.handler import find_cookie_info
        
        classified = {
            "Strictly Necessary": [],
            "Functional": [],
            "Performance": [],
            "Targeting": [],
            "Other": []
        }
        
        for cookie in cookies:
            cookie_name = cookie.get('name', '')
            
            # Versuche, das Cookie in der Datenbank zu finden
            cookie_info = find_cookie_info(cookie_name, database)
            
            if cookie_info and cookie_info.get('Category', '') != "Unknown":
                # Cookie wurde in der Datenbank gefunden
                category = self.map_database_category(cookie_info['Category'])
                description = cookie_info.get('Description', 'Keine Beschreibung verfügbar.')
                classification_method = "database"
            else:
                # Cookie nicht in der Datenbank gefunden, verwende Regeln
                category = self.classify_by_rule(cookie)
                description = self._generate_description(cookie, category)
                classification_method = "rule"
            
            # Füge die Klassifizierungsinformationen zum Cookie hinzu
            cookie['description'] = description
            cookie['category'] = category
            cookie['classification_method'] = classification_method
            
            # Füge das Cookie zur richtigen Kategorie hinzu
            classified[category].append(cookie)
        
        return classified
    
    def _generate_description(self, cookie: Dict[str, Any], category: str) -> str:
        """
        Generiert eine Beschreibung für ein Cookie basierend auf seiner Kategorie.
        
        Args:
            cookie: Das Cookie
            category: Die Kategorie des Cookies
            
        Returns:
            Eine generierte Beschreibung
        """
        name = cookie.get('name', '')
        domain = cookie.get('domain', '')
        
        descriptions = {
            "Strictly Necessary": f"Dieses Cookie ({name}) ist notwendig für die grundlegende Funktionalität der Website.",
            "Functional": f"Dieses Cookie ({name}) verbessert die Benutzerfreundlichkeit und speichert möglicherweise Benutzereinstellungen.",
            "Performance": f"Dieses Cookie ({name}) wird verwendet, um Informationen darüber zu sammeln, wie Besucher die Website nutzen.",
            "Targeting": f"Dieses Cookie ({name}) wird verwendet, um Besuchern relevante Werbung zu zeigen.",
            "Other": f"Dieses Cookie ({name}) konnte keiner spezifischen Kategorie zugeordnet werden."
        }
        
        return descriptions.get(category, "Keine Beschreibung verfügbar.")
    
    def get_consent_categories(self, cookies: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Berechnet, wie viele Cookies in jeder Consent-Kategorie enthalten sind.
        
        Args:
            cookies: Die zu analysierenden Cookies
            
        Returns:
            Ein Dictionary mit der Anzahl der Cookies pro Kategorie
        """
        classified = self.classify_cookies(cookies, [])  # Leere Datenbank für regelbasierte Klassifikation
        return {category: len(cookies) for category, cookies in classified.items()}
    
    def identify_fingerprinting(self, cookies: List[Dict[str, Any]], storage_data: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
        """
        Identifiziert potenzielle Fingerprinting-Techniken basierend auf Cookies und Storage-Daten.
        
        Args:
            cookies: Liste der Cookies
            storage_data: Dictionary mit LocalStorage- und SessionStorage-Daten
            
        Returns:
            Dictionary mit identifizierten Fingerprinting-Techniken
        """
        results = {
            "canvas_fingerprinting": False,
            "font_fingerprinting": False,
            "webrtc_fingerprinting": False,
            "audio_fingerprinting": False,
            "battery_fingerprinting": False,
            "persistent_identifiers": False
        }
        
        # Überprüfe Cookies nach bestimmten Patterns
        for cookie in cookies:
            name = cookie.get('name', '').lower()
            value = cookie.get('value', '').lower()
            
            # Suche nach persistenten Identifikatoren
            if any(pattern in name for pattern in ['id', 'uid', 'uuid', 'guid', 'fingerprint']):
                if len(value) > 15:  # Lange Werte sind verdächtig
                    results["persistent_identifiers"] = True
            
            # Verdächtig lange Cookie-Werte könnten Fingerprinting-Daten sein
            if len(value) > 100:
                results["persistent_identifiers"] = True
        
        # Überprüfe die Storage-Daten auf Fingerprinting-Indikatoren
        for url, storage in storage_data.items():
            local_storage = storage.get("localStorage", {})
            session_storage = storage.get("sessionStorage", {})
            
            # Kombiniere beide Storage-Typen für die Analyse
            all_storage = {**local_storage, **session_storage}
            
            for key, value in all_storage.items():
                key = key.lower()
                if isinstance(value, str):
                    value = value.lower()
                else:
                    # Falls value kein String ist, überspringe diesen Eintrag
                    continue
                
                # Canvas Fingerprinting
                if any(pattern in key for pattern in ['canvas', 'fingerprint', 'signature', 'hash', 'id']) and (
                    'data:image' in value or len(value) > 100
                ):
                    results["canvas_fingerprinting"] = True
                
                # Font Fingerprinting
                if any(pattern in key for pattern in ['font', 'text', 'glyph']) or (
                    ('arial' in value and 'helvetica' in value) or 'font' in value
                ):
                    results["font_fingerprinting"] = True
                
                # WebRTC Fingerprinting
                if 'webrtc' in key or 'stun' in value or 'turn' in value or 'ice' in value:
                    results["webrtc_fingerprinting"] = True
                
                # Audio Fingerprinting
                if 'audio' in key or 'sound' in key or 'oscillator' in value:
                    results["audio_fingerprinting"] = True
                
                # Battery Fingerprinting
                if 'battery' in key or 'power' in key:
                    results["battery_fingerprinting"] = True
        
        return results