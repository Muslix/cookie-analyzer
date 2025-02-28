from .database import find_cookie_info
from typing import Dict, List, Any, Tuple

def classify_cookies(cookies: List[Dict[str, Any]], cookie_database: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Klassifiziert Cookies und ergänzt Informationen aus der Cookie-Datenbank.
    
    Args:
        cookies: Liste der zu klassifizierenden Cookies
        cookie_database: Die Cookie-Datenbank mit Klassifikationsinformationen
        
    Returns:
        Dictionary mit klassifizierten Cookies nach Kategorien
    """
    classified = {
        "Strictly Necessary": [],
        "Performance": [],
        "Targeting": [],
        "Other": []
    }
    for cookie in cookies:
        cookie_info = find_cookie_info(cookie["name"], cookie_database)
        cookie.update({
            "description": cookie_info.get("Description", "Keine Beschreibung verfügbar."),
            "category": cookie_info.get("Category", "Other"),
        })
        if cookie["category"].lower() == "functional":
            classified["Strictly Necessary"].append(cookie)
        elif cookie["category"].lower() == "analytics":
            classified["Performance"].append(cookie)
        elif cookie["category"].lower() == "marketing":
            classified["Targeting"].append(cookie)
        else:
            classified["Other"].append(cookie)
    return classified

def remove_duplicate_cookies(cookies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Entfernt doppelte Cookies basierend auf Name, Domain und Path.
    
    Args:
        cookies: Liste von Cookies, die auf Duplikate geprüft werden sollen
        
    Returns:
        Liste mit eindeutigen Cookies
    """
    unique_cookies = {}
    for cookie in cookies:
        key = (cookie["name"], cookie["domain"], cookie["path"])
        unique_cookies[key] = cookie
    return list(unique_cookies.values())
