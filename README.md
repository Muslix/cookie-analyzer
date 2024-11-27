# Cookie Analyzer

Ein Python-Tool zur Analyse von Websites auf Cookies und Local Storage, mit Integration der [Open Cookie Database](https://github.com/jkwakman/Open-Cookie-Database).

---

## **Funktionen**

- **Cookie-Erkennung**: Identifiziert Cookies auf einer Website.
- **Klassifikation**: Klassifiziert Cookies nach Kategorie und Zweck basierend auf der Open Cookie Database.
- **Local Storage Analyse**: Extrahiert gespeicherte Daten aus dem Local Storage.
- **robots.txt-Berücksichtigung**: Respektiert die Anweisungen in der `robots.txt`-Datei, um sicherzustellen, dass nur erlaubte Seiten gecrawlt werden.
- **Unterstützung für Wildcard-Cookies**: Handhabt Cookies mit dynamischen Namen (z. B. `_gac_*`).

---

## **Anforderungen**

- Python 3.8 oder höher
- Abhängigkeiten (siehe `requirements.txt`)

---

## **Installation**

### 1. **Repository klonen**

git clone https://github.com/Muslix/cookie-analyzer.git
cd cookie-analyzer

2. Abhängigkeiten installieren

pip install -r requirements.txt

3. Playwright installieren

Installiere die Playwright-Browser:

playwright install

Nutzung
1. Beispielskript ausführen

Im Repository ist ein Beispielskript start.py enthalten, das zeigt, wie das Tool genutzt werden kann. Führen Sie das Skript aus:

python start.py

2. Eigenes Projekt erstellen

Sie können die Funktionen des Tools in Ihrem eigenen Projekt nutzen. Hier ist ein Beispiel:

from cookie_analyzer.core import crawl_website, classify_cookies
from cookie_analyzer.database import load_cookie_database

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

Verzeichnisstruktur

cookie-analyzer/
├── cookie_analyzer/             # Hauptmodul
│   ├── __init__.py              # Initialisiert das Modul
│   ├── core.py                  # Enthält die Hauptfunktionen
│   ├── database.py              # Funktionen zur Datenbankverwaltung
├── tests/                       # Tests für das Modul
│   ├── __init__.py
│   └── test_core.py             # Tests für die Hauptfunktionen
├── start.py                     # Beispielskript
├── LICENSE                      # Lizenz (Apache 2.0)
├── README.md                    # Projektbeschreibung
├── requirements.txt             # Python-Abhängigkeiten
└── Open-Cookie-Database.csv     # Cookie-Datenbank

Beispielausgabe

Nach dem Ausführen von start.py könnte die Ausgabe wie folgt aussehen:

--- Cookie-Analyse ---

Strictly Necessary (1):
- pll_language:
  Beschreibung: Saves the chosen language.
  Kategorie: Functional
  Ablaufzeit: 1 year
  Anbieter: Polylang
  Datenschutzrichtlinie: https://polylang.pro/privacy-policy/
  Wildcard-Match: Nein

--- Local Storage ---

Local Storage für https://www.example.com:
- userPreference: dark_mode

Hinweise
robots.txt-Berücksichtigung

Das Tool überprüft, ob Crawling gemäß robots.txt erlaubt ist. Falls nicht erlaubt, wird nur die angegebene Startseite gescannt.
Cookie-Datenbank

Das Tool nutzt die Open Cookie Database, bereitgestellt unter der Apache License 2.0.
Quelle: https://github.com/jkwakman/Open-Cookie-Database
Datenformat der Cookie-Datenbank

Die CSV-Datei muss die folgenden Spalten enthalten:

ID, Vendor, Category, Cookie Name, Value, Description, Expiration, Vendor Website, Privacy Policy, Wildcard match

Lizenz

Dieses Projekt verwendet die Open Cookie Database und ist unter der Apache License 2.0 lizenziert.
Siehe die Datei LICENSE für weitere Informationen.