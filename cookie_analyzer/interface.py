from .core import crawl_website
from .cookie_handler import classify_cookies
from .database import load_cookie_database
from .utils import Config, setup_logging
import argparse
import logging
import sys
import json
from typing import Dict, List, Any, Tuple

def analyze_website(url: str, max_pages: int = None, database_path: str = None) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Dict[str, str]]]:
    """
    Analysiert eine Website und liefert klassifizierte Cookies zurück.
    
    Args:
        url (str): Die URL der Website, die analysiert werden soll.
        max_pages (int, optional): Maximale Anzahl von Seiten, die gecrawlt werden sollen.
        database_path (str, optional): Pfad zur Cookie-Datenbank (CSV-Datei).
    
    Returns:
        Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Dict[str, str]]]: 
            - Klassifizierte Cookies nach Kategorien.
            - Local Storage Daten.
    """
    # Standardwerte aus Config verwenden, wenn nicht angegeben
    if max_pages is None:
        max_pages = Config.DEFAULT_MAX_PAGES
    if database_path is None:
        database_path = Config.DEFAULT_DATABASE_PATH
        
    # Lade die Cookie-Datenbank
    cookie_database = load_cookie_database(database_path)
    # Scanne die Website
    cookies, local_storage = crawl_website(url, max_pages=max_pages)
    # Klassifiziere Cookies
    return classify_cookies(cookies, cookie_database), local_storage

def cli_main() -> None:
    """
    Command Line Interface für Cookie Analyzer.
    Diese Funktion wird als Einstiegspunkt für die Kommandozeilen-Verwendung verwendet.
    """
    # Konfiguration laden
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
    
    args = parser.parse_args()
    
    # Falls keine URL angegeben wurde, interaktiv nachfragen
    url = args.url
    if not url:
        url = input("Bitte geben Sie die URL der zu analysierenden Website ein: ")
        if not url:
            logger.error("Keine URL angegeben. Beende Programm.")
            sys.exit(1)
    
    logger.info(f"Starte Analyse von {url} mit max. {args.pages} Seiten")
    
    # Website analysieren
    try:
        classified_cookies, local_storage = analyze_website(
            url, 
            max_pages=args.pages, 
            database_path=args.database
        )
        
        # Ausgabe im gewünschten Format
        if args.json:
            # JSON-Ausgabe
            result = {
                "cookies": classified_cookies,
                "local_storage": local_storage
            }
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
                    print(f"  Ablaufzeit: {cookie.get('expires', 'Unbekannt')}")
                    print(f"  Domain: {cookie.get('domain', 'Unbekannt')}")
                    
            print("\n--- Local Storage ---")
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
    cli_main()
