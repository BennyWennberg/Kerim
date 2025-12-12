"""
Crawler für staatsanzeiger-eservices.de (Deutschland)

ANPASSUNG ERFORDERLICH:
1. Öffne https://www.staatsanzeiger-eservices.de im Browser
2. Melde dich an und inspiziere die Elemente (F12)
3. Passe die Selektoren unten entsprechend an
"""
from typing import List, Dict, Any, Optional
from .base import BaseCrawler


class StaatsanzeigerCrawler(BaseCrawler):
    """Crawler für staatsanzeiger-eservices.de"""
    
    # ============================================
    # SELEKTOREN - HIER ANPASSEN!
    # ============================================
    
    # Login-Seite
    LOGIN_URL = "/login"
    USERNAME_SELECTOR = 'input[name="username"], input[name="user"], input[name="login"], input[type="text"]#username'
    PASSWORD_SELECTOR = 'input[name="password"], input[type="password"]'
    LOGIN_BUTTON_SELECTOR = 'button[type="submit"], input[type="submit"], .btn-primary, .login-btn'
    LOGIN_SUCCESS_INDICATOR = 'abmelden, logout, mein konto, dashboard, willkommen'
    
    # Ausschreibungs-Suche
    SEARCH_URL = "/vergabe/suche"
    SEARCH_INPUT_SELECTOR = 'input[name="search"], input[name="q"], input.search-input, #suchbegriff'
    REGION_SELECT_SELECTOR = 'select[name="region"], select[name="bundesland"], #region'
    SEARCH_BUTTON_SELECTOR = 'button[type="submit"], .btn-search, input[type="submit"]'
    
    # Ergebnisliste
    TENDER_LINK_SELECTOR = 'a[href*="/vergabe/"], a[href*="/ausschreibung/"], .vergabe-link, .tender-row a'
    
    # Detail-Seite
    TITLE_SELECTOR = 'h1, .vergabe-titel, .detail-title, .ausschreibung-title'
    AUTHORITY_SELECTOR = '.vergabestelle, .auftraggeber, .contracting-authority'
    DESCRIPTION_SELECTOR = '.leistungsbeschreibung, .beschreibung, .description'
    DEADLINE_SELECTOR = '.abgabefrist, .frist, .deadline, .submission-deadline'
    BUDGET_SELECTOR = '.auftragswert, .schaetzwert, .budget'
    LOCATION_SELECTOR = '.ausfuehrungsort, .ort, .location'
    
    # ============================================
    
    async def login(self) -> bool:
        """Login auf staatsanzeiger-eservices.de"""
        try:
            login_url = f"{self.url}{self.LOGIN_URL}"
            print(f"[{self.name}] Navigiere zu {login_url}")
            await self.page.goto(login_url)
            await self.page.wait_for_load_state("networkidle")
            await self.wait(1)
            
            # Username eingeben
            username_field = await self.page.query_selector(self.USERNAME_SELECTOR)
            if not username_field:
                print(f"[{self.name}] WARNUNG: Username-Feld nicht gefunden")
                # Versuche alternatives Formular zu finden
                await self.page.screenshot(path=f"debug_{self.name}_login.png")
                return False
            
            await username_field.fill(self.username)
            print(f"[{self.name}] Username eingegeben: {self.username}")
            
            # Password eingeben
            password_field = await self.page.query_selector(self.PASSWORD_SELECTOR)
            if not password_field:
                print(f"[{self.name}] WARNUNG: Password-Feld nicht gefunden")
                return False
            
            await password_field.fill(self.password)
            
            # Login Button klicken
            login_button = await self.page.query_selector(self.LOGIN_BUTTON_SELECTOR)
            if login_button:
                await login_button.click()
            else:
                await self.page.keyboard.press("Enter")
            
            await self.page.wait_for_load_state("networkidle")
            await self.wait(2)
            
            # Prüfen ob Login erfolgreich
            content = (await self.page.content()).lower()
            for keyword in self.LOGIN_SUCCESS_INDICATOR.split(', '):
                if keyword in content:
                    print(f"[{self.name}] Login erfolgreich!")
                    return True
            
            print(f"[{self.name}] Login möglicherweise fehlgeschlagen")
            return False
            
        except Exception as e:
            print(f"[{self.name}] Login-Fehler: {e}")
            return False
    
    async def scrape_tender_list(self) -> List[str]:
        """Scrapt die Ausschreibungsliste"""
        urls = []
        try:
            search_url = f"{self.url}{self.SEARCH_URL}"
            print(f"[{self.name}] Navigiere zu: {search_url}")
            await self.page.goto(search_url)
            await self.page.wait_for_load_state("networkidle")
            await self.wait(2)
            
            # Suchfilter anwenden
            if self.criteria:
                search_input = await self.page.query_selector(self.SEARCH_INPUT_SELECTOR)
                if search_input:
                    await search_input.fill(self.criteria)
                    print(f"[{self.name}] Suchbegriff: {self.criteria}")
                    
                    await self.page.keyboard.press("Enter")
                    await self.page.wait_for_load_state("networkidle")
                    await self.wait(2)
            
            # Links sammeln
            links = await self.page.query_selector_all(self.TENDER_LINK_SELECTOR)
            print(f"[{self.name}] {len(links)} Links gefunden")
            
            for link in links:
                href = await link.get_attribute("href")
                if href:
                    if not href.startswith("http"):
                        href = f"{self.url}{href}"
                    urls.append(href)
            
            urls = list(set(urls))
            
        except Exception as e:
            print(f"[{self.name}] Fehler: {e}")
        
        return urls
    
    async def scrape_tender_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrapt Details einer Ausschreibung"""
        try:
            await self.page.goto(url)
            await self.page.wait_for_load_state("networkidle")
            
            title = await self._get_text(self.TITLE_SELECTOR)
            authority = await self._get_text(self.AUTHORITY_SELECTOR)
            description = await self._get_text(self.DESCRIPTION_SELECTOR)
            deadline = await self._get_text(self.DEADLINE_SELECTOR)
            budget = await self._get_text(self.BUDGET_SELECTOR)
            location = await self._get_text(self.LOCATION_SELECTOR)
            
            if not title:
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
            print(f"[{self.name}] Fehler: {e}")
            return None
    
    async def _get_text(self, selector: str) -> str:
        """Text aus Element extrahieren"""
        try:
            for sel in selector.split(', '):
                element = await self.page.query_selector(sel.strip())
                if element:
                    text = await element.text_content()
                    if text:
                        return text.strip()
        except:
            pass
        return ""
