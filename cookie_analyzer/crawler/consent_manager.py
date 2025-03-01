"""
Consent-Manager zur Interaktion mit Cookie-Banner.
"""

import logging
import time
from typing import Union, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

logger = logging.getLogger(__name__)

class ConsentManager:
    """Klasse zur Interaktion mit verschiedenen Cookie-Consent-Bannern."""
    
    # Liste von bekannten Selektoren für "Alle ablehnen"-Buttons
    REJECT_BUTTON_SELECTORS = [
        # OneTrust
        "#onetrust-reject-all-handler",
        ".onetrust-close-btn-handler",
        
        # Cookiebot
        "button[data-cui-consent-action='decline']",
        "#CybotCookiebotDialogBodyButtonDecline",
        
        # Cookie-Script
        ".cookie-script-decline-button",
        
        # Generic
        "[aria-label='Ablehnen']",
        "[aria-label='Deny']",
        "[aria-label='Reject']",
        "[title='Ablehnen']",
        "[title='Deny']",
        "[title='Reject']",
        "button:contains('Ablehnen')",
        "button:contains('nur notwendige')",
        "button:contains('Deny')",
        "button:contains('Decline')",
        "button:contains('Reject')",
        "button:contains('Refuse')",
        "[data-testid='uc-deny-all-button']"
    ]
    
    # Liste von bekannten Selektoren für "Einstellungen"-Buttons
    SETTINGS_BUTTON_SELECTORS = [
        # OneTrust
        "#onetrust-pc-btn-handler",
        
        # Cookiebot
        "button.CybotCookiebotDialogBodyButton[data-cui-denial-action='settings']",
        "#CybotCookiebotDialogBodyButtonDetails",
        
        # Generic
        "[aria-label='Cookie-Einstellungen']",
        "[aria-label='Cookie settings']",
        "[title='Einstellungen']",
        "[title='Settings']",
        "button:contains('Einstellungen')",
        "button:contains('Cookie-Einstellungen')",
        "button:contains('Settings')",
        "button:contains('Cookie settings')",
        "[data-testid='uc-settings-button']"
    ]
    
    # Liste von bekannten Selektoren für Banner-Erkennungs-Elemente
    BANNER_DETECTION_SELECTORS = [
        # OneTrust
        "#onetrust-banner-sdk",
        "#onetrust-consent-sdk",
        
        # Cookiebot
        "#CybotCookiebotDialog",
        "[data-cookieconsent='dialog']",
        
        # Cookie-Script
        "#cookiescript_injected",
        
        # Generic
        "[aria-label='Cookie Consent']",
        "[aria-label='Cookie-Banner']",
        "[class*='cookie-banner']",
        "[class*='cookie-consent']",
        "[class*='cookiebanner']",
        "[id*='cookie-banner']",
        "[id*='cookie-consent']",
        "#cookiebanner",
        "#cookie-banner",
        "#cookie-consent",
        ".cookie-notification",
        ".cookieNotice"
    ]
    
    @classmethod
    def interact_with_consent(cls, driver: Union[webdriver.Chrome, Any]) -> bool:
        """
        Versucht, mit einem Cookie-Consent-Banner zu interagieren und alle nicht notwendigen Cookies abzulehnen.
        
        Args:
            driver: Der Selenium WebDriver oder ein anderer Driver, der alle Selenium-Methoden unterstützt
            
        Returns:
            True, wenn eine Interaktion mit einem Banner stattgefunden hat, sonst False
        """
        try:
            # Prüfen, ob ein Banner vorhanden ist
            for selector in cls.BANNER_DETECTION_SELECTORS:
                try:
                    banner = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.debug(f"Cookie-Banner erkannt mit Selektor: {selector}")
                    
                    # Warten, bis der Banner vollständig geladen ist
                    time.sleep(1)
                    
                    # Versuchen, direkt den "Ablehnen"-Button zu finden und zu klicken
                    for reject_selector in cls.REJECT_BUTTON_SELECTORS:
                        try:
                            reject_button = WebDriverWait(driver, 1).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, reject_selector))
                            )
                            reject_button.click()
                            logger.info(f"Cookie-Banner abgelehnt mit Selektor: {reject_selector}")
                            time.sleep(0.5)  # Kurz warten, damit die Aktion wirksam wird
                            return True
                        except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
                            continue
                    
                    # Wenn kein "Ablehnen"-Button gefunden wurde, versuchen, über die Einstellungen zu gehen
                    for settings_selector in cls.SETTINGS_BUTTON_SELECTORS:
                        try:
                            settings_button = WebDriverWait(driver, 1).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, settings_selector))
                            )
                            settings_button.click()
                            logger.info(f"Cookie-Einstellungen geöffnet mit Selektor: {settings_selector}")
                            time.sleep(1)  # Warten, bis die Einstellungen geladen sind
                            
                            # Nach einem "Ablehnen"-Button oder "Speichern"-Button suchen
                            for reject_selector in cls.REJECT_BUTTON_SELECTORS + [
                                "button:contains('Speichern')",
                                "button:contains('Save')",
                                "button:contains('Submit')",
                                "button[type='submit']"
                            ]:
                                try:
                                    reject_button = WebDriverWait(driver, 1).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, reject_selector))
                                    )
                                    reject_button.click()
                                    logger.info(f"Cookie-Einstellungen gespeichert mit Selektor: {reject_selector}")
                                    time.sleep(0.5)  # Kurz warten, damit die Aktion wirksam wird
                                    return True
                                except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
                                    continue
                        except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
                            continue
                            
                    logger.warning("Konnte keine Interaktion mit dem Cookie-Banner durchführen")
                    return False
                    
                except (NoSuchElementException, TimeoutException):
                    continue
                    
            # Kein Banner gefunden
            logger.debug("Kein Cookie-Banner erkannt")
            return False
            
        except Exception as e:
            logger.error(f"Fehler bei der Interaktion mit dem Cookie-Banner: {e}")
            return False