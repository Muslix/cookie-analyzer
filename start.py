from cookie_analyzer.core import crawl_website, classify_cookies
from cookie_analyzer.database import load_cookie_database

if __name__ == "__main__":

    # Lade die Cookie-Datenbank
    cookie_database = load_cookie_database("Open-Cookie-Database.csv")

    # Scanne eine Website
    cookies, local_storage = crawl_website("https://www.example.com", max_pages=1)

    # Klassifiziere Cookies
    classified_cookies = classify_cookies(cookies, cookie_database)

    # Ausgabe der Ergebnisse
    print("\n--- Cookie-Analyse ---")
    for category, cookie_list in classified_cookies.items():
        print(f"\n{category} ({len(cookie_list)}):")
        for cookie in cookie_list:
            print(f"- {cookie['name']}:")
            print(f"  Beschreibung: {cookie.get('description', 'Keine Beschreibung')}")
            print(f"  Kategorie: {cookie.get('category', 'Unbekannt')}")
            print(f"  Ablaufzeit: {cookie.get('expiration', 'Unbekannt')}")
            print(f"  Anbieter: {cookie.get('vendor', 'Unbekannt')}")
            print(f"  Datenschutzrichtlinie: {cookie.get('privacy_policy', 'Keine Datenschutzrichtlinie')}")
            print(f"  Wildcard-Match: {'Ja' if cookie.get('wildcard') else 'Nein'}")

    print("\n--- Local Storage ---")
    for url, local_storage in local_storage.items():
        print(f"\nLocal Storage für {url}:")
        for key, value in local_storage.items():
            print(f"- {key}: {value}")

