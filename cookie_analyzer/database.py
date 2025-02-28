import csv
import logging
import re
from typing import Dict, List, Any, Optional
import requests
import os
from datetime import datetime
from .utils import Config

logger = logging.getLogger(__name__)

def load_cookie_database(file_path: str = None) -> List[Dict[str, Any]]:
    """
    Lädt die Open Cookie Database aus einer CSV-Datei und extrahiert alle relevanten Informationen.
    
    Args:
        file_path: Pfad zur CSV-Datei mit der Cookie-Datenbank. Falls None, wird der Standardpfad verwendet.
        
    Returns:
        Liste mit Cookie-Informationen aus der Datenbank
    """
    # Standard-Datenbankpfad verwenden, wenn keiner angegeben ist
    if file_path is None:
        file_path = Config.DEFAULT_DATABASE_PATH
        
    cookie_database = []
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader, None)  # Überspringe Header-Zeile wenn vorhanden
            
            for row in csv_reader:
                if len(row) >= 10:
                    cookie_database.append({
                        "ID": row[0],
                        "Vendor": row[1],
                        "Category": row[2],
                        "Cookie Name": row[3],
                        "Value": row[4],
                        "Description": row[5],
                        "Expiration": row[6],
                        "Vendor Website": row[7],
                        "Privacy Policy": row[8],
                        "Wildcard match": row[9] == "1"
                    })
                else:
                    logger.warning(f"Ignoriere unvollständige Zeile: {row}")
                    
        logger.info(f"{len(cookie_database)} Cookie-Einträge aus der Datenbank geladen")
    except Exception as e:
        logger.error(f"Fehler beim Laden der Cookie-Datenbank: {e}")
    
    return cookie_database

def find_cookie_info(cookie_name: str, cookie_database: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Sucht nach Informationen zu einem Cookie in der Open Cookie Database.
    
    Args:
        cookie_name: Der Name des zu suchenden Cookies
        cookie_database: Die Cookie-Datenbank
        
    Returns:
        Dictionary mit Informationen zum Cookie oder Standardwerte, falls nicht gefunden
    """
    # Exakte Übereinstimmung zuerst prüfen
    for cookie in cookie_database:
        if not cookie["Wildcard match"] and cookie["Cookie Name"].lower() == cookie_name.lower():
            return cookie
    
    # Dann Wildcard-Übereinstimmungen prüfen
    for cookie in cookie_database:
        if cookie["Wildcard match"]:
            pattern = cookie["Cookie Name"].replace("*", ".*")
            if re.match(f"^{pattern}$", cookie_name, re.IGNORECASE):
                return cookie
            
            # Auch prüfen, ob der Cookie mit einem Präfix beginnt (für _ga* etc.)
            base_name = cookie["Cookie Name"].replace("*", "")
            if cookie_name.lower().startswith(base_name.lower()):
                return cookie
    
    return {"Description": "Keine Beschreibung verfügbar.", "Category": "Unknown"}

def update_cookie_database(output_path: str = None, 
                          url: str = None) -> bool:
    """
    Aktualisiert die Cookie-Datenbank aus dem GitHub-Repository.
    
    Args:
        output_path: Pfad, wohin die aktualisierte Datenbank gespeichert werden soll
        url: URL der aktuellen CSV-Datei im GitHub-Repository
    
    Returns:
        True, wenn die Aktualisierung erfolgreich war, sonst False
    """
    # Standardwerte aus der Konfiguration verwenden, wenn nicht angegeben
    if output_path is None:
        output_path = Config.DEFAULT_DATABASE_PATH
    if url is None:
        url = Config.GITHUB_DATABASE_URL
        
    try:
        # Backup der vorhandenen Datei erstellen, falls sie existiert
        if os.path.exists(output_path):
            backup_path = f"{output_path}.backup-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            os.rename(output_path, backup_path)
            logger.info(f"Backup der Cookie-Datenbank erstellt: {backup_path}")
        
        # Neue Datenbank herunterladen
        logger.info(f"Lade aktuelle Cookie-Datenbank von {url} herunter...")
        response = requests.get(url)
        response.raise_for_status()  # Wirft eine Ausnahme bei HTTP-Fehlern
        
        # Speichern der heruntergeladenen Datenbank
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        # Validierung der heruntergeladenen Datei
        try:
            cookie_db = load_cookie_database(output_path)
            if not cookie_db:
                raise ValueError("Heruntergeladene Datenbank scheint leer zu sein")
                
            logger.info(f"Cookie-Datenbank erfolgreich aktualisiert mit {len(cookie_db)} Einträgen")
            return True
            
        except Exception as e:
            # Bei Fehler in der neuen Datei, Backup wiederherstellen
            logger.error(f"Fehler bei der Validierung der neuen Datenbank: {e}")
            if os.path.exists(backup_path):
                os.rename(backup_path, output_path)
                logger.info(f"Backup der Datenbank wiederhergestellt")
            return False
            
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren der Cookie-Datenbank: {e}")
        return False

def get_alternative_cookie_databases() -> Dict[str, str]:
    """
    Gibt eine Liste alternativer Cookie-Datenbanken mit ihren URLs zurück.
    
    Returns:
        Dict mit Namen und URLs der alternativen Datenbanken
    """
    return {
        "Open Cookie Database (Standard)": Config.GITHUB_DATABASE_URL,
        "Cookiepedia API": "https://cookiepedia.co.uk/api/ (Registrierung erforderlich)",
        "Cookiebot": "https://www.cookiebot.com/ (Kostenpflichtig)",
        "OneTrust": "https://www.onetrust.com/products/cookie-consent/ (Kostenpflichtig)"
    }
