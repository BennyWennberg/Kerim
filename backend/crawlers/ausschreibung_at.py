"""
Crawler für ausschreibung.at (Österreich)

ANPASSUNG ERFORDERLICH:
1. Öffne https://www.ausschreibung.at im Browser
2. Melde dich an und inspiziere die Elemente (F12)
3. Passe die Selektoren unten entsprechend an
"""
from typing import List, Dict, Any, Optional
from .base import BaseCrawler


class AusschreibungAtCrawler(BaseCrawler):
    """Crawler für ausschreibung.at"""
    
    # ============================================
    # SELEKTOREN - HIER ANPASSEN!
    # ============================================
    
    # Login-Seite (optional - es gibt auch öffentliche Ausschreibungen)
    LOGIN_URL = "/Account/Login"
    USERNAME_SELECTOR = 'input[name="Email"], input[type="email"], #Email'
    PASSWORD_SELECTOR = 'input[name="Password"], input[type="password"], #Password'
    LOGIN_BUTTON_SELECTOR = 'button[type="submit"], input[type="submit"]'
    LOGIN_SUCCESS_INDICATOR = 'abmelden, logout, mein konto, willkommen'
    
    # Ausschreibungs-Suche - ÖFFENTLICHE SEITE!
    SEARCH_URL = "/Ausschreibungskarte"
    SEARCH_INPUT_SELECTOR = 'input[name="search"], input.form-control'
    SEARCH_BUTTON_SELECTOR = 'button[type="submit"], .btn-primary'
    
    # Ergebnisliste - Links zu /Ausschreibung/XXXXXX/
    TENDER_LIST_SELECTOR = 'a[href*="/Ausschreibung/"]'
    TENDER_LINK_SELECTOR = 'a[href*="/Ausschreibung/"]'
    
    # Detail-Seite
    TITLE_SELECTOR = 'h1, .tender-title, .ausschreibung-titel, .detail-title'
    AUTHORITY_SELECTOR = '.auftraggeber, .vergabestelle, .authority, .contracting-authority'
    DESCRIPTION_SELECTOR = '.beschreibung, .description, .tender-description, .leistungsbeschreibung'
    DEADLINE_SELECTOR = '.frist, .deadline, .abgabefrist, .submission-deadline'
    BUDGET_SELECTOR = '.budget, .auftragswert, .contract-value, .schaetzwert'
    LOCATION_SELECTOR = '.ort, .location, .ausfuehrungsort, .place'
    
    # ============================================
    
    async def login(self) -> bool:
        """Login auf ausschreibung.at"""
        try:
            login_url = f"{self.url}{self.LOGIN_URL}"
            print(f"[{self.name}] Navigiere zu {login_url}")
            await self.page.goto(login_url)
            await self.page.wait_for_load_state("networkidle")
            await self.wait(1)
            
            # Screenshot für Debugging (optional)
            # await self.page.screenshot(path=f"debug_login_{self.name}.png")
            
            # Username eingeben
            username_field = await self.page.query_selector(self.USERNAME_SELECTOR)
            if not username_field:
                print(f"[{self.name}] WARNUNG: Username-Feld nicht gefunden mit Selektor: {self.USERNAME_SELECTOR}")
                return False
            
            await username_field.fill(self.username)
            print(f"[{self.name}] Username eingegeben")
            
            # Password eingeben
            password_field = await self.page.query_selector(self.PASSWORD_SELECTOR)
            if not password_field:
                print(f"[{self.name}] WARNUNG: Password-Feld nicht gefunden mit Selektor: {self.PASSWORD_SELECTOR}")
                return False
            
            await password_field.fill(self.password)
            print(f"[{self.name}] Password eingegeben")
            
            # Login Button klicken
            login_button = await self.page.query_selector(self.LOGIN_BUTTON_SELECTOR)
            if not login_button:
                print(f"[{self.name}] WARNUNG: Login-Button nicht gefunden mit Selektor: {self.LOGIN_BUTTON_SELECTOR}")
                # Versuche Enter zu drücken
                await self.page.keyboard.press("Enter")
            else:
                await login_button.click()
            
            await self.page.wait_for_load_state("networkidle")
            await self.wait(2)
            
            # Prüfen ob Login erfolgreich
            content = (await self.page.content()).lower()
            success_keywords = self.LOGIN_SUCCESS_INDICATOR.split(', ')
            
            for keyword in success_keywords:
                if keyword in content:
                    print(f"[{self.name}] Login erfolgreich! ('{keyword}' gefunden)")
                    return True
            
            print(f"[{self.name}] Login möglicherweise fehlgeschlagen - keine Erfolgsindikator gefunden")
            return False
            
        except Exception as e:
            print(f"[{self.name}] Login-Fehler: {e}")
            return False
    
    async def scrape_tender_list(self) -> List[str]:
        """Scrapt die Ausschreibungsliste"""
        urls = []
        try:
            search_url = f"{self.url}{self.SEARCH_URL}"
            print(f"[{self.name}] Navigiere zu Suche: {search_url}")
            await self.page.goto(search_url)
            await self.page.wait_for_load_state("networkidle")
            await self.wait(2)
            
            # Optional: Suchfilter anwenden
            if self.criteria:
                search_input = await self.page.query_selector(self.SEARCH_INPUT_SELECTOR)
                if search_input:
                    await search_input.fill(self.criteria)
                    print(f"[{self.name}] Suchbegriff eingegeben: {self.criteria}")
                    
                    search_button = await self.page.query_selector(self.SEARCH_BUTTON_SELECTOR)
                    if search_button:
                        await search_button.click()
                    else:
                        await self.page.keyboard.press("Enter")
                    
                    await self.page.wait_for_load_state("networkidle")
                    await self.wait(2)
            
            # Alle Ausschreibungs-Links sammeln
            links = await self.page.query_selector_all(self.TENDER_LINK_SELECTOR)
            print(f"[{self.name}] {len(links)} Links gefunden")
            
            for link in links:
                href = await link.get_attribute("href")
                if href:
                    if not href.startswith("http"):
                        href = f"{self.url}{href}"
                    urls.append(href)
            
            # Duplikate entfernen
            urls = list(set(urls))
            print(f"[{self.name}] {len(urls)} eindeutige URLs")
            
        except Exception as e:
            print(f"[{self.name}] Fehler beim Laden der Liste: {e}")
        
        return urls
    
    async def scrape_tender_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrapt Details einer Ausschreibung"""
        try:
            await self.page.goto(url)
            await self.page.wait_for_load_state("networkidle")
            await self.wait(1)
            
            # Daten extrahieren
            title = await self._get_text(self.TITLE_SELECTOR)
            authority = await self._get_text(self.AUTHORITY_SELECTOR)
            description = await self._get_text(self.DESCRIPTION_SELECTOR)
            deadline = await self._get_text(self.DEADLINE_SELECTOR)
            budget = await self._get_text(self.BUDGET_SELECTOR)
            location = await self._get_text(self.LOCATION_SELECTOR)
            
            if not title:
                print(f"[{self.name}] Kein Titel gefunden für {url}")
                return None
            
            return self.create_tender_dict(
                title=title,
                authority=authority or "Nicht angegeben",
                location=location or self.region,
                deadline=deadline or "Nicht angegeben",
                description=description or title,
                source_url=url,
                budget=budget,
                category=self.criteria
            )
            
        except Exception as e:
            print(f"[{self.name}] Fehler bei Detail-Scraping: {e}")
            return None
    
    async def _get_text(self, selector: str) -> str:
        """Hilfsmethode: Text aus Element extrahieren"""
        try:
            # Versuche alle Selektoren (kommagetrennt)
            for sel in selector.split(', '):
                element = await self.page.query_selector(sel.strip())
                if element:
                    text = await element.text_content()
                    if text:
                        return text.strip()
        except Exception as e:
            pass
        return ""
