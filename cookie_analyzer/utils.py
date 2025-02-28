import logging
from typing import List, Dict, Any, Tuple, Optional, Union
from urllib.parse import urlparse
import csv
import os
import json
import configparser

logger = logging.getLogger(__name__)

class Config:
    """Zentrale Konfigurationsklasse für alle statischen Werte im Projekt."""

    # Standardwerte
    DEFAULT_DATABASE_PATH = "open-cookie-database.csv"
    DEFAULT_MAX_PAGES = 5
    DEFAULT_RESPECT_ROBOTS = True
    DEFAULT_LOG_LEVEL = "INFO"
    DEFAULT_LOG_FILE = "cookie_analyzer.log"
    
    # GitHub-URLs für Datenbankaktualisierung
    GITHUB_DATABASE_URL = "https://raw.githubusercontent.com/jkwakman/Open-Cookie-Database/master/open-cookie-database.csv"
    
    @classmethod
    def load_from_file(cls, config_file: str = "config.ini") -> Dict[str, Any]:
        """
        Lädt die Konfiguration aus einer INI-Datei.
        
        Args:
            config_file: Pfad zur Konfigurationsdatei
            
        Returns:
            Dict mit Konfigurationswerten
        """
        config = configparser.ConfigParser()
        
        # Standardwerte
        config["DEFAULT"] = {
            "max_pages": str(cls.DEFAULT_MAX_PAGES),
            "respect_robots_txt": str(cls.DEFAULT_RESPECT_ROBOTS),
            "database_path": cls.DEFAULT_DATABASE_PATH,
            "log_level": cls.DEFAULT_LOG_LEVEL
        }
        
        # Lade bestehende Konfiguration wenn vorhanden
        if os.path.exists(config_file):
            try:
                config.read(config_file)
                logger.info(f"Konfiguration aus {config_file} geladen")
            except Exception as e:
                log_error(f"Fehler beim Laden der Konfiguration aus {config_file}", e)
        else:
            # Erstelle neue Konfigurationsdatei mit Standardwerten
            try:
                with open(config_file, "w") as f:
                    config.write(f)
                logger.info(f"Neue Konfigurationsdatei {config_file} mit Standardwerten erstellt")
            except Exception as e:
                log_error(f"Fehler beim Erstellen der Konfigurationsdatei {config_file}", e)
        
        # Konfiguration in Dict umwandeln
        return dict(config["DEFAULT"])
    
    @classmethod
    def get_database_path(cls, config_dict: Dict[str, Any] = None) -> str:
        """
        Gibt den Pfad zur Cookie-Datenbank aus der Konfiguration zurück.
        
        Args:
            config_dict: Optionales Dict mit Konfigurationswerten
            
        Returns:
            Pfad zur Cookie-Datenbank
        """
        if config_dict:
            return config_dict.get("database_path", cls.DEFAULT_DATABASE_PATH)
        return cls.DEFAULT_DATABASE_PATH
    
    @classmethod
    def get_max_pages(cls, config_dict: Dict[str, Any] = None) -> int:
        """
        Gibt die maximale Anzahl zu crawlender Seiten aus der Konfiguration zurück.
        
        Args:
            config_dict: Optionales Dict mit Konfigurationswerten
            
        Returns:
            Maximale Anzahl zu crawlender Seiten
        """
        if config_dict:
            return int(config_dict.get("max_pages", cls.DEFAULT_MAX_PAGES))
        return cls.DEFAULT_MAX_PAGES
    
    @classmethod
    def get_respect_robots(cls, config_dict: Dict[str, Any] = None) -> bool:
        """
        Gibt zurück, ob robots.txt respektiert werden soll.
        
        Args:
            config_dict: Optionales Dict mit Konfigurationswerten
            
        Returns:
            True, wenn robots.txt respektiert werden soll
        """
        if config_dict:
            return config_dict.get("respect_robots_txt", "True").lower() == "true"
        return cls.DEFAULT_RESPECT_ROBOTS
    
    @classmethod
    def get_log_level(cls, config_dict: Dict[str, Any] = None) -> int:
        """
        Gibt das Log-Level aus der Konfiguration zurück.
        
        Args:
            config_dict: Optionales Dict mit Konfigurationswerten
            
        Returns:
            Log-Level (z.B. logging.INFO)
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        
        if config_dict:
            level_str = config_dict.get("log_level", cls.DEFAULT_LOG_LEVEL).upper()
            return level_map.get(level_str, logging.INFO)
        return level_map.get(cls.DEFAULT_LOG_LEVEL, logging.INFO)

def setup_logging(log_file: str = "cookie_analyzer.log", log_level: int = logging.INFO) -> None:
    """
    Richtet das Logging für die Anwendung ein.
    
    Args:
        log_file: Pfad zur Log-Datei
        log_level: Logging-Level (z.B. logging.INFO, logging.DEBUG)
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def log_error(message: str, exception: Exception) -> None:
    """
    Protokolliert einen Fehler mit Nachricht und Exception.
    
    Args:
        message: Fehlermeldung
        exception: Die aufgetretene Exception
    """
    logger.error(f"{message} - {exception}")

