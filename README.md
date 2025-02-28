# Cookie Analyzer

Ein Python-Tool zur Analyse von Websites auf Cookies und Local Storage, mit Integration der [Open Cookie Database](https://github.com/jkwakman/Open-Cookie-Database).

---

## **Funktionen**

- **Cookie-Erkennung**: Identifiziert Cookies auf einer Website.
- **Klassifikation**: Klassifiziert Cookies nach Kategorie und Zweck basierend auf der Open Cookie Database.
- **Local Storage Analyse**: Extrahiert gespeicherte Daten aus dem Local Storage.
- **robots.txt-Berücksichtigung**: Respektiert die Anweisungen in der `robots.txt`-Datei, um sicherzustellen, dass nur erlaubte Seiten gecrawlt werden.
- **Unterstützung für Wildcard-Cookies**: Handhabt Cookies mit dynamischen Namen (z. B. `_gac_*`).
- **Konfigurierbarkeit**: Unterstützt benutzerdefinierte Konfigurationen über Kommandozeilenparameter und Konfigurationsdateien.
- **JSON-Export**: Ermöglicht das Exportieren der Ergebnisse in eine JSON-Datei für weitere Verarbeitung.
- **Logging**: Umfassendes Logging-System für bessere Fehlerbehebung und Nachvollziehbarkeit.

---

## **Anforderungen**

- Python 3.8 oder höher
- Abhängigkeiten (siehe `requirements.txt`)

---

## **Installation**

### 1. **Repository klonen**

```bash
git clone https://github.com/Muslix/cookie-analyzer.git
cd cookie-analyzer
```

### 2. **Abhängigkeiten installieren**

```bash
pip install -r requirements.txt
```

### 3. **Playwright installieren**

Installiere die Playwright-Browser:

```bash
playwright install
```

### 4. **Open Cookie Database herunterladen**

Stelle sicher, dass die Open Cookie Database als `Open-Cookie-Database.csv` im Hauptverzeichnis des Projekts verfügbar ist.
Die Datenbank kann von https://github.com/jkwakman/Open-Cookie-Database heruntergeladen werden.

---

## **Nutzung**

### 1. **Kommandozeilen-Interface**

```bash
python start.py https://www.example.com
```

#### Kommandozeilenoptionen:

```
usage: start.py [-h] [-p PAGES] [-d DATABASE] [-j] [-o OUTPUT] [-n] [url]

Cookie Analyzer - Ein Tool zur Cookie-Analyse von Websites

positional arguments:
  url                   URL der zu analysierenden Website

optional arguments:
  -h, --help            Zeigt diese Hilfenachricht an und beendet das Programm
  -p PAGES, --pages PAGES
                        Maximale Anzahl von Seiten zum Crawlen (Standard: 5)
  -d DATABASE, --database DATABASE
                        Pfad zur Cookie-Datenbank (Standard: Open-Cookie-Database.csv)
  -j, --json            Ausgabe im JSON-Format
  -o OUTPUT, --output OUTPUT
                        Speichert die Ergebnisse in einer JSON-Datei
  -n, --no-robots       Ignoriert robots.txt (nicht empfohlen)
```

### 2. **Konfigurationsdatei**

Das Tool unterstützt eine `config.ini`-Datei mit folgenden Einstellungen:

```ini
[DEFAULT]
max_pages = 5
respect_robots_txt = True
database_path = Open-Cookie-Database.csv
log_level = INFO
```

### 3. **Als Bibliothek in eigenen Projekten einbinden**

#### Installation als Paket

Um Cookie Analyzer als Paket in Ihrem Projekt zu verwenden, können Sie es direkt aus dem Repository installieren:

```bash
# Installation direkt aus GitHub
pip install git+https://github.com/Muslix/cookie-analyzer.git

# Oder lokale Installation nach dem Klonen
cd cookie-analyzer
pip install -e .
```

#### Beispiele für die Einbindung

**Beispiel 1: Einfache Website-Analyse**

```python
from cookie_analyzer import analyze_website, setup_logging

# Logging einrichten (optional)
setup_logging()

# Website analysieren und Cookies klassifizieren
classified_cookies, local_storage = analyze_website(
    "https://www.example.com", 
    max_pages=3,
    database_path="pfad/zu/Open-Cookie-Database.csv"
)

# Ergebnisse verarbeiten
print("Gefundene Cookie-Kategorien:")
for category, cookies in classified_cookies.items():
    print(f"{category}: {len(cookies)}")
```

**Beispiel 2: Spezieller Crawler mit detaillierter Konfiguration**

```python
from cookie_analyzer import CookieCrawler, classify_cookies, load_cookie_database, save_results_as_json

# Cookie-Datenbank laden
cookie_db = load_cookie_database("pfad/zu/Open-Cookie-Database.csv")

# Crawler mit speziellen Einstellungen erstellen
crawler = CookieCrawler(
    start_url="https://www.example.com",
    max_pages=10,
    respect_robots=True
)

# Crawling durchführen
cookies, local_storage = crawler.crawl()

# Cookies klassifizieren
classified_cookies = classify_cookies(cookies, cookie_db)

# Ergebnisse als JSON speichern
save_results_as_json({
    "cookies": classified_cookies,
    "local_storage": local_storage
}, "ergebnisse.json")
```

**Beispiel 3: Integration in Web-Anwendungen**

```python
from flask import Flask, request, jsonify
from cookie_analyzer import analyze_website, validate_url

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    
    # URL validieren
    valid_url = validate_url(url)
    if not valid_url:
        return jsonify({"error": "Invalid URL"}), 400
    
    # Website analysieren
    try:
        cookies, storage = analyze_website(
            valid_url, 
            max_pages=data.get('max_pages', 1),
            database_path=data.get('database_path', 'Open-Cookie-Database.csv')
        )
        
        return jsonify({
            "cookies": cookies,
            "local_storage": storage
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

**Beispiel 4: Zugriff auf alle exportierten Funktionen**

```python
# Alle wichtigen Funktionen und Klassen sind direkt aus dem Paket importierbar
from cookie_analyzer import (
    crawl_website,
    CookieCrawler,
    classify_cookies,
    analyze_website,
    load_cookie_database,
    find_cookie_info,
    remove_duplicate_cookies,
    setup_logging,
    save_results_as_json,
    load_config
)

# Alternativ können Sie auch die einzelnen Module importieren
from cookie_analyzer.core import crawl_website
from cookie_analyzer.crawler import CookieCrawler
from cookie_analyzer.cookie_handler import classify_cookies, remove_duplicate_cookies
from cookie_analyzer.database import load_cookie_database, find_cookie_info
from cookie_analyzer.utils import setup_logging, save_results_as_json, load_config
```

---

## **Beispielausgabe**

Nach dem Ausführen von `start.py` könnte die Ausgabe wie folgt aussehen:

```text
--- Cookie-Analyse ---

Strictly Necessary (1):
- pll_language:
  Beschreibung: Saves the chosen language.
  Kategorie: Functional
  Ablaufzeit: 1 year
  Domain: example.com

--- Local Storage ---

Local Storage für https://www.example.com:
- userPreference: dark_mode
```

---

## **Projektstruktur**

```text
cookie_analyzer/
├── __init__.py
├── core.py            # Kern-Funktionalität
├── crawler.py         # Website-Crawler
├── cookie_handler.py  # Cookie-Verarbeitung
├── database.py        # Datenbankintegration
├── interface.py       # API-Schnittstelle
└── utils.py           # Hilfsfunktionen
```

---

## **Hinweise**

### **robots.txt-Berücksichtigung**

Das Tool überprüft, ob Crawling gemäß robots.txt erlaubt ist. Falls nicht erlaubt, wird nur die angegebene Startseite gescannt.

### **Cookie-Datenbank**

Das Tool nutzt die Open Cookie Database, bereitgestellt unter der Apache License 2.0.
- Quelle: https://github.com/jkwakman/Open-Cookie-Database

### **Datenformat der Cookie-Datenbank**

Die CSV-Datei muss die folgenden Spalten enthalten:

```text
ID, Vendor, Category, Cookie Name, Value, Description, Expiration, Vendor Website, Privacy Policy, Wildcard match
```

---

## **Lizenz**

Dieses Projekt verwendet die Open Cookie Database und ist unter der Apache License 2.0 lizenziert.
Siehe die Datei LICENSE für weitere Informationen.
