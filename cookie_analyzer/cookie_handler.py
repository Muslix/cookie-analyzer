from typing import Dict, List, Any, Tuple, Optional, Set
import re
import logging

logger = logging.getLogger(__name__)

class CookieClassifier:
    """Klasse zur regelbasierten Klassifizierung von Cookies."""
    
    # Bekannte Cookie-Muster für verschiedene Kategorien
    PATTERNS = {
        "Strictly Necessary": [
            # Session/Login-bezogen
            r"^(session|sess|sid|csrf|xsrf|token|auth|login|secure|jsession|phpsessid)",
            r"sess(ion)?id",
            r"logged_?in",
            r"(cookie)?consent",
            # Technisch notwendige Cookies
            r"wp-settings",
            r"wordpress_?",
            r"woocommerce_",
            r"_shopify_",
            r"cart",
            r"^hs",  # HubSpot
            # Language/Region
            r"language",
            r"country",
            r"currency",
            r"loc(ale)?",
            r"region",
            # Function-specific
            r"^has_js",
        ],
        "Performance": [
            # Analytics
            r"^_ga",
            r"ga-audiences",
            r"^_gid",
            r"^_gat",
            r"utma",
            r"utmb",
            r"utmc",
            r"utmz",
            r"^__utm",
            r"^_pk_",
            r"^mp_",
            r"^mf_",
            r"^matomo",
            r"^mp_",
            # Performance
            r"^_hjAbsoluteSessionInProgress",
            r"^_hjSession",
            r"^_hjid",
            r"^_hj",
            r"optimizely",
            r"^ts_c",
            r"^intercom-session",
        ],
        "Targeting": [
            # Werbe-Cookies
            r"^_fbp",
            r"_ttp",
            r"^_gcl_",
            r"^_uetsid",
            r"^ad(words|form|sense|verb)?",
            r"doubleclick",
            r"^criteo",
            r"^nQ_",
            r"^personalization_id",
            r"^__qca",
            r"^IDE",
            # Social Media
            r"^fr$",
            r"^sb$",
            r"^(tr|guest_id)",
            r"^lidc",
            r"^bcookie",
            r"^(spin|wd|xs|c_user|presence|act)",
            r"^twitter_",
            r"^pinterest_",
            # Tracking
            r"^__gads",
            r"^taboola",
            r"^outbrain",
            r"^zopim",
            r"^lfeeder",
        ]
    }

    # Bekannte Cookie-Domains mit Kategorien
    DOMAINS = {
        "google-analytics.com": "Performance",
        "doubleclick.net": "Targeting",
        "facebook.com": "Targeting",
        "facebook.net": "Targeting",
        "twitter.com": "Targeting",
        "linkedin.com": "Targeting",
        "bing.com": "Targeting",
        "optimizely.com": "Performance",
        "hotjar.com": "Performance",
        "crazyegg.com": "Performance",
        "youtube.com": "Targeting",
        "googleadservices.com": "Targeting",
        "googlesyndication.com": "Targeting",
        "amazon-adsystem.com": "Targeting",
        "adroll.com": "Targeting",
        "adnxs.com": "Targeting",
        "sharethis.com": "Targeting",
        "addthis.com": "Targeting",
        "pinterest.com": "Targeting",
        "hubspot.com": "Performance",
        "analytics": "Performance",
    }

    # Schlüsselwörter im Namen oder Wert des Cookies für Kategorie-Zuordnung
    KEYWORDS = {
        "Strictly Necessary": [
            "session", "csrf", "xsrf", "token", "auth", "login", "secure", 
            "consent", "language", "country", "cart", "currency", "locale", 
            "necessary", "required", "essential"
        ],
        "Performance": [
            "analytics", "ga-", "_ga", "statistic", "stats", "optimize", 
            "performance", "monitor", "ab-test", "test", "heatmap", 
            "hotjar", "matomo", "audience"
        ],
        "Targeting": [
            "ad", "ads", "adsense", "adwords", "banner", "campaign", 
            "cookie", "facebook", "marketing", "partner", "pixel", 
            "recommend", "retarget", "social", "track", "twitter", "visitor"
        ]
    }

    @staticmethod
    def classify_by_rule(cookie: Dict[str, Any]) -> str:
        """
        Klassifiziert einen Cookie anhand von Regeln und Mustern.
        
        Args:
            cookie: Der zu klassifizierende Cookie
            
        Returns:
            Die ermittelte Kategorie des Cookies
        """
        name = cookie.get("name", "").lower()
        domain = cookie.get("domain", "").lower()
        value = str(cookie.get("value", "")).lower()
        
        # 1. Prüfe Domain-basierte Klassifikation
        for known_domain, category in CookieClassifier.DOMAINS.items():
            if known_domain in domain:
                logger.debug(f"Domain-basierte Klassifikation für {name}: {category} (Domain: {domain} enthält {known_domain})")
                return category
        
        # 2. Prüfe Pattern-basierte Klassifikation
        for category, patterns in CookieClassifier.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, name, re.IGNORECASE):
                    logger.debug(f"Pattern-basierte Klassifikation für {name}: {category} (Pattern: {pattern})")
                    return category
        
        # 3. Prüfe Keyword-basierte Klassifikation
        for category, keywords in CookieClassifier.KEYWORDS.items():
            # Prüfe Keywords im Cookie-Namen
            for keyword in keywords:
                if keyword in name:
                    logger.debug(f"Keyword-basierte Klassifikation für {name}: {category} (Keyword im Namen: {keyword})")
                    return category
                    
            # Prüfe Keywords im Cookie-Wert (nur für kurze Werte, um false positives zu vermeiden)
            if len(value) < 50:  # Nur kurze Werte prüfen
                for keyword in keywords:
                    if keyword in value:
                        logger.debug(f"Keyword-basierte Klassifikation für {name}: {category} (Keyword im Wert: {keyword})")
                        return category
        
        # 4. Fallback: Heuristiken basierend auf Cookie-Eigenschaften
        
        # Heuristik 1: Session-Cookies ohne Expire-Date sind oft "Strictly Necessary"
        if cookie.get("expires", -1) == -1 or cookie.get("session", False):
            logger.debug(f"Heuristische Klassifikation für {name}: Strictly Necessary (Session-Cookie ohne Expire-Date)")
            return "Strictly Necessary"
            
        # Heuristik 2: Cookies mit langer Lebensdauer sind oft "Targeting"
        if isinstance(cookie.get("expires", 0), (int, float)) and cookie.get("expires", 0) > 15552000:  # > 180 Tage
            logger.debug(f"Heuristische Klassifikation für {name}: Targeting (Lange Lebensdauer)")
            return "Targeting"
            
        # Heuristik 3: Kurze, zufällig aussehende Namen ohne Expire-Date sind oft "Performance"
        if len(name) <= 5 and name.isalnum() and not name.isalpha():
            logger.debug(f"Heuristische Klassifikation für {name}: Performance (Kurzer, zufälliger Name)")
            return "Performance"
        
        # Wenn keine Regel greift, als "Other" kategorisieren
        return "Other"


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
        from .database import find_cookie_info  # Import at function level to avoid circular imports
        
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
                if ("canvas" in key_lower and len(value) > 500) or "canvasfingerprint" in key_lower:
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
