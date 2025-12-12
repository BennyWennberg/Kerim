"""
Detaillierte Analyse eines einzelnen Portals
"""
import asyncio
import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from playwright.async_api import async_playwright


async def analyze_ausschreibung_at():
    """Analysiert ausschreibung.at im Detail"""
    print("="*60)
    print("Analysiere: ausschreibung.at")
    print("="*60)
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    
    try:
        # Die echte Ausschreibungsseite finden
        url = "https://www.ausschreibung.at"
        await page.goto(url)
        await asyncio.sleep(2)
        
        # Alle Links auf der Seite finden
        print("\nAlle Links mit 'ausschreib' oder 'vergabe':")
        links = await page.query_selector_all("a")
        for link in links:
            href = await link.get_attribute("href") or ""
            text = await link.text_content() or ""
            if any(x in href.lower() or x in text.lower() for x in ["ausschreib", "vergabe", "tender", "suche"]):
                print(f"  - {text.strip()[:40]} -> {href[:60]}")
        
    finally:
        await browser.close()
        await playwright.stop()


async def analyze_staatsanzeiger():
    """Analysiert staatsanzeiger-eservices.de"""
    print("\n" + "="*60)
    print("Analysiere: staatsanzeiger-eservices.de")
    print("="*60)
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    
    try:
        url = "https://www.staatsanzeiger-eservices.de"
        await page.goto(url)
        await asyncio.sleep(2)
        
        print("\nSeiten-Titel:", await page.title())
        
        # Alle Links finden
        print("\nWichtige Links:")
        links = await page.query_selector_all("a")
        for link in links:
            href = await link.get_attribute("href") or ""
            text = await link.text_content() or ""
            if any(x in href.lower() or x in text.lower() for x in ["ausschreib", "vergabe", "tender", "suche", "login"]):
                print(f"  - {text.strip()[:40]} -> {href[:60]}")
        
    finally:
        await browser.close()
        await playwright.stop()


async def analyze_rib():
    """Analysiert meinauftrag.rib.de - hat oeffentliche Ausschreibungen"""
    print("\n" + "="*60)
    print("Analysiere: meinauftrag.rib.de (RIB)")
    print("="*60)
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    
    try:
        # RIB hat eine oeffentliche Seite
        url = "https://meinauftrag.rib.de/public/informations"
        print(f"\nOeffne: {url}")
        await page.goto(url)
        await asyncio.sleep(3)
        
        print("Seiten-Titel:", await page.title())
        
        # Suche nach Tabellen oder Listen
        tables = await page.query_selector_all("table")
        print(f"\nTabellen gefunden: {len(tables)}")
        
        # Suche nach Ausschreibungs-Links
        links = await page.query_selector_all("a")
        tender_links = []
        for link in links:
            href = await link.get_attribute("href") or ""
            text = await link.text_content() or ""
            if "/public/" in href and len(text.strip()) > 10:
                tender_links.append((text.strip()[:60], href))
        
        print(f"\nMoegliche Ausschreibungen ({len(tender_links)}):")
        for text, href in tender_links[:10]:
            print(f"  - {text}")
        
    finally:
        await browser.close()
        await playwright.stop()


async def main():
    await analyze_ausschreibung_at()
    await analyze_staatsanzeiger()
    await analyze_rib()


if __name__ == "__main__":
    asyncio.run(main())

