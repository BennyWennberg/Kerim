import asyncio
import re
from playwright.async_api import async_playwright

async def test_ausschreibung_at():
    print("="*60)
    print("1. AUSSCHREIBUNG.AT (Oesterreich)")
    print("="*60)
    
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page()
    
    await page.goto("https://www.ausschreibung.at")
    await asyncio.sleep(2)
    
    links = await page.query_selector_all('a[href*="/Ausschreibung/"]')
    print(f"Gefundene Links: {len(links)}")
    
    tenders = []
    for link in links[:10]:
        href = await link.get_attribute("href") or ""
        text = (await link.text_content() or "").strip()
        match = re.search(r"/Ausschreibung/\d+", href)
        if match and text and len(text) > 10:
            tenders.append({"title": text[:80], "url": href})
    
    print(f"\nEchte Ausschreibungen ({len(tenders)}):")
    for i, t in enumerate(tenders[:5], 1):
        print(f"  {i}. {t['title']}")
    
    await browser.close()
    await pw.stop()
    return tenders

async def test_tender24():
    print("\n" + "="*60)
    print("2. TENDER24.DE (Deutschland)")
    print("="*60)
    
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page()
    
    await page.goto("https://www.tender24.de")
    await asyncio.sleep(2)
    
    rows = await page.query_selector_all("table tr")
    print(f"Gefundene Zeilen: {len(rows)}")
    
    tenders = []
    for row in rows[1:7]:
        cells = await row.query_selector_all("td")
        if len(cells) >= 2:
            date = (await cells[0].text_content() or "").strip()
            title = (await cells[1].text_content() or "").strip()
            if title and len(title) > 5:
                tenders.append({"title": f"{date} - {title[:60]}", "url": ""})
    
    print(f"\nEchte Ausschreibungen ({len(tenders)}):")
    for i, t in enumerate(tenders[:5], 1):
        print(f"  {i}. {t['title']}")
    
    await browser.close()
    await pw.stop()
    return tenders

async def test_staatsanzeiger():
    print("\n" + "="*60)
    print("3. STAATSANZEIGER-ESERVICES.DE")
    print("="*60)
    
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page()
    
    await page.goto("https://www.staatsanzeiger-eservices.de/sol-b.html")
    await asyncio.sleep(2)
    
    title = await page.title()
    print(f"Seiten-Titel: {title}")
    
    # Suche nach Inhalten
    elements = await page.query_selector_all("table tr, .list-item, article, div.result")
    print(f"Gefundene Elemente: {len(elements)}")
    
    tenders = []
    for elem in elements[:10]:
        text = (await elem.text_content() or "").strip()
        if text and len(text) > 30 and len(text) < 500:
            clean = " ".join(text.split())[:100]
            if clean not in [t["title"] for t in tenders]:
                tenders.append({"title": clean, "url": ""})
    
    print(f"\nGefundene Elemente ({len(tenders)}):")
    for i, t in enumerate(tenders[:5], 1):
        print(f"  {i}. {t['title'][:70]}...")
    
    await browser.close()
    await pw.stop()
    return tenders

async def test_deutsche_evergabe():
    print("\n" + "="*60)
    print("4. DEUTSCHE-EVERGABE.DE")
    print("="*60)
    
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page()
    
    await page.goto("https://www.deutsche-evergabe.de")
    await asyncio.sleep(2)
    
    title = await page.title()
    print(f"Seiten-Titel: {title}")
    
    # Diese Seite ist eine Vergabe-Plattform, probiere verschiedene URLs
    content = await page.content()
    if "ausschreibung" in content.lower():
        print("Ausschreibungs-Inhalte gefunden")
    
    # Suche nach Links
    links = await page.query_selector_all("a")
    vergabe_links = []
    for link in links:
        href = await link.get_attribute("href") or ""
        text = (await link.text_content() or "").strip()
        if "vergabe" in href.lower() or "ausschreibung" in href.lower():
            if text and len(text) > 5:
                vergabe_links.append(text[:60])
    
    print(f"\nVergabe-Links ({len(vergabe_links)}):")
    for i, t in enumerate(vergabe_links[:5], 1):
        print(f"  {i}. {t}")
    
    await browser.close()
    await pw.stop()
    return vergabe_links

async def test_rib():
    print("\n" + "="*60)
    print("5. RIB MEINAUFTRAG.DE")
    print("="*60)
    
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page()
    
    await page.goto("https://meinauftrag.rib.de/public/publications")
    await asyncio.sleep(3)
    
    title = await page.title()
    print(f"Seiten-Titel: {title}")
    
    # Diese Seite koennte Login erfordern
    content = await page.content()
    if "login" in content.lower() or len(content) < 5000:
        print("Vermutlich Login erforderlich")
    
    elements = await page.query_selector_all("table tr, .item, article, .card")
    print(f"Gefundene Elemente: {len(elements)}")
    
    tenders = []
    for elem in elements[:10]:
        text = (await elem.text_content() or "").strip()
        if text and len(text) > 20:
            tenders.append(text[:80])
    
    print(f"\nGefundene Inhalte ({len(tenders)}):")
    for i, t in enumerate(tenders[:5], 1):
        print(f"  {i}. {t[:70]}...")
    
    await browser.close()
    await pw.stop()
    return tenders

async def main():
    print("TENDERSCOUT - ECHTZEIT TEST ALLER PORTALE")
    print("="*60)
    
    r1 = await test_ausschreibung_at()
    r2 = await test_tender24()
    r3 = await test_staatsanzeiger()
    r4 = await test_deutsche_evergabe()
    r5 = await test_rib()
    
    print("\n" + "="*60)
    print("ZUSAMMENFASSUNG")
    print("="*60)
    print(f"  Ausschreibung.at: {len(r1)} Ausschreibungen")
    print(f"  Tender24.de: {len(r2)} Ausschreibungen")
    print(f"  Staatsanzeiger: {len(r3)} Elemente")
    print(f"  Deutsche-eVergabe: {len(r4)} Links")
    print(f"  RIB Meinauftrag: {len(r5)} Inhalte")

if __name__ == "__main__":
    asyncio.run(main())

