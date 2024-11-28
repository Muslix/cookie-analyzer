from .core import crawl_website, classify_cookies
from .database import load_cookie_database

def analyze_website(url, max_pages=1, database_path="Open-Cookie-Database.csv"):
    """
    Analysiert eine Website und liefert klassifizierte Cookies zurück.
    
    Args:
        url (str): Die URL der Website, die analysiert werden soll.
        max_pages (int): Maximale Anzahl von Seiten, die gecrawlt werden sollen.
        database_path (str): Pfad zur Cookie-Datenbank (CSV-Datei).
    
    Returns:
        dict: Klassifizierte Cookies nach Kategorien.
    """
    # Lade die Cookie-Datenbank
    cookie_database = load_cookie_database(database_path)

    # Scanne die Website
    cookies, local_storage = crawl_website(url, max_pages=max_pages)

    # Klassifiziere Cookies
    return classify_cookies(cookies, cookie_database), local_storage
