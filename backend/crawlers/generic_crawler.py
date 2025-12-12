"""
Generischer Crawler fuer benutzerdefinierte Portale.
Versucht automatisch Login, Suche und Ausschreibungen zu finden.
"""
import asyncio
import re
import hashlib
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from typing import Optional


class GenericPortalCrawler:
    """Generischer Crawler der versucht, beliebige Portale zu crawlen"""
    
    def __init__(self, portal_config: dict):
        self.config = portal_config
        self.name = portal_config.get("name", "Unbekannt")
        self.url = portal_config.get("url", "")
        self.username = portal_config.get("username", "")
        self.password = portal_config.get("password", "")
        self.region = portal_config.get("region", "")
        self.criteria = portal_config.get("criteria", "")
        
        # Optionale benutzerdefinierte Selektoren
        self.selectors = portal_config.get("selectors", {})
    
    async def crawl(self) -> list:
        """Hauptmethode - crawlt das Portal"""
        print(f"  Crawle {self.name} (generisch)...")
        tenders = []
        
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # 1. Startseite oeffnen
            await page.goto(self.url, timeout=30000)
            await asyncio.sleep(2)
            
            # 2. Login versuchen wenn Credentials vorhanden
            if self.username and self.password:
                await self._try_login(page)
            
            # 3. Ausschreibungen suchen
            tenders = await self._find_tenders(page)
            
            print(f"    -> {len(tenders)} Ausschreibungen gefunden")
            
        except Exception as e:
            print(f"    Fehler bei {self.name}: {e}")
        finally:
            await browser.close()
            await pw.stop()
        
        return tenders
    
    async def _try_login(self, page) -> bool:
        """Versucht sich einzuloggen"""
        try:
            # Benutzerdefinierte Selektoren oder automatische Erkennung
            username_sel = self.selectors.get("username", None)
            password_sel = self.selectors.get("password", None)
            login_btn_sel = self.selectors.get("loginButton", None)
            
            # Falls keine Selektoren definiert, versuche automatische Erkennung
            if not username_sel:
                username_sel = await self._find_username_field(page)
            if not password_sel:
                password_sel = await self._find_password_field(page)
            
            if not username_sel or not password_sel:
                print(f"    Login-Felder nicht gefunden bei {self.name}")
                return False
            
            # Login-Seite finden
            login_urls = ["/login", "/anmelden", "/signin", "/auth", "/user/login", "/Account/Login"]
            for login_path in login_urls:
                try:
                    test_url = self.url.rstrip("/") + login_path
                    await page.goto(test_url, timeout=10000)
                    await asyncio.sleep(1)
                    
                    # Prüfe ob Login-Formular vorhanden
                    username_field = await page.query_selector(username_sel)
                    if username_field:
                        break
                except:
                    continue
            
            # Username eingeben
            username_field = await page.query_selector(username_sel)
            if username_field:
                await username_field.fill(self.username)
            
            # Passwort eingeben
            password_field = await page.query_selector(password_sel)
            if password_field:
                await password_field.fill(self.password)
            
            # Login-Button klicken oder Enter druecken
            if login_btn_sel:
                btn = await page.query_selector(login_btn_sel)
                if btn:
                    await btn.click()
            else:
                await page.keyboard.press("Enter")
            
            await asyncio.sleep(3)
            
            # Pruefen ob Login erfolgreich
            content = await page.content()
            if any(x in content.lower() for x in ["logout", "abmelden", "willkommen", "dashboard", "mein konto"]):
                print(f"    Login erfolgreich bei {self.name}")
                return True
            
            return False
            
        except Exception as e:
            print(f"    Login-Fehler bei {self.name}: {e}")
            return False
    
    async def _find_username_field(self, page) -> Optional[str]:
        """Findet automatisch das Username-Feld"""
        selectors = [
            'input[name="username"]',
            'input[name="email"]',
            'input[name="user"]',
            'input[name="login"]',
            'input[name="Email"]',
            'input[name="Username"]',
            'input[id="username"]',
            'input[id="email"]',
            'input[id="user"]',
            'input[type="email"]',
            'input[type="text"]:first-of-type',
        ]
        
        for sel in selectors:
            try:
                elem = await page.query_selector(sel)
                if elem:
                    return sel
            except:
                continue
        
        return None
    
    async def _find_password_field(self, page) -> Optional[str]:
        """Findet automatisch das Passwort-Feld"""
        selectors = [
            'input[type="password"]',
            'input[name="password"]',
            'input[name="Password"]',
            'input[id="password"]',
        ]
        
        for sel in selectors:
            try:
                elem = await page.query_selector(sel)
                if elem:
                    return sel
            except:
                continue
        
        return None
    
    async def _find_tenders(self, page) -> list:
        """Findet Ausschreibungen auf der Seite"""
        tenders = []
        
        # Benutzerdefinierter Selektor oder automatische Erkennung
        tender_sel = self.selectors.get("tenderList", None)
        
        # Verschiedene Seiten durchsuchen
        search_paths = [
            "",  # Startseite
            "/ausschreibungen",
            "/tenders",
            "/vergaben",
            "/public",
            "/search",
            "/suche",
            "/bekanntmachungen",
        ]
        
        for path in search_paths:
            try:
                test_url = self.url.rstrip("/") + path
                await page.goto(test_url, timeout=15000)
                await asyncio.sleep(2)
                
                # Versuche Ausschreibungen zu finden
                found = await self._extract_tenders_from_page(page)
                if found:
                    tenders.extend(found)
                    break  # Erste erfolgreiche Seite reicht
                    
            except:
                continue
        
        return tenders
    
    async def _extract_tenders_from_page(self, page) -> list:
        """Extrahiert Ausschreibungen von der aktuellen Seite"""
        tenders = []
        
        # Benutzerdefinierter Selektor
        tender_sel = self.selectors.get("tenderList", None)
        
        if tender_sel:
            # Verwende benutzerdefinierten Selektor
            elements = await page.query_selector_all(tender_sel)
        else:
            # Automatische Erkennung - versuche verschiedene Selektoren
            selectors_to_try = [
                'a[href*="ausschreibung"]',
                'a[href*="tender"]',
                'a[href*="vergabe"]',
                'a[href*="projekt"]',
                'table tr',
                '.tender-item',
                '.ausschreibung',
                'article',
                '.list-item',
                '.result-item',
            ]
            
            elements = []
            for sel in selectors_to_try:
                try:
                    found = await page.query_selector_all(sel)
                    if len(found) > 2:  # Mindestens 3 Elemente
                        elements = found
                        break
                except:
                    continue
        
        # Ausschreibungen extrahieren
        for elem in elements[:20]:  # Max 20
            try:
                text = await elem.text_content()
                if not text or len(text.strip()) < 15:
                    continue
                
                text = text.strip()
                clean_text = " ".join(text.split())
                
                # Nur relevante Inhalte
                if len(clean_text) > 500:
                    clean_text = clean_text[:500]
                
                # ID generieren
                tender_id = hashlib.md5(clean_text.encode()).hexdigest()[:12]
                
                # Link finden
                link = ""
                link_elem = await elem.query_selector("a")
                if link_elem:
                    href = await link_elem.get_attribute("href") or ""
                    if href:
                        if href.startswith("/"):
                            link = self.url.rstrip("/") + href
                        elif href.startswith("http"):
                            link = href
                        else:
                            link = self.url
                else:
                    link = self.url
                
                # Titel extrahieren (erster Teil des Textes)
                title = clean_text[:150] if len(clean_text) > 150 else clean_text
                
                # Stadt extrahieren
                city = self._extract_city(clean_text)
                location = f"{city}, {self.region}" if city else self.region or "Unbekannt"
                
                tenders.append({
                    "id": f"custom_{tender_id}",
                    "title": title,
                    "authority": self.name,
                    "location": location,
                    "deadline": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
                    "published_at": datetime.now().strftime("%Y-%m-%d"),
                    "budget": None,
                    "category": self.criteria or "Bauleistungen",
                    "description": clean_text,
                    "source_url": link,
                    "source_portal": self.name
                })
                
            except:
                continue
        
        return tenders
    
    def _extract_city(self, text: str) -> str:
        """Extrahiert Stadtname aus Text"""
        cities = [
            "Wien", "Graz", "Linz", "Salzburg", "Innsbruck", "Klagenfurt",
            "Berlin", "Hamburg", "Muenchen", "Koeln", "Frankfurt", "Stuttgart",
            "Duesseldorf", "Leipzig", "Dortmund", "Essen", "Bremen", "Dresden",
            "Hannover", "Nuernberg", "Duisburg", "Bochum", "Wuppertal", "Bielefeld",
            "Bonn", "Muenster", "Karlsruhe", "Mannheim", "Augsburg", "Wiesbaden",
            "Freiburg", "Mainz", "Kassel", "Heidelberg", "Ulm", "München", "Köln",
            "Düsseldorf", "Nürnberg", "Zürich", "Basel", "Bern", "Genf"
        ]
        
        for city in cities:
            if city.lower() in text.lower():
                return city
        
        # PLZ + Ort suchen
        match = re.search(r'(\d{4,5})\s+([A-Z][a-zäöüß]+)', text)
        if match:
            return match.group(2)
        
        return ""


async def crawl_custom_portal(portal_config: dict) -> list:
    """Hilfsfunktion zum Crawlen eines benutzerdefinierten Portals"""
    crawler = GenericPortalCrawler(portal_config)
    return await crawler.crawl()

