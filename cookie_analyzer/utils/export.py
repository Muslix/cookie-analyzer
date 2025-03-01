"""
Export-Funktionalitäten für den Cookie-Analyzer.
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

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
        logger.error(f"Fehler beim Speichern der JSON-Datei - {e}")
        return False