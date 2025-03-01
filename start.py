#!/usr/bin/env python3
from cookie_analyzer.interface.wrapper import analyze_website
from cookie_analyzer.utils.logging import setup_logging
from cookie_analyzer.utils.export import save_results_as_json
from cookie_analyzer.utils.url import validate_url
from cookie_analyzer.utils.config import Config
from cookie_analyzer.database.updater import update_cookie_database, get_alternative_cookie_databases
from cookie_analyzer.services.crawler_factory import CrawlerType
from cookie_analyzer.services.initializer import get_cookie_classifier_service

import argparse
import logging
import sys
import json

def main():
    # Konfiguration aus Datei laden
    config_dict = Config.load_from_file()
    
    # Logging einrichten
    log_level = Config.get_log_level(config_dict)
    setup_logging(Config.DEFAULT_LOG_FILE, log_level)
    
    logger = logging.getLogger(__name__)
    
    # Argument-Parser einrichten
    parser = argparse.ArgumentParser(description="Cookie Analyzer - Ein Tool zur Cookie-Analyse von Websites")
    parser.add_argument("url", nargs="?", help="URL der zu analysierenden Website")
    parser.add_argument("-p", "--pages", type=int, 
                        default=Config.get_max_pages(config_dict), 
                        help=f"Maximale Anzahl von Seiten zum Crawlen (Standard: {Config.get_max_pages(config_dict)})")
    parser.add_argument("-d", "--database", 
                        default=Config.get_database_path(config_dict), 
                        help=f"Pfad zur Cookie-Datenbank (Standard: {Config.get_database_path(config_dict)})")
    parser.add_argument("-j", "--json", action="store_true", help="Ausgabe im JSON-Format")
    parser.add_argument("-o", "--output", help="Speichert die Ergebnisse in einer JSON-Datei")
    parser.add_argument("-n", "--no-robots", action="store_true", 
                        help="Ignoriert robots.txt (nicht empfohlen)")
    parser.add_argument("-u", "--update-db", action="store_true",
                        help="Aktualisiert die Cookie-Datenbank vor der Analyse")
    parser.add_argument("--list-alternatives", action="store_true",
                        help="Zeigt alternative Cookie-Datenbanken an und beendet das Programm")
    parser.add_argument("-a", "--all-available", action="store_true",
                        help="Zeigt auch potenziell verfügbare Cookies an")
    
    # Neue Argumente für erweiterte Funktionen
    parser.add_argument("-s", "--selenium", action="store_true", 
                        help="Verwendet Selenium für erweiterte Cookie-Erfassung und Consent-Interaktion")
    parser.add_argument("--async", dest="use_async", action="store_true", 
                        help="Verwendet asynchrone Verarbeitung für bessere Performance bei mehreren Seiten")
    parser.add_argument("--no-consent", action="store_true", 
                        help="Deaktiviert die automatische Interaktion mit Cookie-Consent-Bannern")
    parser.add_argument("--show-browser", action="store_true", 
                        help="Zeigt den Browser während der Analyse (kein Headless-Modus)")
    parser.add_argument("--fingerprinting", action="store_true", 
                        help="Analysiert und zeigt potenzielle Fingerprinting-Techniken")
    parser.add_argument("--dynamic", action="store_true", 
                        help="Zeigt dynamisch gesetzte Cookies getrennt an")
    parser.add_argument("--full", action="store_true",
                        help="Aktiviert alle Analyse-Features (Selenium, Fingerprinting, dynamische Cookies)")
    
    args = parser.parse_args()
    
    # Zeige alternative Datenbanken an, wenn gewünscht
    if args.list_alternatives:
        print("\nAlternative Cookie-Datenbanken:")
        alternatives = get_alternative_cookie_databases()
        for name, url in alternatives.items():
            print(f"- {name}: {url}")
        return
    
    # Datenbank aktualisieren, wenn gewünscht
    if args.update_db:
        print("Aktualisiere Cookie-Datenbank...")
        if update_cookie_database(args.database):
            print("Cookie-Datenbank erfolgreich aktualisiert!")
        else:
            print("Fehler beim Aktualisieren der Cookie-Datenbank.")
            if not args.url:
                return
    
    # Falls keine URL angegeben wurde, interaktiv nachfragen
    url = args.url
    if not url:
        url = input("Bitte geben Sie die URL der zu analysierenden Website ein: ")
        if not url:
            logger.error("Keine URL angegeben. Beende Programm.")
            sys.exit(1)
    
    # URL validieren und ggf. Schema hinzufügen
    validated_url = validate_url(url)
    if not validated_url:
        logger.error(f"Ungültige URL: {url}")
        sys.exit(1)
    
    # Verwende die validierte URL
    url = validated_url
    
    # Wenn --full angegeben oder wenn keine speziellen Parameter angegeben wurden, 
    # aktiviere alle Features
    if args.full or (not any([args.selenium, args.use_async, args.fingerprinting, args.dynamic])):
        args.selenium = True
        args.fingerprinting = True
        args.dynamic = True
    
    respect_robots = not args.no_robots
    crawler_type = CrawlerType.SELENIUM if args.selenium else (
        CrawlerType.PLAYWRIGHT_ASYNC if args.use_async else CrawlerType.PLAYWRIGHT
    )
    
    logger.info(f"Starte Analyse von {url} mit max. {args.pages} Seiten "
               f"(robots.txt {'wird beachtet' if respect_robots else 'wird ignoriert'}, "
               f"Crawler-Typ: {crawler_type})")
    
    # Website analysieren
    try:
        classified_cookies, storage_data = analyze_website(
            url, 
            max_pages=args.pages, 
            database_path=args.database,
            use_async=args.use_async,
            use_selenium=args.selenium,
            interact_with_consent=not args.no_consent,
            headless=not args.show_browser
        )
        
        # Fingerprinting-Analyse durchführen, wenn gewünscht
        fingerprinting_data = None
        if args.fingerprinting:
            cookie_classifier = get_cookie_classifier_service()
            all_cookies = []
            for category, cookies in classified_cookies.items():
                all_cookies.extend(cookies)
            fingerprinting_data = cookie_classifier.identify_fingerprinting(all_cookies, storage_data)
        
        # Ergebnis für die Ausgabe aufbereiten
        result = {
            "cookies": classified_cookies,
            "storage": storage_data
        }
        
        if fingerprinting_data:
            result["fingerprinting"] = fingerprinting_data
            
        if args.all_available and 'available_cookies' in locals():
            result["available_cookies"] = available_cookies
        
        # In Datei speichern, wenn gewünscht
        if args.output:
            save_results_as_json(result, args.output)
        
        # Ausgabe im gewünschten Format
        if args.json:
            # JSON-Ausgabe auf der Konsole
            print(json.dumps(result, indent=2))
        else:
            # Formatierte Textausgabe
            print("\n=== Aktuelle Cookie-Analyse ===")
            for category, cookie_list in classified_cookies.items():
                print(f"\n{category} ({len(cookie_list)}):")
                for cookie in cookie_list:
                    print(f"- {cookie['name']}:")
                    print(f"  Beschreibung: {cookie.get('description', 'Keine Beschreibung')}")
                    print(f"  Kategorie: {cookie.get('category', 'Unbekannt')}")
                    print(f"  Klassifizierungsmethode: {cookie.get('classification_method', 'Unbekannt')}")
                    print(f"  Ablaufzeit: {cookie.get('expires', 'Unbekannt')}")
                    print(f"  Domain: {cookie.get('domain', 'Unbekannt')}")
                    
            if args.all_available and 'available_cookies' in locals():
                print("\n=== Verfügbare/Mögliche Cookies ===")
                print("Diese Cookies könnten gesetzt werden, wenn der Benutzer zustimmt:\n")
                for category, cookie_list in available_cookies.items():
                    if cookie_list:  # Zeige nur Kategorien mit Cookies
                        print(f"\n{category} ({len(cookie_list)}):")
                        for cookie in cookie_list:
                            print(f"- {cookie['name']}:")
                            print(f"  Beschreibung: {cookie.get('description', 'Keine Beschreibung')}")
                            print(f"  Kategorie: {cookie.get('category', 'Unbekannt')}")
                            print(f"  Anbieter: {cookie.get('vendor', 'Unbekannt')}")
                            print(f"  Ablaufzeit: {cookie.get('expiration', 'Unbekannt')}")
                            if 'domain' in cookie:
                                print(f"  Domain: {cookie['domain']}")
            
            # Web Storage-Ausgabe
            print("\n=== Web Storage ===")
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
                print("\n=== Fingerprinting-Analyse ===")
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
    main()

