from cookie_analyzer.interface import analyze_website
if __name__ == "__main__":

    # scanne die Website und klassifiziere Cookies
    classified_cookies, local_storage = analyze_website("https://www.planitprima.com", max_pages=1, database_path="Open-Cookie-Database.csv")

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

