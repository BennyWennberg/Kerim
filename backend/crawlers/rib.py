"""
Crawler für meinauftrag.rib.de (Bayern)

ANPASSUNG ERFORDERLICH:
1. Öffne https://meinauftrag.rib.de im Browser
2. Melde dich an und inspiziere die Elemente (F12)
3. Passe die Selektoren unten entsprechend an
"""
from typing import List, Dict, Any, Optional
from .base import BaseCrawler


class RibCrawler(BaseCrawler):
    """Crawler für meinauftrag.rib.de"""
    
    # ============================================
    # SELEKTOREN - HIER ANPASSEN!
    # ============================================
    
    LOGIN_URL = "/public/informations"
    LOGIN_LINK_SELECTOR = 'a[href*="login"], .login-link, a.btn-login'
    USERNAME_SELECTOR = 'input[name="username"], input[name="email"], input[type="email"], input[type="text"][name*="user"]'
    PASSWORD_SELECTOR = 'input[name="password"], input[type="password"]'
    LOGIN_BUTTON_SELECTOR = 'button[type="submit"], input[type="submit"], .btn-login'
    LOGIN_SUCCESS_INDICATOR = 'logout, abmelden, meine aufträge, dashboard'
    
    SEARCH_URL = "/public/informations"
    SEARCH_INPUT_SELECTOR = 'input[type="search"], .search-input, input[name="search"]'
    TENDER_LINK_SELECTOR = 'a[href*="/tender/"], a[href*="/ausschreibung/"], tr.clickable a, .tender-row a'
    
    TITLE_SELECTOR = 'h1, .tender-title, .auftrag-titel'
    AUTHORITY_SELECTOR = '.auftraggeber, .client-name'
    DESCRIPTION_SELECTOR = '.beschreibung, .description, .leistungsverzeichnis'
    DEADLINE_SELECTOR = '.abgabefrist, .submission-date'
    BUDGET_SELECTOR = '.budget, .auftragssumme'
    LOCATION_SELECTOR = '.ausfuehrungsort, .location'
    
    # ============================================
    
    async def login(self) -> bool:
        try:
            await self.page.goto(f"{self.url}{self.LOGIN_URL}")
            await self.page.wait_for_load_state("networkidle")
            await self.wait(1)
            
            # Erst zum Login-Bereich navigieren (falls nötig)
            login_link = await self.page.query_selector(self.LOGIN_LINK_SELECTOR)
            if login_link:
                await login_link.click()
                await self.page.wait_for_load_state("networkidle")
                await self.wait(1)
            
            username_field = await self.page.query_selector(self.USERNAME_SELECTOR)
            if username_field:
                await username_field.fill(self.username)
            else:
                print(f"[{self.name}] Username-Feld nicht gefunden")
                return False
            
            password_field = await self.page.query_selector(self.PASSWORD_SELECTOR)
            if password_field:
                await password_field.fill(self.password)
            else:
                print(f"[{self.name}] Password-Feld nicht gefunden")
                return False
            
            login_button = await self.page.query_selector(self.LOGIN_BUTTON_SELECTOR)
            if login_button:
                await login_button.click()
            else:
                await self.page.keyboard.press("Enter")
            
            await self.page.wait_for_load_state("networkidle")
            await self.wait(2)
            
            content = (await self.page.content()).lower()
            for keyword in self.LOGIN_SUCCESS_INDICATOR.split(', '):
                if keyword in content:
                    print(f"[{self.name}] Login erfolgreich!")
                    return True
            
            return False
            
        except Exception as e:
            print(f"[{self.name}] Login-Fehler: {e}")
            return False
    
    async def scrape_tender_list(self) -> List[str]:
        urls = []
        try:
            await self.page.goto(f"{self.url}{self.SEARCH_URL}")
            await self.page.wait_for_load_state("networkidle")
            await self.wait(2)
            
            if self.criteria:
                search_input = await self.page.query_selector(self.SEARCH_INPUT_SELECTOR)
                if search_input:
                    await search_input.fill(self.criteria)
                    await self.page.keyboard.press("Enter")
                    await self.page.wait_for_load_state("networkidle")
                    await self.wait(2)
            
            links = await self.page.query_selector_all(self.TENDER_LINK_SELECTOR)
            for link in links:
                href = await link.get_attribute("href")
                if href:
                    if not href.startswith("http"):
                        href = f"{self.url}{href}"
                    urls.append(href)
            
            urls = list(set(urls))
            print(f"[{self.name}] {len(urls)} URLs gefunden")
            
        except Exception as e:
            print(f"[{self.name}] Fehler: {e}")
        
        return urls
    
    async def scrape_tender_detail(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            await self.page.goto(url)
            await self.page.wait_for_load_state("networkidle")
            
            title = await self._get_text(self.TITLE_SELECTOR)
            if not title:
                return None
            
            return self.create_tender_dict(
                title=title,
                authority=await self._get_text(self.AUTHORITY_SELECTOR) or "Nicht angegeben",
                location=await self._get_text(self.LOCATION_SELECTOR) or self.region,
                deadline=await self._get_text(self.DEADLINE_SELECTOR) or "Nicht angegeben",
                description=await self._get_text(self.DESCRIPTION_SELECTOR) or title,
                source_url=url,
                budget=await self._get_text(self.BUDGET_SELECTOR),
                category=self.criteria
            )
            
        except Exception as e:
            print(f"[{self.name}] Fehler: {e}")
            return None
    
    async def _get_text(self, selector: str) -> str:
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
