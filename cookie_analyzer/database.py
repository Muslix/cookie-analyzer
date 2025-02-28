import csv
import logging
import re
from typing import Dict, List, Any, Optional
import requests
import os
from datetime import datetime
from .utils import Config

logger = logging.getLogger(__name__)

class DatabaseHandler:
    """Handles all cookie database operations."""
    
    def load_database(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lädt die Cookie-Datenbank aus einer CSV-Datei.
        
        Args:
            file_path: Pfad zur CSV-Datei mit der Cookie-Datenbank.
            
        Returns:
            Liste von Cookie-Einträgen aus der Datenbank.
        """
        if file_path is None:
            file_path = Config.DEFAULT_DATABASE_PATH
        
        cookie_database = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)  # Headers überspringen
                
                for row in reader:
                    if len(row) >= 10:  # Sicherstellen, dass die Zeile vollständig ist
                        cookie_database.append({
                            "ID": row[0],
                            "Parent Organization": row[1],
                            "Vendor": row[2],
                            "Cookie Name": row[3],
                            "Value": row[4],
                            "Description": row[5],
                            "Expiration": row[6],
                            "Vendor Website": row[7],
                            "Privacy Policy": row[8],
                            "Wildcard match": row[9] == "1",
                            "Category": row[10] if len(row) > 10 else "Unknown"
                        })
                    else:
                        logger.warning(f"Ignoriere unvollständige Zeile: {row}")
                        
            logger.info(f"{len(cookie_database)} Cookie-Einträge aus der Datenbank geladen")
        except Exception as e:
            logger.error(f"Fehler beim Laden der Cookie-Datenbank: {e}")
        
        return cookie_database
    
    def find_cookie_info(self, cookie_name: str, cookie_database: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Findet Informationen zu einem bestimmten Cookie in der Datenbank.
        
        Args:
            cookie_name: Der Name des Cookies
            cookie_database: Die Cookie-Datenbank
            
        Returns:
            Dictionary mit den Informationen zum Cookie oder Standardwerte
        """
        # Direkte Übereinstimmung
        for cookie in cookie_database:
            if cookie["Cookie Name"].lower() == cookie_name.lower():
                return cookie
        
        # Wildcard-Übereinstimmung prüfen
        for cookie in cookie_database:
            if cookie.get("Wildcard match", False) and "*" in cookie["Cookie Name"]:
                pattern = cookie["Cookie Name"].replace("*", ".*")
                if re.match(pattern, cookie_name, re.IGNORECASE):
                    return cookie
                
                # Alternative: Prüfen, ob der Cookie mit dem Basis-Namen beginnt (ohne *)
                base_name = cookie["Cookie Name"].replace("*", "")
                if cookie_name.lower().startswith(base_name.lower()):
                    return cookie
        
        return {"Description": "Keine Beschreibung verfügbar.", "Category": "Unknown"}
    
    def update_database(self, output_path: Optional[str] = None, url: Optional[str] = None) -> bool:
        """
        Aktualisiert die Cookie-Datenbank aus einer Online-Quelle.
        
        Args:
            output_path: Pfad, unter dem die aktualisierte Datenbank gespeichert werden soll.
            url: URL zur aktuellen Datenbank (optional, sonst wird die Standard-URL verwendet).
            
        Returns:
            True, wenn die Aktualisierung erfolgreich war, sonst False.
        """
        if output_path is None:
            output_path = Config.DEFAULT_DATABASE_PATH
            
        if url is None:
            url = Config.GITHUB_DATABASE_URL
            
        # Backup der aktuellen Datenbank erstellen
        backup_path = f"{output_path}.bak"
        try:
            if os.path.exists(output_path):
                os.rename(output_path, backup_path)
                logger.info(f"Backup der Datenbank erstellt: {backup_path}")
                
            # Neue Datenbank herunterladen
            logger.info(f"Lade aktuelle Cookie-Datenbank von {url} herunter...")
            response = requests.get(url)
            response.raise_for_status()  # Wirft eine Ausnahme bei HTTP-Fehlern
            
            # Speichern der heruntergeladenen Datenbank
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # Validierung der heruntergeladenen Datei
            try:
                cookie_db = self.load_database(output_path)
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
    Liefert eine Liste alternativer Cookie-Datenbanken.
    
    Returns:
        Dictionary mit Namen und URLs zu alternativen Cookie-Datenbanken
    """
    return {
        "Open Cookie Database (GitHub)": Config.GITHUB_DATABASE_URL,
    }


# Legacy-Funktionen für Abwärtskompatibilität
def load_cookie_database(file_path: str = None) -> List[Dict[str, Any]]:
    """Legacy-Funktion für Abwärtskompatibilität."""
    handler = DatabaseHandler()
    return handler.load_database(file_path)

def find_cookie_info(cookie_name: str, cookie_database: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Legacy-Funktion für Abwärtskompatibilität."""
    handler = DatabaseHandler()
    return handler.find_cookie_info(cookie_name, cookie_database)

def update_cookie_database(output_path: str = None, url: str = None) -> bool:
    """Legacy-Funktion für Abwärtskompatibilität."""
    handler = DatabaseHandler()
    return handler.update_database(output_path, url)
