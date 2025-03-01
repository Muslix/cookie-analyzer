"""
Kommandozeilen-Schnittstelle für den Cookie-Analyzer.
"""

import argparse
import logging
import sys
import json
from typing import Dict, List, Any, Tuple, Optional

from ..core.analyzer import CookieAnalyzer
from ..utils.config import Config
from ..utils.url import validate_url
from ..utils.logging import setup_logging
from ..services.provider import ServiceProvider
from ..services.initializer import initialize_services, get_cookie_classifier_service
from ..services.crawler_factory import CrawlerType
from .wrapper import analyze_website

logger = logging.getLogger(__name__)

def cli_main() -> None:
    """Haupt-Einstiegspunkt für die Kommandozeilen-Schnittstelle."""
    # Logging einrichten
    setup_logging()
    
    # Konfiguration laden
    config_dict = Config.load_from_file()
    
    # Command-Line-Argumente parsen
    parser = argparse.ArgumentParser(description="Cookie-Analyzer: Analysiert Cookies auf Websites")
    parser.add_argument("url", nargs="?", help="URL der zu analysierenden Website")
    parser.add_argument("-p", "--pages", type=int, 
                        default=Config.get_max_pages(config_dict),
                        help=f"Maximale Anzahl von Seiten, die gecrawlt werden sollen (Standard: {Config.get_max_pages(config_dict)})")
    parser.add_argument("-d", "--database", 
                        default=Config.get_database_path(config_dict),
                        help=f"Pfad zur Cookie-Datenbank (Standard: {Config.get_database_path(config_dict)})")
    parser.add_argument("-j", "--json", action="store_true", help="Ausgabe im JSON-Format")
    parser.add_argument("-a", "--async", dest="use_async", action="store_true", 
                        help="Asynchrone Verarbeitung für bessere Performance")
    
    # Neue Argumente für erweiterte Funktionen
    parser.add_argument("-s", "--selenium", action="store_true", 
                        help="Verwendet Selenium für erweiterte Cookie-Erfassung und Consent-Interaktion")
    parser.add_argument("--no-consent-interaction", action="store_true", 
                        help="Deaktiviert die automatische Interaktion mit Cookie-Consent-Bannern")
    parser.add_argument("--show-browser", action="store_true", 
                        help="Zeigt den Browser bei Verwendung von Selenium (kein Headless-Modus)")
    parser.add_argument("--fingerprinting", action="store_true", 
                        help="Analysiert und zeigt Fingerprinting-Techniken")
    parser.add_argument("--dynamic", action="store_true", 
                        help="Zeigt dynamisch gesetzte Cookies getrennt an")
    
    args = parser.parse_args()
    
    # Falls keine URL angegeben wurde, interaktiv nachfragen
    url = args.url
    if not url:
        url = input("Bitte geben Sie die URL der zu analysierenden Website ein: ")
        if not url:
            logger.error("Keine URL angegeben. Beende Programm.")
            sys.exit(1)
    
    # URL validieren
    validated_url = validate_url(url)
    if not validated_url:
        logger.error(f"Ungültige URL: {url}")
        sys.exit(1)
    url = validated_url
    
    logger.info(f"Starte Analyse von {url} mit max. {args.pages} Seiten" + 
               (" (asynchron)" if args.use_async else "") + 
               (" mit Selenium" if args.selenium else ""))
    
    # Stellen Sie sicher, dass die Services initialisiert sind
    initialize_services()
    
    # Website analysieren
    try:
        classified_cookies, storage_data = analyze_website(
            url, 
            max_pages=args.pages, 
            database_path=args.database,
            use_async=args.use_async,
            use_selenium=args.selenium,
            interact_with_consent=not args.no_consent_interaction,
            headless=not args.show_browser
        )
        logger.info("Analyse erfolgreich abgeschlossen")
        
        # Fingerprinting-Analyse durchführen, wenn angefordert
        fingerprinting_data = None
        if args.fingerprinting:
            cookie_classifier = get_cookie_classifier_service()
            all_cookies = []
            for category, cookies in classified_cookies.items():
                all_cookies.extend(cookies)
            fingerprinting_data = cookie_classifier.identify_fingerprinting(all_cookies, storage_data)
        
        # Ausgabe im gewünschten Format
        if args.json:
            # JSON-Ausgabe
            result = {
                "cookies": classified_cookies,
                "storage": storage_data
            }
            
            # Füge Fingerprinting-Daten hinzu, wenn vorhanden
            if fingerprinting_data:
                result["fingerprinting"] = fingerprinting_data
                
            print(json.dumps(result, indent=2))
        else:
            # Formatierte Textausgabe
            print("\n--- Cookie-Analyse ---")
            for category, cookie_list in classified_cookies.items():
                print(f"\n{category} ({len(cookie_list)}):")
                for cookie in cookie_list:
                    print(f"- {cookie['name']}:")
                    print(f"  Beschreibung: {cookie.get('description', 'Keine Beschreibung')}")
                    print(f"  Kategorie: {cookie.get('category', 'Unbekannt')}")
                    print(f"  Klassifizierungsmethode: {cookie.get('classification_method', 'Unbekannt')}")
                    print(f"  Ablaufzeit: {cookie.get('expires', 'Unbekannt')}")
                    print(f"  Domain: {cookie.get('domain', 'Unbekannt')}")
                    
            # Web Storage-Ausgabe
            print("\n--- Web Storage ---")
            for url, storage in storage_data.items():
                print(f"\nStorage für {url}:")
                
                # Local Storage
                local_storage = storage.get("localStorage", {})
                if local_storage:
                    print("\nLocal Storage:")
                    for key, value in local_storage.items():
                        print(f"- {key}: {value}")
                else:
                    print("Keine Local Storage-Einträge gefunden")
                
                # Session Storage (nur bei Selenium)
                session_storage = storage.get("sessionStorage", {})
                if session_storage:
                    print("\nSession Storage:")
                    for key, value in session_storage.items():
                        print(f"- {key}: {value}")
                
                # Dynamische Cookies (nur bei Selenium und wenn --dynamic angegeben)
                if args.dynamic and "dynamicCookies" in storage:
                    dynamic_cookies = storage.get("dynamicCookies", [])
                    if dynamic_cookies:
                        print("\nDynamisch gesetzte Cookies:")
                        for cookie in dynamic_cookies:
                            print(f"- {cookie['name']}: {cookie.get('value', '(kein Wert)')}")
            
            # Fingerprinting-Ausgabe
            if fingerprinting_data:
                print("\n--- Fingerprinting-Analyse ---")
                fingerprinting_detected = any(fingerprinting_data.values())
                if fingerprinting_detected:
                    print("Potenzielle Fingerprinting-Techniken erkannt:")
                    for tech, detected in fingerprinting_data.items():
                        if detected:
                            print(f"- {tech.replace('_', ' ').title()}")
                else:
                    print("Keine Fingerprinting-Techniken erkannt.")
                    
    except Exception as e:
        logger.error(f"Fehler bei der Analyse: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli_main()