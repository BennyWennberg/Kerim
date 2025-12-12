"""
Test-Script: Besucht alle Portale und extrahiert echte Ausschreibungen
"""
import asyncio
import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from playwright.async_api import async_playwright
from config import PORTALS


async def test_portal(name: str, url: str, username: str, password: str):
    """Testet ein Portal und extrahiert Ausschreibungen"""
    print(f"\n{'='*60}")
    print(f"TESTE: {name}")
    print(f"   URL: {url}")
    print(f"{'='*60}")
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    
    tenders_found = []
    
    try:
        # 1. Hauptseite besuchen
        print(f"\n1. Öffne {url}...")
        await page.goto(url, timeout=30000)
        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(2)
        
        # 2. Suche nach öffentlichen Ausschreibungen (ohne Login)
        print("2. Suche nach öffentlichen Ausschreibungen...")
        
        # Verschiedene URLs probieren
        public_urls = [
            f"{url}/ausschreibungen",
            f"{url}/tenders",
            f"{url}/public",
            f"{url}/vergabe",
            f"{url}/public/informations",
            f"{url}/suche",
            url  # Hauptseite als Fallback
        ]
        
        for test_url in public_urls:
            try:
                await page.goto(test_url, timeout=15000)
                await page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(1)
                
                # Suche nach Ausschreibungs-Links
                content = await page.content()
                if any(x in content.lower() for x in ['ausschreibung', 'vergabe', 'tender', 'auftrag', 'leistung']):
                    print(f"   ✓ Gefunden bei: {test_url}")
                    break
            except:
                continue
        
        # 3. Extrahiere alle möglichen Ausschreibungs-Elemente
        print("3. Extrahiere Ausschreibungen...")
        
        # Verschiedene Selektoren probieren
        selectors = [
            'table tr',
            '.tender-item, .tender-row',
            '.ausschreibung, .vergabe',
            'article, .card, .item',
            '.result, .search-result',
            'a[href*="ausschreibung"], a[href*="tender"], a[href*="vergabe"]',
        ]
        
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                if len(elements) > 2:  # Mindestens 3 Elemente
                    print(f"   Gefunden mit Selektor: {selector} ({len(elements)} Elemente)")
                    
                    for i, elem in enumerate(elements[:5]):  # Max 5
                        try:
                            text = await elem.text_content()
                            if text and len(text.strip()) > 20:
                                # Bereinige Text
                                text = ' '.join(text.split())[:200]
                                if text not in [t['title'] for t in tenders_found]:
                                    tenders_found.append({
                                        'title': text,
                                        'source': name
                                    })
                        except:
                            pass
                    
                    if tenders_found:
                        break
            except:
                continue
        
        # 4. Falls Login verfügbar, versuche einzuloggen
        if username and password and len(tenders_found) < 5:
            print("4. Versuche Login...")
            
            login_urls = ['/login', '/anmelden', '/signin', '/auth/login', '/user/login']
            
            for login_path in login_urls:
                try:
                    await page.goto(f"{url}{login_path}", timeout=10000)
                    await asyncio.sleep(1)
                    
                    # Suche Input-Felder
                    inputs = await page.query_selector_all('input')
                    username_field = None
                    password_field = None
                    
                    for inp in inputs:
                        input_type = await inp.get_attribute("type") or "text"
                        input_name = (await inp.get_attribute("name") or "").lower()
                        
                        if input_type == "password":
                            password_field = inp
                        elif input_type in ["text", "email"] and any(x in input_name for x in ["user", "email", "login", "name"]):
                            username_field = inp
                        elif input_type == "text" and not username_field:
                            username_field = inp
                    
                    if username_field and password_field:
                        print(f"   Login-Formular gefunden bei {login_path}")
                        await username_field.fill(username)
                        await password_field.fill(password)
                        await page.keyboard.press("Enter")
                        await asyncio.sleep(3)
                        
                        # Prüfe ob Login erfolgreich
                        new_content = await page.content()
                        if any(x in new_content.lower() for x in ['logout', 'abmelden', 'willkommen', 'dashboard']):
                            print("   ✓ Login erfolgreich!")
                        break
                except Exception as e:
                    continue
        
        # 5. Ergebnisse ausgeben
        print(f"\nGEFUNDENE AUSSCHREIBUNGEN ({len(tenders_found)}):")
        if tenders_found:
            for i, tender in enumerate(tenders_found[:5], 1):
                print(f"   {i}. {tender['title'][:100]}...")
        else:
            print("   ❌ Keine Ausschreibungen gefunden")
            print("   → CSS-Selektoren müssen manuell angepasst werden")
        
    except Exception as e:
        print(f"   ❌ FEHLER: {e}")
    finally:
        await browser.close()
        await playwright.stop()
    
    return tenders_found


async def main():
    print("="*60)
    print("TenderScout AI - Portal-Test")
    print("="*60)
    print("\nTeste alle konfigurierten Portale...")
    
    all_results = {}
    
    for portal_key, config in PORTALS.items():
        name = config.get("name", portal_key)
        url = config.get("url", "")
        username = config.get("username", "")
        password = config.get("password", "")
        
        results = await test_portal(name, url, username, password)
        all_results[name] = results
    
    # Zusammenfassung
    print("\n" + "="*60)
    print("ZUSAMMENFASSUNG")
    print("="*60)
    
    total = 0
    for portal, tenders in all_results.items():
        count = len(tenders)
        total += count
        status = "✓" if count > 0 else "✗"
        print(f"   {status} {portal}: {count} Ausschreibungen")
    
    print(f"\n   GESAMT: {total} Ausschreibungen gefunden")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

