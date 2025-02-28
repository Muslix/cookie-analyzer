from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
import tldextract
import logging
import asyncio
from typing import Dict, List, Tuple, Any, Optional, Set, Union, Protocol
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import re

logger = logging.getLogger(__name__)

class BrowserContextProtocol(Protocol):
    """Protocol defining the browser context interface for type checking."""
    def cookies(self) -> List[Dict[str, Any]]: ...
    def new_page(self): ...
    def close(self) -> None: ...

class PageProtocol(Protocol):
    """Protocol defining the page interface for type checking."""
    def goto(self, url: str, **kwargs) -> None: ...
    def evaluate(self, expression: str, **kwargs) -> Any: ...

# Klasse für die Cookie-Einwilligung-Erkennung
class ConsentManager:
    """Klasse zum Erkennen und Interagieren mit Cookie-Consent-Bannern."""
    
    # Bekannte Cookie-Banner-Selektoren
    CONSENT_BUTTON_SELECTORS = [
        # OneTrust
        ".onetrust-accept-btn-handler",
        "#onetrust-accept-btn-handler",
        "#accept-recommended-btn-handler",
        
        # CookieBot
        "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
        ".CybotCookiebotDialogBodyButton",
        
        # Cookie-Script
        ".cookie-accept-all-button",
        "#cookiescript_accept",
        
        # CookieYes
        ".cookie-accept-all",
        "#cookie-accept",
        
        # EU Cookie Consent
        "#eu-cookie-consent-accept",
        ".eu-cookie-consent-accept",
        
        # Übliche Button-Klassen/IDs
        ".accept-cookies",
        "#accept-cookies",
        ".accept-all-cookies",
        "#accept-all-cookies",
        ".accept",
        "#accept",
        ".agree-button",
        "#agree-button",
        ".consent-accept",
        "#consent-accept",
        
        # Text-basierte Buttons
        "button[contains(text(), 'Akzeptieren')]",
        "button[contains(text(), 'Zustimmen')]",
        "button[contains(text(), 'Annehmen')]",
        "button[contains(text(), 'Accept')]",
        "button[contains(text(), 'Agree')]",
        "button[contains(text(), 'Allow')]",
        
        # Data-Attribute
        "[data-cookieconsent='accept']",
        "[data-purpose='cookie-policy-accept']",
        "[data-testid='cookie-accept']"
    ]
    
    # Regex-Patterns für die Erkennung von Cookie-Banner-Containern
    COOKIE_BANNER_TEXT_PATTERNS = [
        r"cookie[s]?(\s+policy|\s+consent|\s+settings)?",
        r"wir verwenden cookies",
        r"diese website verwendet cookies",
        r"diese seite verwendet cookies",
        r"datenschutz",
        r"privacy",
        r"gdpr",
        r"dsgvo",
        r"zustimm[en|ung]",
        r"akzeptier[en|t]",
        r"annehm[en|e]",
        r"einwillig[en|ung]",
        r"accept(\s+all)?(\s+cookies)?",
        r"agree(\s+to)?(\s+cookies)?"
    ]
    
    @staticmethod
    def interact_with_consent(driver: webdriver.Chrome) -> bool:
        """
        Versucht, mit einem Cookie-Consent-Banner zu interagieren.
        
        Args:
            driver: Der Selenium-WebDriver
            
        Returns:
            True, wenn erfolgreich mit einem Banner interagiert wurde, sonst False
        """
        try:
            # Kurze Wartezeit für das Laden von Bannern
            time.sleep(2)
            
            # Versuche zuerst, mit bekannten Selektoren zu interagieren
            for selector in ConsentManager.CONSENT_BUTTON_SELECTORS:
                try:
                    if selector.startswith("button[contains"):
                        # XPath für Text-enthaltende Buttons
                        xpath = f"//{selector}"
                        elements = driver.find_elements(By.XPATH, xpath)
                        if elements:
                            logger.info(f"Cookie-Banner-Button gefunden mit XPath: {xpath}")
                            elements[0].click()
                            time.sleep(1)  # Kurze Wartezeit nach dem Klicken
                            return True
                    else:
                        # CSS-Selektoren
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            logger.info(f"Cookie-Banner-Button gefunden mit Selector: {selector}")
                            elements[0].click()
                            time.sleep(1)  # Kurze Wartezeit nach dem Klicken
                            return True
                except Exception as e:
                    continue  # Weiter mit dem nächsten Selector
            
            # Falls keine bekannten Selektoren funktionieren, suche nach Text-Patterns
            page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            
            for pattern in ConsentManager.COOKIE_BANNER_TEXT_PATTERNS:
                if re.search(pattern, page_text, re.IGNORECASE):
                    # Suche nach Buttons in der Nähe des gefundenen Texts
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    links = driver.find_elements(By.TAG_NAME, "a")
                    
                    for button in buttons + links:
                        button_text = button.text.lower().strip()
                        if any(kw in button_text for kw in ["accept", "akzeptieren", "zustimmen", "allow", "agree"]):
                            logger.info(f"Cookie-Banner-Button gefunden mit Text: {button_text}")
                            try:
                                button.click()
                                time.sleep(1)
                                return True
                            except:
                                continue  # Versuche den nächsten Button
            
            logger.info("Kein Cookie-Banner gefunden oder Interaktion nicht möglich")
            return False
            
        except Exception as e:
            logger.error(f"Fehler bei der Interaktion mit Cookie-Banner: {e}")
            return False

