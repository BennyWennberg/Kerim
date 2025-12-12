from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, Browser, Page
from typing import List, Dict, Any, Optional
import asyncio
import hashlib
from datetime import datetime

import os
import sys

# Füge Backend-Ordner zum Pfad hinzu
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from config import HEADLESS_MODE, CRAWL_DELAY_SECONDS


class BaseCrawler(ABC):
    """Abstrakte Basisklasse für alle Portal-Crawler"""
    
    def __init__(self, portal_config: Dict[str, Any]):
        self.config = portal_config
        self.name = portal_config.get("name", "Unknown")
        self.url = portal_config.get("url", "")
        self.username = portal_config.get("username", "")
        self.password = portal_config.get("password", "")
        self.region = portal_config.get("region", "")
        self.criteria = portal_config.get("criteria", "")
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def start_browser(self):
        """Startet den Playwright Browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=HEADLESS_MODE)
        context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.page = await context.new_page()
        print(f"[{self.name}] Browser gestartet")
    
    async def close_browser(self):
        """Schließt den Browser"""
        if self.browser:
            await self.browser.close()
            print(f"[{self.name}] Browser geschlossen")
    
    async def wait(self, seconds: float = None):
        """Wartet zwischen Requests (Rate Limiting)"""
        await asyncio.sleep(seconds or CRAWL_DELAY_SECONDS)
    
    def generate_tender_id(self, source_url: str) -> str:
        """Generiert eine eindeutige ID basierend auf der URL"""
        hash_object = hashlib.md5(source_url.encode())
        return f"t-{hash_object.hexdigest()[:8]}"
    
    def create_tender_dict(
        self,
        title: str,
        authority: str,
        location: str,
        deadline: str,
        description: str,
        source_url: str,
        budget: str = None,
        category: str = None
    ) -> Dict[str, Any]:
        """Erstellt ein standardisiertes Tender-Dictionary"""
        return {
            "id": self.generate_tender_id(source_url),
            "title": title.strip(),
            "authority": authority.strip(),
            "location": location.strip() or self.region,
            "deadline": deadline,
            "budget": budget,
            "category": category or self.criteria,
            "description": description.strip(),
            "source_url": source_url,
            "source_portal": self.name,
            "crawled_at": datetime.utcnow().isoformat(),
        }
    
    @abstractmethod
    async def login(self) -> bool:
        """
        Führt den Login auf dem Portal durch.
        Muss von jeder Portal-Implementierung überschrieben werden.
        Returns: True wenn Login erfolgreich, sonst False
        """
        pass
    
    @abstractmethod
    async def scrape_tender_list(self) -> List[str]:
        """
        Scrapt die Liste aller Ausschreibungs-URLs.
        Returns: Liste von URLs zu einzelnen Ausschreibungen
        """
        pass
    
    @abstractmethod
    async def scrape_tender_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrapt die Details einer einzelnen Ausschreibung.
        Returns: Tender-Dictionary oder None bei Fehler
        """
        pass
    
    async def run(self) -> List[Dict[str, Any]]:
        """
        Hauptmethode: Führt den kompletten Crawl-Vorgang durch.
        Returns: Liste aller gefundenen Tenders
        """
        tenders = []
        
        try:
            await self.start_browser()
            
            # Login
            print(f"[{self.name}] Starte Login...")
            if not await self.login():
                print(f"[{self.name}] Login fehlgeschlagen!")
                return tenders
            print(f"[{self.name}] Login erfolgreich!")
            
            # Tender-Liste holen
            print(f"[{self.name}] Hole Ausschreibungsliste...")
            tender_urls = await self.scrape_tender_list()
            print(f"[{self.name}] {len(tender_urls)} Ausschreibungen gefunden")
            
            # Jede Ausschreibung scrapen
            for i, url in enumerate(tender_urls, 1):
                print(f"[{self.name}] Scrape {i}/{len(tender_urls)}: {url[:50]}...")
                try:
                    tender = await self.scrape_tender_detail(url)
                    if tender:
                        tenders.append(tender)
                    await self.wait()
                except Exception as e:
                    print(f"[{self.name}] Fehler bei {url}: {e}")
                    continue
            
            print(f"[{self.name}] Fertig! {len(tenders)} Ausschreibungen gescrapt")
            
        except Exception as e:
            print(f"[{self.name}] Kritischer Fehler: {e}")
        finally:
            await self.close_browser()
        
        return tenders

