# Cookie Analyzer
Ein Python-Tool zur Analyse von Websites auf Cookies und Local Storage, mit Integration der [Open Cookie Database](https://github.com/jkwakman/Open-Cookie-Database).

![CI Status](https://github.com/Muslix/cookie-analyzer/actions/workflows/ci.yml/badge.svg)
![Docker Status](https://github.com/Muslix/cookie-analyzer/actions/workflows/docker.yml/badge.svg)
![Code Quality](https://github.com/Muslix/cookie-analyzer/actions/workflows/lint.yml/badge.svg)

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
- **Erweiterte Cookie-Erkennung**: Verwendet Selenium für die Erkennung dynamisch gesetzter Cookies.
- **Cookie-Consent-Simulation**: Automatische Interaktion mit gängigen Cookie-Consent-Bannern.
- **Regelbasierte Klassifizierung**: Verwendet Heuristiken zur Klassifizierung unbekannter Cookies.
- **Fingerprinting-Erkennung**: Identifiziert potenzielle Fingerprinting-Techniken auf Websites.
- **Asynchrones Crawling**: Unterstützt asynchrone Verarbeitung für bessere Performance.
- **Dependency Injection**: Modulare Architektur für bessere Testbarkeit und Flexibilität.
---
## **Anforderungen**
- Python 3.8 oder höher
- Playwright (für Standard-Crawling)
- Selenium (für erweiterte Cookie-Erfassung)
- Weitere Abhängigkeiten (siehe `requirements.txt`)
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

Ohne weitere Parameter verwendet der Cookie Analyzer standardmäßig alle verfügbaren Funktionen (Selenium für erweiterte Cookie-Erkennung, Consent-Banner-Interaktion, und Fingerprinting-Analyse).

#### Kommandozeilenoptionen:
```
usage: start.py [-h] [-p PAGES] [-d DATABASE] [-j] [-o OUTPUT] [-n] [-u] [--list-alternatives] [-a] [-s] [--async] [--no-consent] [--show-browser] [--fingerprinting] [--dynamic] [--full] [url]

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
  -u, --update-db       Aktualisiert die Cookie-Datenbank vor der Analyse
  --list-alternatives   Zeigt alternative Cookie-Datenbanken an und beendet das Programm
  -a, --all-available   Zeigt auch potenziell verfügbare Cookies an
  -s, --selenium        Verwendet Selenium für erweiterte Cookie-Erfassung und Consent-Interaktion
  --async               Verwendet asynchrone Verarbeitung für bessere Performance bei mehreren Seiten
  --no-consent          Deaktiviert die automatische Interaktion mit Cookie-Consent-Bannern
  --show-browser        Zeigt den Browser während der Analyse (kein Headless-Modus)
  --fingerprinting      Analysiert und zeigt potenzielle Fingerprinting-Techniken
  --dynamic             Zeigt dynamisch gesetzte Cookies getrennt an
  --full                Aktiviert alle Analyse-Features (Selenium, Fingerprinting, dynamische Cookies)
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

#### Grundlegende Verwendung
Die einfachste Methode zur Verwendung des Cookie Analyzers in einem eigenen Projekt:

```python
from cookie_analyzer import analyze_website

# Website analysieren mit Standardeinstellungen
classified_cookies, storage_data = analyze_website("https://www.example.com")

# Ergebnisse verarbeiten
print("\nCookie-Kategorien:")
for category, cookies in classified_cookies.items():
    print(f"{category}: {len(cookies)}")
```

#### Verwendung mit erweiterten Funktionen
Um die erweiterten Funktionen wie Selenium und Fingerprinting-Erkennung zu nutzen:

```python
from cookie_analyzer import analyze_website
from cookie_analyzer.services import get_cookie_classifier_service

# Website mit Selenium analysieren und Consent-Banner automatisch akzeptieren
classified_cookies, storage_data = analyze_website(
    "https://www.example.com",
    use_selenium=True,
    interact_with_consent=True,
    headless=True  # True für unsichtbaren Browser, False zum Anzeigen
)

# Fingerprinting-Erkennung
cookie_classifier = get_cookie_classifier_service()
all_cookies = []
for category, cookies in classified_cookies.items():
    all_cookies.extend(cookies)
    
fingerprinting_data = cookie_classifier.identify_fingerprinting(all_cookies, storage_data)

# Überprüfen, ob Fingerprinting-Techniken erkannt wurden
if any(fingerprinting_data.values()):
    print("Fingerprinting-Techniken erkannt:")
    for tech, detected in fingerprinting_data.items():
        if detected:
            print(f"- {tech}")
```

#### Zugriff auf alle verfügbaren Klassen und Funktionen
Das Paket bietet direkten Zugriff auf alle wichtigen Komponenten:

```python
# Neue Klassen und Funktionen
from cookie_analyzer import (
    # Core-Funktionalitäten
    analyze_website, 
    analyze_website_async,
    CookieAnalyzer,
    
    # Crawler-Komponenten
    CookieCrawler,
    AsyncCookieCrawler,
    SeleniumCookieCrawler,
    
    # Dependency Injection
    initialize_services,
    ServiceProvider,
    get_database_service,
    get_cookie_classifier_service,
    get_crawler_service,
    
    # Cookie-Verarbeitung
    CookieHandler,
    CookieClassifier,
    
    # Datenbank-Funktionen
    DatabaseHandler,
    
    # Hilfsfunktionen
    setup_logging,
    save_results_as_json,
    load_config,
    validate_url,
    Config
)
```

#### Implementierungen des Dependency Injection Patterns
Für fortgeschrittene Anwendungen können Sie eigene Implementierungen der Service-Schnittstellen erstellen:

```python
from cookie_analyzer.services import ServiceProvider, CookieDatabaseService

# Beispiel: Eigene Implementierung des Datenbank-Services
class CustomDatabaseService:
    """Eigene Implementierung des Datenbank-Services"""
    
    def load_database(self, file_path=None):
        # Eigene Logik zum Laden der Datenbank
        return []
    
    def find_cookie_info(self, cookie_name, cookie_database):
        # Eigene Logik zum Finden von Cookie-Informationen
        return {"Description": "Custom description", "Category": "Performance"}
    
    def update_database(self, output_path=None, url=None):
        # Eigene Logik zum Aktualisieren der Datenbank
        return True

# Registrieren der eigenen Implementierung
ServiceProvider.register("database", CustomDatabaseService())
```

#### Beispiel für asynchrone Verarbeitung
Für Anwendungen, die asynchrones Verhalten benötigen:

```python
import asyncio
from cookie_analyzer import analyze_website_async

async def main():
    # Website asynchron analysieren
    classified_cookies, storage_data = await analyze_website_async(
        "https://www.example.com",
        max_pages=3
    )
    
    # Ergebnisse verarbeiten
    print("Analyseergebnisse:", len(classified_cookies))

# Ausführen der asynchronen Funktion
asyncio.run(main())
```

Hinweis: Wenn Sie die asynchrone Verarbeitung nutzen möchten, stellen Sie sicher, dass Sie in einer asynchronen Umgebung arbeiten.

#### Beispiel für die Integration in Web-Frameworks
Beispiel für die Integration in Flask:

```python
from flask import Flask, request, jsonify
from cookie_analyzer import analyze_website

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    
    try:
        cookies, storage = analyze_website(
            url,
            max_pages=data.get('max_pages', 1),
            use_selenium=data.get('use_selenium', True)
        )
        
        return jsonify({
            "cookies": cookies,
            "storage": storage
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Beispiel für die Integration in Django:

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from cookie_analyzer import analyze_website

@csrf_exempt
def analyze_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        url = data.get('url')
        
        try:
            cookies, storage = analyze_website(
                url,
                max_pages=data.get('max_pages', 1),
                use_selenium=data.get('use_selenium', True)
            )
            
            return JsonResponse({
                "cookies": cookies,
                "storage": storage
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)
```

---
## **Beispielausgabe**
Nach dem Ausführen von `start.py` könnte die Ausgabe wie folgt aussehen:
```text
=== Aktuelle Cookie-Analyse ===

Strictly Necessary (2):
- pll_language:
  Beschreibung: Saves the chosen language.
  Kategorie: Functional
  Klassifizierungsmethode: database
  Ablaufzeit: 1 year
  Domain: example.com
- session:
  Beschreibung: Technisch notwendiger Session-Cookie
  Kategorie: Strictly Necessary
  Klassifizierungsmethode: rule-based
  Ablaufzeit: Session
  Domain: example.com

Performance (1):
- _ga:
  Beschreibung: Google Analytics tracking cookie
  Kategorie: Performance
  Klassifizierungsmethode: database
  Ablaufzeit: 2 years
  Domain: example.com

Targeting (1):
- _fbp:
  Beschreibung: Facebook Pixel tracking cookie
  Kategorie: Targeting
  Klassifizierungsmethode: rule-based
  Ablaufzeit: 90 days
  Domain: example.com

=== Web Storage ===

Storage für https://www.example.com:

Local Storage:
- userPreference: dark_mode
- lastVisit: 2023-05-22

Session Storage:
- temporaryData: {"lastView":"homepage"}

Dynamisch gesetzte Cookies:
- _gat: 1
- _dc_gtm_UA-12345: 1

=== Fingerprinting-Analyse ===
Potenzielle Fingerprinting-Techniken erkannt:
- Canvas Fingerprinting
- Persistent Identifiers
```
---
## **Projektstruktur**
```text
cookie_analyzer/
├── __init__.py         # Package-Initialisierung und API-Exporte
├── core.py             # Kern-Funktionalität der Analyse
├── crawler.py          # Website-Crawler (Playwright, Async, Selenium)
├── cookie_handler.py   # Cookie-Verarbeitung und Klassifizierung
├── database.py         # Datenbankintegration und -operationen
├── interface.py        # CLI-Schnittstelle und API-Funktionen
├── services.py         # Dependency Injection Services
└── utils.py            # Hilfsfunktionen und Konfiguration
```
---
## **CI/CD Pipeline**

Das Projekt ist mit einer umfassenden CI/CD-Pipeline eingerichtet, die automatische Tests, Codequalitätsprüfung, Docker-Image-Erstellung und Veröffentlichung umfasst.

### **GitHub Actions Workflows**

1. **CI (Continuous Integration)**
   - Automatische Tests auf mehreren Python-Versionen (3.9, 3.10, 3.11)
   - Installiert Chrome und ChromeDriver für Selenium-Tests
   - Führt Tests mit Berichterstattung zur Codeabdeckung aus
   - Lädt Codeabdeckungsberichte zu Codecov hoch

2. **Code Quality**
   - Prüft die Codeformatierung mit Black
   - Sortierung der Importe mit isort
   - Lint-Prüfung mit flake8
   - Statische Code-Analyse mit pylint

3. **Docker Build und Test**
   - Erstellt ein Docker-Image für die Anwendung
   - Testet das erstellte Image
   - Veröffentlicht das Image in der GitHub Container Registry (bei Pushes zu main/master oder Tags)

4. **CD (Continuous Deployment)**
   - Automatische Veröffentlichung des Pakets auf PyPI bei Erstellung eines neuen Tags
   - Erstellt GitHub Releases mit den Distributionspaketen

### **Lokale Entwicklung mit Make-Befehlen**

Das Projekt enthält eine `Makefile` mit nützlichen Befehlen zur Entwicklung:

```bash
# Installation der Abhängigkeiten
make install

# Ausführen der Tests
make test

# Code-Coverage prüfen
make coverage

# Lint-Prüfung durchführen
make lint

# Code formatieren
make format

# Release erstellen und auf PyPI hochladen
make release

# Bereinigen von temporären Dateien
make clean
```

### **Docker-Unterstützung**

Sie können die Anwendung mit Docker ausführen:

```bash
# Docker-Image bauen
docker build -t cookie-analyzer .

# Anwendung ausführen
docker run cookie-analyzer https://www.example.com

# Mit Docker Compose ausführen
docker-compose up cookie-analyzer

# Tests in Docker ausführen
docker-compose up test
```

---
## **Hinweise**

### **Selenium vs. Playwright**
- **Playwright**: Standardmäßiger Crawler, schneller für einfache Analysen
- **Selenium**: Erweiterter Crawler mit Unterstützung für dynamische Cookies und Consent-Banner-Interaktion
- **Async Playwright**: Für performantes Crawling mehrerer Seiten gleichzeitig

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

### **Regelbasierte Klassifizierung**
Wenn ein Cookie nicht in der Datenbank gefunden wird, verwendet der Cookie Analyzer Heuristiken zur Bestimmung der wahrscheinlichen Kategorie:
- **Pattern-basiert**: Matching auf bekannte Cookie-Namensmuster
- **Domain-basiert**: Klassifizierung anhand der Cookie-Domain
- **Keyword-basiert**: Analyse von Namen und Werten auf typische Schlüsselwörter
- **Lebensdauer-basiert**: Langlebige Cookies werden oft für Targeting verwendet

---
## **Lizenz**
Dieses Projekt verwendet die Open Cookie Database und ist unter der Apache License 2.0 lizenziert.
Siehe die Datei LICENSE für weitere Informationen.