class SeleniumCookieCrawler:
    """Eine Klasse zum Crawlen von Webseiten mit Selenium und Extrahieren von Cookies und Local Storage."""
    
    def __init__(self, start_url: str, max_pages: int = 1, respect_robots: bool = True, 
                interact_with_consent: bool = True, headless: bool = True):
        """
        Initialisiert den Selenium-basierten Cookie-Crawler.
        
        Args:
            start_url (str): Die Start-URL für das Crawling.
            max_pages (int): Maximale Anzahl der zu crawlenden Seiten.
            respect_robots (bool): Ob robots.txt respektiert werden soll.
            interact_with_consent (bool): Ob mit Cookie-Consent-Bannern interagiert werden soll.
            headless (bool): Ob der Browser im Headless-Modus laufen soll.
        """
        self.start_url = start_url
        self.max_pages = max_pages
        self.respect_robots = respect_robots
        self.interact_with_consent = interact_with_consent
        self.headless = headless
        self.rp = self._load_robots_txt() if respect_robots else None
        
    def _load_robots_txt(self) -> RobotFileParser:
        """Lädt und analysiert die robots.txt-Datei der Website."""
        parsed_url = tldextract.extract(self.start_url)
        base_url = f"https://{parsed_url.registered_domain}/robots.txt"
        rp = RobotFileParser()
        try:
            rp.set_url(base_url)
            rp.read()
            logger.info(f"robots.txt erfolgreich geladen: {base_url}")
        except Exception as e:
            logger.warning(f"Fehler beim Laden der robots.txt: {e}")
        return rp
    
    def is_allowed_by_robots(self, url: str) -> bool:
        """Prüft, ob eine URL laut robots.txt gecrawlt werden darf."""
        if not self.respect_robots or self.rp is None:
            return True
        return self.rp.can_fetch("*", url)
    
    def is_internal_link(self, test_url: str) -> bool:
        """Prüft, ob ein Link intern ist."""
        base_domain = tldextract.extract(self.start_url).registered_domain
        test_domain = tldextract.extract(test_url).registered_domain
        return base_domain == test_domain
    
    def get_local_storage(self, driver: webdriver.Chrome) -> Dict[str, str]:
        """Liest den localStorage aus dem Browser aus."""
        try:
            local_storage = driver.execute_script("""
                let items = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    items[key] = localStorage.getItem(key);
                }
                return items;
            """)
            return local_storage
        except Exception as e:
            logger.error(f"Fehler beim Auslesen des localStorage: {e}")
            return {}
    
    def get_session_storage(self, driver: webdriver.Chrome) -> Dict[str, str]:
        """Liest den sessionStorage aus dem Browser aus."""
        try:
            session_storage = driver.execute_script("""
                let items = {};
                for (let i = 0; i < sessionStorage.length; i++) {
                    const key = sessionStorage.key(i);
                    items[key] = sessionStorage.getItem(key);
                }
                return items;
            """)
            return session_storage
        except Exception as e:
            logger.error(f"Fehler beim Auslesen des sessionStorage: {e}")
            return {}
    
    def get_cookies(self, driver: webdriver.Chrome) -> List[Dict[str, Any]]:
        """Konvertiert Selenium-Cookies in ein standardisiertes Format."""
        selenium_cookies = driver.get_cookies()
        
        # Konvertiere das Selenium-Cookie-Format in das Format, das wir im Rest der Anwendung verwenden
        standardized_cookies = []
        for cookie in selenium_cookies:
            standard_cookie = {
                "name": cookie.get("name", ""),
                "value": cookie.get("value", ""),
                "domain": cookie.get("domain", ""),
                "path": cookie.get("path", "/"),
                "expires": cookie.get("expiry", -1),
                "httpOnly": cookie.get("httpOnly", False),
                "secure": cookie.get("secure", False),
                "sameSite": cookie.get("sameSite", "None")
            }
            standardized_cookies.append(standard_cookie)
            
        return standardized_cookies
    
    def find_dynamic_cookies(self, driver: webdriver.Chrome) -> List[Dict[str, Any]]:
        """
        Sucht nach dynamisch gesetzten Cookies durch Benutzerinteraktionen.
        Simuliert Scrolling und Klicks auf interaktive Elemente.
        """
        initial_cookies = set([(c["name"], c["domain"]) for c in self.get_cookies(driver)])
        
        try:
            # 1. Scrolling simulieren
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # 2. Versuchen, auf ein paar interaktive Elemente zu klicken
            interactive_elements = []
            
            # Füge Tabs, Accordions und ähnliche Elemente hinzu
            for selector in [".tab", "[role='tab']", ".accordion", ".accordion-header", 
                            ".collapse-header", "[data-toggle='collapse']"]:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                interactive_elements.extend(elements[:2])  # Beschränke auf die ersten 2 pro Selektor
            
            # Klicke auf einige dieser Elemente
            for element in interactive_elements[:5]:  # Beschränke auf max. 5 Elemente
                try:
                    element.click()
                    time.sleep(0.5)
                except:
                    continue
                    
            # Überprüfe, ob neue Cookies hinzugefügt wurden
            current_cookies = self.get_cookies(driver)
            current_cookie_keys = set([(c["name"], c["domain"]) for c in current_cookies])
            
            new_cookie_keys = current_cookie_keys - initial_cookies
            dynamic_cookies = [c for c in current_cookies 
                              if (c["name"], c["domain"]) in new_cookie_keys]
            
            if dynamic_cookies:
                logger.info(f"Gefunden {len(dynamic_cookies)} dynamisch gesetzte Cookies nach Benutzerinteraktion")
                
            return dynamic_cookies
            
        except Exception as e:
            logger.error(f"Fehler beim Suchen nach dynamischen Cookies: {e}")
            return []
    
    def crawl(self) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Union[Dict[str, str], str]]]]:
        """
        Crawlt eine Website mit Selenium und extrahiert Cookies und Web Storage Daten.
        
        Returns:
            Tuple mit Liste von Cookies und Dictionary mit Local/Session Storage und dynamischen Cookies
        """
        if self.respect_robots and not self.is_allowed_by_robots(self.start_url):
            logger.warning("Crawling ist laut robots.txt verboten. Es wird nur die eingegebene Seite gescannt.")
            return self.scan_single_page()
        
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        visited = set()
        to_visit = [self.start_url]
        all_cookies = []
        all_storage = {}
        
        try:
            driver = webdriver.Chrome(options=options)
            
            while to_visit and len(visited) < self.max_pages:
                url = to_visit.pop(0)
                if url in visited:
                    continue
                
                if self.respect_robots and not self.is_allowed_by_robots(url):
                    logger.warning(f"robots.txt verbietet das Crawlen von: {url}")
                    continue
                
                logger.info(f"Scanne mit Selenium: {url}")
                visited.add(url)
                
                try:
                    driver.get(url)
                    
                    # Warte, bis die Seite geladen ist
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Interagiere mit Cookie-Consent-Banner, falls aktiviert
                    if self.interact_with_consent:
                        consent_handled = ConsentManager.interact_with_consent(driver)
                        if consent_handled:
                            logger.info(f"Cookie-Consent-Banner auf {url} wurde behandelt")
                            # Kurze Wartezeit nach Consent-Interaktion
                            time.sleep(2)
                    
                    # Sammle normale Cookies
                    cookies = self.get_cookies(driver)
                    all_cookies.extend(cookies)
                    
                    # Sammle Web Storage und dynamische Cookies für diese URL
                    local_storage = self.get_local_storage(driver)
                    session_storage = self.get_session_storage(driver)
                    
                    # Suche nach dynamisch gesetzten Cookies
                    dynamic_cookies = self.find_dynamic_cookies(driver)
                    
                    # Speichere alle gesammelten Daten für diese URL
                    all_storage[url] = {
                        "localStorage": local_storage,
                        "sessionStorage": session_storage,
                        "dynamicCookies": dynamic_cookies
                    }
                    
                    # Links für weiteres Crawling finden
                    if len(visited) < self.max_pages:
                        elements = driver.find_elements(By.TAG_NAME, "a")
                        for element in elements:
                            try:
                                href = element.get_attribute("href")
                                if href and self.is_internal_link(href) and href not in visited:
                                    to_visit.append(href)
                            except:
                                continue
                    
                except Exception as e:
                    logger.error(f"Fehler beim Scannen von {url} mit Selenium: {e}")
                
            # Einige Cookies könnten doppelt erfasst worden sein, füge sie zum Gesamtergebnis hinzu
            all_cookies.extend([cookie for storage in all_storage.values() 
                              for cookie in storage.get("dynamicCookies", [])])
                
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren von Selenium: {e}")
        finally:
            try:
                driver.quit()
            except:
                pass
            
        return all_cookies, all_storage
    
    def scan_single_page(self) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Union[Dict[str, str], str]]]]:
        """Scannt nur die eingegebene Seite mit Selenium."""
        logger.info(f"Scanne nur die eingegebene Seite mit Selenium: {self.start_url}")
        
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        cookies = []
        storage_data = {}
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(self.start_url)
            
            # Warte, bis die Seite geladen ist
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Interagiere mit Cookie-Consent-Banner, falls aktiviert
            if self.interact_with_consent:
                consent_handled = ConsentManager.interact_with_consent(driver)
                if consent_handled:
                    logger.info(f"Cookie-Consent-Banner auf {self.start_url} wurde behandelt")
                    # Kurze Wartezeit nach Consent-Interaktion
                    time.sleep(2)
            
            # Sammle normale Cookies
            cookies = self.get_cookies(driver)
            
            # Sammle Web Storage und dynamische Cookies
            local_storage = self.get_local_storage(driver)
            session_storage = self.get_session_storage(driver)
            dynamic_cookies = self.find_dynamic_cookies(driver)
            
            storage_data = {
                self.start_url: {
                    "localStorage": local_storage,
                    "sessionStorage": session_storage,
                    "dynamicCookies": dynamic_cookies
                }
            }
            
            # Füge dynamische Cookies zum Gesamtergebnis hinzu
            cookies.extend(dynamic_cookies)
            
        except Exception as e:
            logger.error(f"Fehler beim Scannen der Seite {self.start_url} mit Selenium: {e}")
        finally:
            try:
                driver.quit()
            except:
                pass
                
        return cookies, storage_data