def validate_url(url: str) -> str:
    """
    Validiert eine URL und fügt das Schema hinzu, wenn es fehlt.
    
    Args:
        url: Die zu validierende URL
        
    Returns:
        Die validierte URL mit Schema oder leerer String bei ungültiger URL
    """
    # Schema hinzufügen, wenn es fehlt
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    try:
        parsed = urlparse(url)
        if parsed.netloc:
            return url
        return ""
    except Exception as e:
        log_error(f"Ungültige URL: {url}", e)
        return ""

def read_csv(file_path: str) -> List[List[str]]:
    """
    Liest eine CSV-Datei und gibt die Zeilen zurück.
    
    Args:
        file_path: Pfad zur CSV-Datei
        
    Returns:
        Liste von Listen mit CSV-Zeilen
    """
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            return list(csv.reader(file))
    except Exception as e:
        log_error("Fehler beim Lesen der CSV-Datei", e)
        return []

def validate_csv_headers(headers: List[str], required_headers: List[str]) -> bool:
    """
    Prüft, ob alle erforderlichen Header in der CSV-Datei vorhanden sind.
    
    Args:
        headers: Die vorhandenen Header
        required_headers: Die erforderlichen Header
        
    Returns:
        True wenn alle erforderlichen Header vorhanden sind, sonst False
    """
    missing_headers = [header for header in required_headers if header not in headers]
    if missing_headers:
        log_error("Fehlende CSV-Header", Exception(f"{missing_headers}"))
        return False
    return True

def save_results_as_json(data: Dict[str, Any], output_file: str = "cookie_analysis.json") -> bool:
    """
    Speichert die Ergebnisse als JSON-Datei.
    
    Args:
        data: Die zu speichernden Daten
        output_file: Pfad zur Ausgabedatei
        
    Returns:
        True bei Erfolg, sonst False
    """
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Ergebnisse wurden in {output_file} gespeichert")
        return True
    except Exception as e:
        log_error("Fehler beim Speichern der JSON-Datei", e)
        return False

def load_config(config_file: str = "config.ini") -> configparser.ConfigParser:
    """
    Lädt die Konfiguration aus einer INI-Datei oder erstellt eine Standardkonfiguration.
    
    Args:
        config_file: Pfad zur Konfigurationsdatei
        
    Returns:
        ConfigParser-Objekt mit der Konfiguration
    """
    config = configparser.ConfigParser()
    
    # Standardwerte
    config["DEFAULT"] = {
        "max_pages": "5",
        "respect_robots_txt": "True",
        "database_path": "open-cookie-database.csv",
        "log_level": "INFO"
    }
    
    # Lade bestehende Konfiguration wenn vorhanden
    if os.path.exists(config_file):
        try:
            config.read(config_file)
            logger.info(f"Konfiguration aus {config_file} geladen")
        except Exception as e:
            log_error(f"Fehler beim Laden der Konfiguration aus {config_file}", e)
    else:
        # Erstelle neue Konfigurationsdatei mit Standardwerten
        try:
            with open(config_file, "w") as f:
                config.write(f)
            logger.info(f"Neue Konfigurationsdatei {config_file} mit Standardwerten erstellt")
        except Exception as e:
            log_error(f"Fehler beim Erstellen der Konfigurationsdatei {config_file}", e)
    
    return config
