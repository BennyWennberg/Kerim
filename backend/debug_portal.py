"""
Debug-Script zum Analysieren der Portal-Strukturen
Speichert Screenshots und HTML für jeden Login-Bereich
"""
import asyncio
import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from playwright.async_api import async_playwright
from config import PORTALS


async def analyze_portal(portal_key: str, portal_config: dict):
    """Analysiert ein Portal und speichert Debug-Infos"""
    name = portal_config.get("name", portal_key)
    url = portal_config.get("url", "")
    
    print(f"\n{'='*60}")
    print(f"Analysiere: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    # Debug-Ordner erstellen
    debug_dir = os.path.join(backend_dir, "debug_output")
    os.makedirs(debug_dir, exist_ok=True)
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)  # SICHTBAR!
    page = await browser.new_page()
    
    try:
        # Hauptseite besuchen
        print(f"1. Öffne Hauptseite: {url}")
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)
        
        # Screenshot Hauptseite
        screenshot_path = os.path.join(debug_dir, f"{portal_key}_main.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"   Screenshot: {screenshot_path}")
        
        # HTML speichern
        html_path = os.path.join(debug_dir, f"{portal_key}_main.html")
        html = await page.content()
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"   HTML: {html_path}")
        
        # Login-Seite suchen
        login_urls = ["/login", "/anmelden", "/signin", "/auth/login"]
        login_found = False
        
        for login_path in login_urls:
            try:
                login_url = f"{url}{login_path}"
                print(f"2. Versuche Login-URL: {login_url}")
                await page.goto(login_url)
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(2)
                
                # Prüfen ob Login-Formular vorhanden
                page_content = await page.content()
                if "password" in page_content.lower() or "passwort" in page_content.lower():
                    login_found = True
                    
                    # Screenshot Login
                    screenshot_path = os.path.join(debug_dir, f"{portal_key}_login.png")
                    await page.screenshot(path=screenshot_path, full_page=True)
                    print(f"   Login gefunden! Screenshot: {screenshot_path}")
                    
                    # HTML speichern
                    html_path = os.path.join(debug_dir, f"{portal_key}_login.html")
                    with open(html_path, "w", encoding="utf-8") as f:
                        f.write(page_content)
                    print(f"   HTML: {html_path}")
                    
                    # Input-Felder analysieren
                    print(f"\n   Gefundene Input-Felder:")
                    inputs = await page.query_selector_all("input")
                    for inp in inputs:
                        input_type = await inp.get_attribute("type") or "text"
                        input_name = await inp.get_attribute("name") or ""
                        input_id = await inp.get_attribute("id") or ""
                        input_class = await inp.get_attribute("class") or ""
                        print(f"   - type='{input_type}' name='{input_name}' id='{input_id}' class='{input_class[:50]}'")
                    
                    # Submit-Buttons analysieren
                    print(f"\n   Gefundene Buttons:")
                    buttons = await page.query_selector_all("button, input[type='submit']")
                    for btn in buttons:
                        btn_type = await btn.get_attribute("type") or ""
                        btn_text = await btn.text_content() or ""
                        btn_class = await btn.get_attribute("class") or ""
                        print(f"   - type='{btn_type}' text='{btn_text.strip()[:30]}' class='{btn_class[:50]}'")
                    
                    break
            except Exception as e:
                print(f"   Fehler bei {login_path}: {e}")
                continue
        
        if not login_found:
            print("   WARNUNG: Kein Login-Formular gefunden!")
            # Suche nach Login-Link auf der Hauptseite
            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            
            login_links = await page.query_selector_all("a")
            print("\n   Mögliche Login-Links auf Hauptseite:")
            for link in login_links:
                href = await link.get_attribute("href") or ""
                text = await link.text_content() or ""
                if any(x in href.lower() or x in text.lower() for x in ["login", "anmeld", "sign", "auth"]):
                    print(f"   - '{text.strip()[:30]}' -> {href}")
        
    except Exception as e:
        print(f"   FEHLER: {e}")
    finally:
        await browser.close()
        await playwright.stop()


async def main():
    print("="*60)
    print("TenderScout AI - Portal Debug Analyse")
    print("="*60)
    print("\nDieser Script öffnet sichtbare Browser-Fenster,")
    print("um die Login-Seiten der Portale zu analysieren.")
    print()
    
    # Nur ein Portal analysieren zum Test
    portal_key = "ausschreibung_at"
    if portal_key in PORTALS:
        await analyze_portal(portal_key, PORTALS[portal_key])
    
    print("\n" + "="*60)
    print("Analyse abgeschlossen!")
    print(f"Debug-Dateien in: {os.path.join(backend_dir, 'debug_output')}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

