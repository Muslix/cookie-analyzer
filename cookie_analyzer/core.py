from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from .database import find_cookie_info
import tldextract

def load_robots_txt(start_url):
    """Lädt und analysiert die robots.txt-Datei der Website."""
    parsed_url = tldextract.extract(start_url)
    base_url = f"https://{parsed_url.registered_domain}/robots.txt"
    rp = RobotFileParser()
    try:
        rp.set_url(base_url)
        rp.read()
        print(f"robots.txt erfolgreich geladen: {base_url}")
    except Exception as e:
        print(f"Fehler beim Laden der robots.txt: {e}")
    return rp

def is_allowed_by_robots(rp, url):
    """Prüft, ob eine URL laut robots.txt gecrawlt werden darf."""
    return rp.can_fetch("*", url)

def get_local_storage(page):
    """Liest den localStorage einer Seite aus."""
    try:
        local_storage = page.evaluate("() => { return window.localStorage; }")
        return local_storage
    except Exception as e:
        print(f"Fehler beim Auslesen des localStorage: {e}")
        return {}

def scan_single_page(url):
    """Scannt nur die eingegebene Seite auf Cookies und Local Storage."""
    print(f"Scanne nur die eingegebene Seite: {url}")
    cookies = []
    local_storage = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        try:
            with context.new_page() as page:
                page.goto(url)
                cookies = context.cookies()
                local_storage = get_local_storage(page)
        except Exception as e:
            print(f"Fehler beim Scannen der Seite {url}: {e}")
        finally:
            browser.close()

    return cookies, local_storage

def crawl_website(start_url, max_pages=1):
    """Crawlt eine Website und sammelt Cookies."""
    rp = load_robots_txt(start_url)

    if not is_allowed_by_robots(rp, start_url):
        print("Crawling ist laut robots.txt verboten. Es wird nur die eingegebene Seite gescannt.")
        return scan_single_page(start_url)

    visited = set()
    to_visit = [start_url]
    all_cookies = []
    all_local_storage = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue

            if not is_allowed_by_robots(rp, url):
                print(f"robots.txt verbietet das Crawlen von: {url}")
                continue

            print(f"Scanne: {url}")
            visited.add(url)

            try:
                with context.new_page() as page:
                    page.goto(url)

                    cookies = context.cookies()
                    all_cookies.extend(cookies)

                    local_storage = get_local_storage(page)
                    all_local_storage[url] = local_storage

                    html = page.evaluate("() => document.documentElement.outerHTML")
                    soup = BeautifulSoup(html, "html.parser")
                    for link in soup.find_all("a", href=True):
                        full_url = urljoin(url, link["href"])
                        if is_internal_link(start_url, full_url):
                            to_visit.append(full_url)
            except Exception as e:
                print(f"Fehler beim Scannen von {url}: {e}")

        browser.close()

    all_cookies = remove_duplicate_cookies(all_cookies)
    return all_cookies, all_local_storage

def is_internal_link(base_url, test_url):
    """Prüft, ob ein Link intern ist."""
    base_domain = tldextract.extract(base_url).registered_domain
    test_domain = tldextract.extract(test_url).registered_domain
    return base_domain == test_domain

def remove_duplicate_cookies(cookies):
    """Entfernt doppelte Cookies basierend auf Name, Domain und Path."""
    unique_cookies = {}
    for cookie in cookies:
        key = (cookie["name"], cookie["domain"], cookie["path"])
        unique_cookies[key] = cookie
    return list(unique_cookies.values())

def classify_cookies(cookies, cookie_database):
    """Klassifiziert Cookies und ergänzt Informationen aus der Cookie-Datenbank."""
    classified = {"Strictly Necessary": [], "Performance": [], "Targeting": [], "Other": []}
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
