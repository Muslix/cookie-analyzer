"""
Consent-Manager zur Interaktion mit Cookie-Banner.
"""

import logging
import time
from typing import Union, Any, List, Dict
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
        "button[id*='onetrust'][id*='reject']",
        
        # Cookiebot
        "button[data-cui-consent-action='decline']",
        "#CybotCookiebotDialogBodyButtonDecline",
        "[aria-label*='cookie'][aria-label*='decline']",
        
        # CookieYes
        ".cookie-yes-decline-btn",
        ".cky-btn-reject",
        ".cky-decline",
        "[data-cky-tag='reject-button']",
        
        # Cookie-Script
        ".cookie-script-decline-button",
        ".cookiescript_reject",
        
        # Complianz
        ".cmplz-deny",
        ".cc-deny",
        ".cmplz-btn-deny",
        
        # Osano
        ".osano-cm-deny",
        "[data-osano-deny]",
        
        # Didomi
        ".didomi-continue-without-agreeing",
        "button[data-didomi-action='deny']",
        ".didomi-components-button--decline",
        
        # Termly
        "#termly-decline",
        ".termly-decline-button",
        
        # Borlabs - korrigierte Selektoren
        "#BorlabsCookieBox [data-cookie-refuse]",
        ".BorlabsCookie ._brlbs-refuse-btn",
        ".BorlabsCookie ._brlbs-btn[data-cookie-refuse]",
        "#CookieBoxTextDescription a[href*='cookie-refuse']",
        "#CookieBoxSaveButton[data-cookie-refuse]",
        "a._brlbs-btn._brlbs-refuse-btn",
        "a._brlbs-refuse-btn",
        "button._brlbs-refuse-btn",
        ".BorlabsCookie a[href*='cookie-refuse']",
        "a[data-cookie-refuse]",
        
        # Borlabs - "Nur essenzielle Cookies akzeptieren" Buttons
        ".brlbs-btn-accept-only-essential",
        "button.brlbs-btn-accept-only-essential",
        "button[class*='accept-only-essential']",
        "a.brlbs-btn-accept-only-essential",
        "a[class*='accept-only-essential']",
        "button[data-cookie-essentialOnly='true']",
        "a[data-cookie-essentialOnly='true']",
        "[data-cookie-individual='false']",
        ".BorlabsCookie button[data-cookie-individual='false']",
        
        # Hu-manity.co
        ".hu-consent-reject",
        
        # Command Act X
        ".commander-reject",
        ".commander-decline",
        
        # Consentmanager.net
        ".cmp-decline",
        ".cmp-denyall",
        
        # Generic (Deutsch)
        "[aria-label='Ablehnen']",
        "[aria-label='Nur essenzielle Cookies akzeptieren']",
        "[aria-label='Nur notwendige Cookies akzeptieren']",
        "[aria-label='Nur erforderliche Cookies akzeptieren']",
        "[title='Ablehnen']",
        "[title='Nur essenzielle Cookies akzeptieren']",
        "[title='Nur notwendige Cookies akzeptieren']",
        
        # Generic (Englisch)
        "[aria-label='Deny']",
        "[aria-label='Reject']",
        "[aria-label='Refuse']",
        "[aria-label='Decline']",
        "[aria-label='Accept only essential cookies']",
        "[aria-label='Accept only necessary cookies']",
        "[aria-label='Accept only required cookies']",
        "[title='Deny']",
        "[title='Reject']",
        "[title='Refuse']",
        "[title='Accept only essential cookies']",
        "[title='Accept only necessary cookies']",
        
        "[data-testid='uc-deny-all-button']",
        "a[href*='cookie-refuse']",
        
        # Generic "Nur essenzielle/notwendige Cookies"
        "button[class*='essential-only']",
        "button[class*='only-essential']",
        "button[class*='necessary-only']",
        "button[class*='only-necessary']",
        "button[class*='required-only']",
        "button[class*='only-required']"
    ]
    
    # Liste von bekannten Selektoren für "Einstellungen"-Buttons
    SETTINGS_BUTTON_SELECTORS = [
        # OneTrust
        "#onetrust-pc-btn-handler",
        ".ot-sdk-show-settings",
        
        # Cookiebot
        "button.CybotCookiebotDialogBodyButton[data-cui-denial-action='settings']",
        "#CybotCookiebotDialogBodyButtonDetails",
        
        # CookieYes
        ".cky-btn-settings",
        ".cky-btn-customize",
        "[data-cky-tag='settings-button']",
        
        # Complianz
        ".cmplz-manage-options",
        ".cc-show-settings",
        
        # Osano
        ".osano-cm-settings",
        "[data-osano-settings]",
        
        # Didomi
        ".didomi-components-button--customize",
        "button[data-didomi-action='customize']",
        
        # Termly
        "#termly-settings",
        ".termly-settings-button",
        
        # Borlabs - korrigierte Selektoren
        ".BorlabsCookie ._brlbs-btn[data-cookie-setting]",
        "#CookieBoxSettings",
        "#CookieBoxSettingsButton",
        "._brlbs-btn[data-cookie-setting]",
        "a._brlbs-btn[data-cookie-setting]",
        
        # Generic
        "[aria-label='Cookie-Einstellungen']",
        "[aria-label='Cookie settings']",
        "[aria-label='Settings']",
        "[aria-label='Preferences']",
        "[title='Einstellungen']",
        "[title='Settings']",
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
        
        # CookieYes
        ".cky-consent-container",
        ".cky-consent-bar",
        "#cookie-law-info-bar",
        
        # Cookie-Script
        "#cookiescript_injected",
        
        # Complianz
        ".cmplz-cookiebanner",
        ".cc-window",
        "#cmplz-cookiebanner-container",
        
        # Osano
        ".osano-cm-window",
        
        # Didomi
        "#didomi-host",
        ".didomi-notice-banner",
        
        # Termly
        "#termly-code-snippet-support",
        ".termly-banner",
        
        # Borlabs
        "#BorlabsCookieBox",
        ".BorlabsCookie",
        
        # Hu-manity.co
        ".hu-consent-banner",
        
        # Command Act X
        ".commander-cookie-banner",
        
        # Consentmanager.net
        ".cmp-container",
        
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
        ".cookieNotice",
        "[class*='consent']",
        "[class*='gdpr']",
        "[id*='consent']",
        "[id*='gdpr']"
    ]
    
    # Liste von Selektoren für checkboxes, die deaktiviert werden sollen
    DESELECT_CHECKBOX_SELECTORS = [
        # Verbreitete Checkbox-Selektoren
        "input[type='checkbox'][checked]:not([data-purpose='essential']):not([data-category='necessary'])",
        ".toggle-switch.checked:not([data-category='necessary']):not([data-purpose='essential'])",
        ".toggle-on:not([data-category='necessary'])",
        
        # Borlabs spezifische Selektoren
        ".BorlabsCookie input[type='checkbox'][checked]:not([id*='essential']):not([id*='necessary'])",
        ".BorlabsCookie input[type='checkbox'][name='borlabsCookieSelectAll']",
        "input[name='cookieGroup[]']:not([value='essential'])"
    ]
    
    # Liste von Consent-Manager-spezifischen JavaScript-Skripten zur Interaktion
    CONSENT_MANAGER_SCRIPTS = {
        "OneTrust": """
            if (typeof OnetrustActiveGroups !== 'undefined') {
                console.log('OneTrust gefunden');
                if (typeof OptanonWrapper === 'function') {
                    OptanonWrapper(); 
                }
                return true;
            }
            return false;
        """,
        "Cookiebot": """
            if (typeof CookieConsent !== 'undefined') {
                console.log('Cookiebot gefunden');
                if (typeof CookieConsent.decline === 'function') {
                    CookieConsent.decline(); 
                    return true;
                }
            }
            return false;
        """,
        "CookieYes": """
            if (typeof CookieYes !== 'undefined') {
                console.log('CookieYes gefunden');
                if (typeof cky_rejectAll === 'function') {
                    cky_rejectAll(); 
                    return true;
                }
            }
            return false;
        """,
        "Complianz": """
            if (typeof cmplz_accept_statistics !== 'undefined' || typeof cmplz_set_cookie_policy !== 'undefined') {
                console.log('Complianz gefunden');
                if (typeof cmplz_deny_all === 'function') {
                    cmplz_deny_all(); 
                    return true;
                } else if (typeof cmplz_set_cookie_policy === 'function') {
                    cmplz_set_cookie_policy('no'); 
                    return true;
                }
            }
            return false;
        """,
        "Borlabs": """
            if (typeof BorlabsCookie !== 'undefined') {
                console.log('Borlabs gefunden');
                try {
                    // Suche nach "Nur essenzielle Cookies" Button
                    var essentialOnly = document.querySelector('.brlbs-btn-accept-only-essential, button[class*="accept-only-essential"], a[class*="accept-only-essential"], button[data-cookie-essentialOnly="true"], a[data-cookie-essentialOnly="true"], [data-cookie-individual="false"]');
                    if (essentialOnly) {
                        console.log('Borlabs: Nur essenzielle Cookies Button gefunden');
                        essentialOnly.click();
                        return true;
                    }
                    
                    // Versuche, die akzeptierten Cookie-Gruppen zu finden und nur wesentliche zu aktivieren
                    var cookieGroups = document.querySelectorAll('input[name="cookieGroup[]"]');
                    if (cookieGroups.length > 0) {
                        // Alle Checkboxen deaktivieren außer essential/necessary
                        for (var i = 0; i < cookieGroups.length; i++) {
                            var checkbox = cookieGroups[i];
                            if (checkbox.value !== 'essential' && checkbox.value !== 'necessary') {
                                if (checkbox.checked) checkbox.click();
                            }
                        }
                        
                        // Speichern-Button finden und klicken
                        var saveButton = document.querySelector('#CookieBoxSaveButton');
                        if (saveButton) {
                            saveButton.click();
                            return true;
                        }
                    } else {
                        // Direkte Ablehnen-Links
                        var refuseLinks = document.querySelectorAll('a[data-cookie-refuse], a._brlbs-refuse-btn, a[href*="cookie-refuse"]');
                        if (refuseLinks.length > 0) {
                            refuseLinks[0].click();
                            return true;
                        }
                    }
                } catch (e) {
                    console.error('Borlabs Cookie Interaktion fehlgeschlagen:', e);
                }
            }
            return false;
        """
    }
    
    @classmethod
    def detect_consent_manager(cls, driver: Union[webdriver.Chrome, Any]) -> str:
        """
        Versucht, den verwendeten Consent-Manager zu identifizieren.
        
        Args:
            driver: Der Selenium WebDriver oder ein anderer Driver
            
        Returns:
            str: Der Name des erkannten Consent-Managers oder "Unknown"
        """
        try:
            # Überprüfe JavaScript-Variablen und Objekte
            js_detections = {
                "OneTrust": "typeof OnetrustActiveGroups !== 'undefined' || typeof OneTrust !== 'undefined'",
                "Cookiebot": "typeof CookieConsent !== 'undefined' || typeof Cookiebot !== 'undefined'",
                "CookieYes": "typeof CLI_DATA !== 'undefined' || typeof CookieYes !== 'undefined'",
                "Complianz": "typeof cmplz_accepted_categories !== 'undefined' || typeof complianz !== 'undefined'",
                "Osano": "typeof Osano !== 'undefined'",
                "Didomi": "typeof Didomi !== 'undefined'",
                "Termly": "typeof Termly !== 'undefined'",
                "Borlabs": "typeof BorlabsCookie !== 'undefined'",
                "CommandActX": "typeof TC_PRIVACY !== 'undefined'",
                "ConsentManager.net": "typeof CmpCookieName !== 'undefined'"
            }
            
            for name, js_check in js_detections.items():
                try:
                    result = driver.execute_script(f"return {js_check};")
                    if result:
                        logger.info(f"Consent-Manager erkannt: {name}")
                        return name
                except Exception:
                    continue
            
            # Überprüfe DOM-Elemente
            dom_detections = {
                "OneTrust": "#onetrust-banner-sdk, #onetrust-consent-sdk",
                "Cookiebot": "#CybotCookiebotDialog",
                "CookieYes": ".cky-consent-container, #cookie-law-info-bar",
                "Complianz": ".cmplz-cookiebanner, .cc-window",
                "Osano": ".osano-cm-window",
                "Didomi": "#didomi-host",
                "Termly": "#termly-code-snippet-support",
                "Borlabs": "#BorlabsCookieBox, .BorlabsCookie",
                "CommandActX": ".commander-cookie-banner",
                "ConsentManager.net": ".cmp-container"
            }
            
            for name, selector in dom_detections.items():
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and len(elements) > 0:
                        logger.info(f"Consent-Manager erkannt (DOM): {name}")
                        return name
                except Exception:
                    continue
            
            return "Unknown"
        except Exception as e:
            logger.error(f"Fehler bei der Erkennung des Consent-Managers: {e}")
            return "Unknown"
    
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
            # Zuerst eine kurze Verzögerung, damit der Banner vollständig geladen wird
            time.sleep(1)
            
            # Consent-Manager identifizieren
            consent_manager = cls.detect_consent_manager(driver)
            
            # Versuchen, über JavaScript direkt mit dem Consent-Manager zu interagieren
            if (consent_manager != "Unknown" and consent_manager in cls.CONSENT_MANAGER_SCRIPTS):
                try:
                    success = driver.execute_script(cls.CONSENT_MANAGER_SCRIPTS[consent_manager])
                    if success:
                        logger.info(f"Erfolgreich mit {consent_manager}-API interagiert")
                        time.sleep(0.5)
                        return True
                except Exception as e:
                    logger.debug(f"JavaScript-Interaktion mit {consent_manager} fehlgeschlagen: {e}")
            
            # Prüfen, ob ein Banner vorhanden ist
            for selector in cls.BANNER_DETECTION_SELECTORS:
                try:
                    banner = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.debug(f"Cookie-Banner erkannt mit Selektor: {selector}")
                    
                    # Warten, bis der Banner vollständig geladen ist
                    time.sleep(1)
                    
                    # Versuchen, direkt den "Ablehnen"-Button oder "Nur essenzielle Cookies" zu finden und zu klicken
                    for reject_selector in cls.REJECT_BUTTON_SELECTORS:
                        try:
                            # Prüfen, ob der Selektor jQuery-Syntax enthält
                            if ":contains(" in reject_selector:
                                continue  # Überspringe ungültige Selektoren
                                
                            # Versuchen, den Button zu finden und zu klicken
                            # Nehme eine kürzere Wartezeit, da wir viele Selektoren durchprobieren
                            reject_button = WebDriverWait(driver, 0.5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, reject_selector))
                            )
                            
                            # Debug-Information für den Button, der gefunden wurde
                            button_text = driver.execute_script("return arguments[0].textContent", reject_button).strip()
                            logger.debug(f"Button gefunden: '{button_text}' mit Selektor: {reject_selector}")
                            
                            # Versuche, den Button zu klicken
                            reject_button.click()
                            logger.info(f"Cookie-Banner interagiert mit Selektor: {reject_selector} (Text: '{button_text}')")
                            time.sleep(0.5)  # Kurz warten, damit die Aktion wirksam wird
                            return True
                        except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
                            continue
                        except Exception as e:
                            logger.debug(f"Fehler bei Selektor {reject_selector}: {str(e)}")
                            continue
                    
                    # Wenn kein "Ablehnen"-Button gefunden wurde, versuchen, über die Einstellungen zu gehen
                    for settings_selector in cls.SETTINGS_BUTTON_SELECTORS:
                        try:
                            # Prüfen, ob der Selektor jQuery-Syntax enthält
                            if ":contains(" in settings_selector:
                                continue  # Überspringe ungültige Selektoren
                                
                            settings_button = WebDriverWait(driver, 1).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, settings_selector))
                            )
                            settings_button.click()
                            logger.info(f"Cookie-Einstellungen geöffnet mit Selektor: {settings_selector}")
                            time.sleep(1)  # Warten, bis die Einstellungen geladen sind
                            
                            # Versuchen, alle nicht notwendigen Checkboxen zu deaktivieren
                            for checkbox_selector in cls.DESELECT_CHECKBOX_SELECTORS:
                                try:
                                    # Prüfen, ob der Selektor jQuery-Syntax enthält
                                    if ":contains(" in checkbox_selector or ":has(" in checkbox_selector:
                                        continue  # Überspringe ungültige Selektoren
                                        
                                    checkboxes = driver.find_elements(By.CSS_SELECTOR, checkbox_selector)
                                    for checkbox in checkboxes:
                                        try:
                                            if checkbox.is_displayed() and checkbox.is_enabled():
                                                driver.execute_script("arguments[0].click();", checkbox)
                                                logger.debug(f"Checkbox deaktiviert: {checkbox_selector}")
                                        except Exception:
                                            continue
                                except Exception:
                                    continue
                            
                            # Nach einem "Ablehnen"-Button oder "Speichern"-Button suchen
                            safe_selectors = [
                                "button[type='submit']",
                                ".save-button",
                                "#save-settings",
                                "#submit-settings",
                                "[data-action='save']",
                                "#CookieBoxSaveButton"
                            ]
                            
                            for reject_selector in cls.REJECT_BUTTON_SELECTORS + safe_selectors:
                                try:
                                    # Prüfen, ob der Selektor jQuery-Syntax enthält
                                    if ":contains(" in reject_selector:
                                        continue  # Überspringe ungültige Selektoren
                                        
                                    reject_button = WebDriverWait(driver, 1).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, reject_selector))
                                    )
                                    reject_button.click()
                                    logger.info(f"Cookie-Einstellungen gespeichert mit Selektor: {reject_selector}")
                                    time.sleep(0.5)  # Kurz warten, damit die Aktion wirksam wird
                                    return True
                                except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
                                    continue
                                except Exception as e:
                                    logger.debug(f"Fehler bei Selektor {reject_selector}: {str(e)}")
                                    continue
                        except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
                            continue
                        except Exception as e:
                            logger.debug(f"Fehler bei Selektor {settings_selector}: {str(e)}")
                            continue
                            
                    logger.warning("Konnte keine Interaktion mit dem Cookie-Banner durchführen")
                    return False
                    
                except (NoSuchElementException, TimeoutException):
                    continue
                except Exception as e:
                    logger.debug(f"Fehler bei Selektor {selector}: {str(e)}")
                    continue
                    
            # Kein Banner gefunden
            logger.debug("Kein Cookie-Banner erkannt")
            return False
            
        except Exception as e:
            logger.error(f"Fehler bei der Interaktion mit dem Cookie-Banner: {e}")
            return False