class CookieCrawler:
    """Eine Klasse zum Crawlen von Webseiten und Extrahieren von Cookies und Local Storage."""
    
    def __init__(self, start_url: str, max_pages: int = 1, respect_robots: bool = True):
        """
        Initialisiert den Cookie-Crawler.
        
        Args:
            start_url (str): Die Start-URL für das Crawling.
            max_pages (int): Maximale Anzahl der zu crawlenden Seiten.
            respect_robots (bool): Ob robots.txt respektiert werden soll.
        """
        self.start_url = start_url
        self.max_pages = max_pages
        self.respect_robots = respect_robots
        self.rp = self._load_robots_txt() if respect_robots else None
        
    def _load_robots_txt(self) -> RobotFileParser:
        """Lädt und analysiert die robots.txt-Datei der Website."""
        parsed_url = tldextract.extract(self.start_url)
        base_url = f"https://{parsed_url.registered_domain}/robots.txt"
        rp = RobotFileParser()
        try:
            rp.set_url(base_url)
            rp.read()
            logger.info(f"robots.txt erfolgreich geladen: {base_url}")
        except Exception as e:
            logger.warning(f"Fehler beim Laden der robots.txt: {e}")
        return rp
    
    def is_allowed_by_robots(self, url: str) -> bool:
        """Prüft, ob eine URL laut robots.txt gecrawlt werden darf."""
        if not self.respect_robots or self.rp is None:
            return True
        return self.rp.can_fetch("*", url)
    
    def is_internal_link(self, test_url: str) -> bool:
        """Prüft, ob ein Link intern ist."""
        base_domain = tldextract.extract(self.start_url).registered_domain
        test_domain = tldextract.extract(test_url).registered_domain
        return base_domain == test_domain
    
    @staticmethod
    def get_local_storage(page: PageProtocol) -> Dict[str, str]:
        """Liest den localStorage einer Seite aus."""
        try:
            local_storage = page.evaluate("() => { return window.localStorage; }")
            return local_storage
        except Exception as e:
            logger.error(f"Fehler beim Auslesen des localStorage: {e}")
            return {}
    
    def scan_single_page(self) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Scannt nur die eingegebene Seite auf Cookies und Local Storage."""
        logger.info(f"Scanne nur die eingegebene Seite: {self.start_url}")
        cookies = []
        local_storage = {}
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            try:
                with context.new_page() as page:
                    page.goto(self.start_url)
                    cookies = context.cookies()
                    local_storage = self.get_local_storage(page)
            except Exception as e:
                logger.error(f"Fehler beim Scannen der Seite {self.start_url}: {e}")
            finally:
                browser.close()
                
        return cookies, local_storage
    
    def crawl(self) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, str]]]:
        """Crawlt eine Website und sammelt Cookies."""
        if self.respect_robots and not self.is_allowed_by_robots(self.start_url):
            logger.warning("Crawling ist laut robots.txt verboten. Es wird nur die eingegebene Seite gescannt.")
            cookies, local_storage = self.scan_single_page()
            return cookies, {self.start_url: local_storage}
        
        visited = set()
        to_visit = [self.start_url]
        all_cookies = []
        all_local_storage = {}
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            
            while to_visit and len(visited) < self.max_pages:
                url = to_visit.pop(0)
                if url in visited:
                    continue
                    
                if self.respect_robots and not self.is_allowed_by_robots(url):
                    logger.warning(f"robots.txt verbietet das Crawlen von: {url}")
                    continue
                    
                logger.info(f"Scanne: {url}")
                visited.add(url)
                
                try:
                    with context.new_page() as page:
                        page.goto(url)
                        
                        cookies = context.cookies()
                        all_cookies.extend(cookies)
                        
                        local_storage = self.get_local_storage(page)
                        all_local_storage[url] = local_storage
                        
                        html = page.evaluate("() => document.documentElement.outerHTML")
                        soup = BeautifulSoup(html, "html.parser")
                        for link in soup.find_all("a", href=True):
                            full_url = urljoin(url, link["href"])
                            if self.is_internal_link(full_url):
                                to_visit.append(full_url)
                except Exception as e:
                    logger.error(f"Fehler beim Scannen von {url}: {e}")
            
            browser.close()
        
        return all_cookies, all_local_storage


class AsyncCookieCrawler:
    """Eine asynchrone Klasse zum Crawlen von Webseiten und Extrahieren von Cookies und Local Storage."""
    
    def __init__(self, start_url: str, max_pages: int = 1, respect_robots: bool = True, max_concurrent: int = 3):
        """
        Initialisiert den asynchronen Cookie-Crawler.
        
        Args:
            start_url (str): Die Start-URL für das Crawling.
            max_pages (int): Maximale Anzahl der zu crawlenden Seiten.
            respect_robots (bool): Ob robots.txt respektiert werden soll.
            max_concurrent (int): Maximale Anzahl gleichzeitiger Crawling-Operationen.
        """
        self.start_url = start_url
        self.max_pages = max_pages
        self.respect_robots = respect_robots
        self.max_concurrent = max_concurrent
        self.rp = self._load_robots_txt() if respect_robots else None
        self.semaphore: Optional[asyncio.Semaphore] = None
        
    def _load_robots_txt(self) -> RobotFileParser:
        """Lädt und analysiert die robots.txt-Datei der Website."""
        parsed_url = tldextract.extract(self.start_url)
        base_url = f"https://{parsed_url.registered_domain}/robots.txt"
        rp = RobotFileParser()
        try:
            rp.set_url(base_url)
            rp.read()
            logger.info(f"robots.txt erfolgreich geladen: {base_url}")
        except Exception as e:
            logger.warning(f"Fehler beim Laden der robots.txt: {e}")
        return rp
    
    def is_allowed_by_robots(self, url: str) -> bool:
        """Prüft, ob eine URL laut robots.txt gecrawlt werden darf."""
        if not self.respect_robots or self.rp is None:
            return True
        return self.rp.can_fetch("*", url)
    
    def is_internal_link(self, test_url: str) -> bool:
        """Prüft, ob ein Link intern ist."""
        base_domain = tldextract.extract(self.start_url).registered_domain
        test_domain = tldextract.extract(test_url).registered_domain
        return base_domain == test_domain
    
    @staticmethod
    async def get_local_storage(page) -> Dict[str, str]:
        """Liest den localStorage einer Seite aus."""
        try:
            local_storage = await page.evaluate("() => { return window.localStorage; }")
            return local_storage
        except Exception as e:
            logger.error(f"Fehler beim Auslesen des localStorage: {e}")
            return {}
    
    async def scan_single_page(self) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Scannt nur die eingegebene Seite auf Cookies und Local Storage."""
        logger.info(f"Scanne nur die eingegebene Seite: {self.start_url}")
        cookies = []
        local_storage = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            try:
                page = await context.new_page()
                await page.goto(self.start_url)
                cookies = await context.cookies()
                local_storage = await self.get_local_storage(page)
                await page.close()
            except Exception as e:
                logger.error(f"Fehler beim Scannen der Seite {self.start_url}: {e}")
            finally:
                await browser.close()
                
        return cookies, local_storage
    
    async def process_page(self, url: str, context, visited: Set[str], 
                          to_visit: List[str], all_cookies: List[Dict[str, Any]], 
                          all_local_storage: Dict[str, Dict[str, str]]) -> None:
        """Verarbeitet eine einzelne Seite asynchron."""
        async with self.semaphore:  # Begrenzt die Anzahl gleichzeitiger Anfragen
            if url in visited:
                return
                
            if self.respect_robots and not self.is_allowed_by_robots(url):
                logger.warning(f"robots.txt verbietet das Crawlen von: {url}")
                return
                
            logger.info(f"Scanne asynchron: {url}")
            visited.add(url)
            
            try:
                page = await context.new_page()
                await page.goto(url)
                
                cookies = await context.cookies()
                all_cookies.extend(cookies)
                
                local_storage = await self.get_local_storage(page)
                all_local_storage[url] = local_storage
                
                html = await page.evaluate("() => document.documentElement.outerHTML")
                soup = BeautifulSoup(html, "html.parser")
                
                for link in soup.find_all("a", href=True):
                    full_url = urljoin(url, link["href"])
                    if self.is_internal_link(full_url) and full_url not in visited and len(visited) < self.max_pages:
                        to_visit.append(full_url)
                
                await page.close()
            except Exception as e:
                logger.error(f"Fehler beim Scannen von {url}: {e}")
    
    async def crawl_async(self) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, str]]]:
        """Crawlt eine Website asynchron und sammelt Cookies."""
        if self.respect_robots and not self.is_allowed_by_robots(self.start_url):
            logger.warning("Crawling ist laut robots.txt verboten. Es wird nur die eingegebene Seite gescannt.")
            return await self.scan_single_page()
        
        visited: Set[str] = set()
        to_visit: List[str] = [self.start_url]
        all_cookies: List[Dict[str, Any]] = []
        all_local_storage: Dict[str, Dict[str, str]] = {}
        
        # Semaphore zur Begrenzung gleichzeitiger Anfragen
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            try:
                while to_visit and len(visited) < self.max_pages:
                    # Sammle bis zu max_concurrent URLs zum gleichzeitigen Verarbeiten
                    batch = []
                    while to_visit and len(batch) < self.max_concurrent and len(visited) + len(batch) < self.max_pages:
                        url = to_visit.pop(0)
                        if url not in visited:
                            batch.append(url)
                    
                    if not batch:
                        break
                    
                    # Verarbeite den Batch parallel
                    tasks = [
                        self.process_page(url, context, visited, to_visit, all_cookies, all_local_storage)
                        for url in batch
                    ]
                    await asyncio.gather(*tasks)
                    
            finally:
                await browser.close()
        
        return all_cookies, all_local_storage