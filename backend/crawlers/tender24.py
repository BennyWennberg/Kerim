"""
Crawler für tender24.de (Baden-Württemberg)

ANPASSUNG ERFORDERLICH:
1. Öffne https://www.tender24.de im Browser
2. Melde dich an und inspiziere die Elemente (F12)
3. Passe die Selektoren unten entsprechend an
"""
from typing import List, Dict, Any, Optional
from .base import BaseCrawler


class Tender24Crawler(BaseCrawler):
    """Crawler für tender24.de"""
    
    # ============================================
    # SELEKTOREN - HIER ANPASSEN!
    # ============================================
    
    LOGIN_URL = "/login"
    USERNAME_SELECTOR = 'input[name="username"], input[name="email"], input[type="text"]#username'
    PASSWORD_SELECTOR = 'input[name="password"], input[type="password"]#password'
    LOGIN_BUTTON_SELECTOR = 'button[type="submit"], .btn-login, input[type="submit"]'
    LOGIN_SUCCESS_INDICATOR = 'logout, abmelden, mein konto'
    
    SEARCH_URL = "/ausschreibungen"
    SEARCH_INPUT_SELECTOR = 'input[name="q"], input.search, input[type="search"]'
    TENDER_LINK_SELECTOR = 'a[href*="/ausschreibung/"], a[href*="/tender/"], .ausschreibung-link'
    
    TITLE_SELECTOR = 'h1, .ausschreibung-title'
    AUTHORITY_SELECTOR = '.vergabestelle, .auftraggeber'
    DESCRIPTION_SELECTOR = '.beschreibung, .leistung'
    DEADLINE_SELECTOR = '.frist, .abgabefrist'
    BUDGET_SELECTOR = '.budget, .wert'
    LOCATION_SELECTOR = '.ort, .region'
    
    # ============================================
    
    async def login(self) -> bool:
        try:
            await self.page.goto(f"{self.url}{self.LOGIN_URL}")
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
