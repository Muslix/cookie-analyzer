#!/usr/bin/env python3
from cookie_analyzer.interface import analyze_website
from cookie_analyzer.utils import setup_logging, save_results_as_json, validate_url, Config
from cookie_analyzer.database import update_cookie_database, get_alternative_cookie_databases
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
    
    respect_robots = not args.no_robots
    logger.info(f"Starte Analyse von {url} mit max. {args.pages} Seiten (robots.txt {'wird beachtet' if respect_robots else 'wird ignoriert'})")
    
    # Website analysieren
    try:
        classified_cookies, local_storage, available_cookies = analyze_website(
            url, 
            max_pages=args.pages, 
            database_path=args.database,
            show_available=args.all_available
        )
        
        # Ergebnis für die Ausgabe aufbereiten
        result = {
            "cookies": classified_cookies,
            "local_storage": local_storage
        }
        
        if args.all_available:
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
                    print(f"  Ablaufzeit: {cookie.get('expires', 'Unbekannt')}")
                    print(f"  Domain: {cookie.get('domain', 'Unbekannt')}")
                    
            if args.all_available and available_cookies:
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
                    
            print("\n=== Local Storage ===")
            for url, storage in local_storage.items():
                print(f"\nLocal Storage für {url}:")
                if not storage:  # Prüfe, ob Storage leer ist
                    print("  Keine Einträge gefunden")
                else:
                    for key, value in storage.items():
                        print(f"- {key}: {value}")
                    
    except Exception as e:
        logger.error(f"Fehler bei der Analyse: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

