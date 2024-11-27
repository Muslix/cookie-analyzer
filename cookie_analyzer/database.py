import csv

def load_cookie_database(file_path="Open-Cookie-Database.csv"):
    """Lädt die Open Cookie Database aus einer CSV-Datei und extrahiert alle relevanten Informationen."""
    cookie_database = []
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(",")  # Zerlege die Zeile anhand von Kommas
                if len(parts) >= 10:  # Stelle sicher, dass mindestens 10 Spalten vorhanden sind
                    cookie_database.append({
                        "ID": parts[0],                        # 1. Spalte: ID
                        "Vendor": parts[1],                    # 2. Spalte: Anbieter
                        "Category": parts[2],                  # 3. Spalte: Kategorie
                        "Cookie Name": parts[3],               # 4. Spalte: Cookie-Name
                        "Value": parts[4],                     # 5. Spalte: Wert (falls vorhanden)
                        "Description": parts[5],               # 6. Spalte: Beschreibung
                        "Expiration": parts[6],                # 7. Spalte: Ablaufzeit
                        "Vendor Website": parts[7],            # 8. Spalte: Anbieter-Name
                        "Privacy Policy": parts[8],            # 9. Spalte: Datenschutzrichtlinie
                        "Wildcard match": parts[9] == "1"      # 10. Spalte: Wildcard-Matching
                    })
    except Exception as e:
        print(f"Fehler beim Laden der Cookie-Datenbank: {e}")
    return cookie_database

def find_cookie_info(cookie_name, cookie_database):
    """Sucht nach Informationen zu einem Cookie in der Open Cookie Database."""
    for cookie in cookie_database:
        if cookie["Wildcard match"]:
            # Prüfe Wildcard-Muster
            if cookie_name.startswith(cookie["Cookie Name"]):
                return cookie
        elif cookie["Cookie Name"].lower() == cookie_name.lower():
            return cookie
    return {"Description": "Keine Beschreibung verfügbar.", "Category": "Unknown"}
