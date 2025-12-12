"""
Erweiterte Crawler - holen Erstellungsdatum und vollstaendige Beschreibungen
"""
import asyncio
import re
import hashlib
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from crawlers.categorizer import categorize_tender


def extract_city_from_text(text: str) -> str:
    """Extrahiert Stadtname aus Text"""
    # Bekannte Staedte in DACH-Region
    cities = [
        # Oesterreich
        "Wien", "Graz", "Linz", "Salzburg", "Innsbruck", "Klagenfurt", "Villach", 
        "Wels", "St. Poelten", "Dornbirn", "Wiener Neustadt", "Steyr", "Feldkirch",
        "Bregenz", "Leonding", "Klosterneuburg", "Baden", "Wolfsberg", "Leoben",
        # Deutschland
        "Berlin", "Hamburg", "Muenchen", "Koeln", "Frankfurt", "Stuttgart", "Duesseldorf",
        "Leipzig", "Dortmund", "Essen", "Bremen", "Dresden", "Hannover", "Nuernberg",
        "Duisburg", "Bochum", "Wuppertal", "Bielefeld", "Bonn", "Muenster", "Karlsruhe",
        "Mannheim", "Augsburg", "Wiesbaden", "Moenchengladbach", "Gelsenkirchen", "Aachen",
        "Braunschweig", "Chemnitz", "Kiel", "Krefeld", "Halle", "Magdeburg", "Freiburg",
        "Oberhausen", "Luebeck", "Erfurt", "Mainz", "Rostock", "Kassel", "Hagen",
        "Saarbruecken", "Hamm", "Potsdam", "Ludwigshafen", "Oldenburg", "Leverkusen",
        "Osnabrueck", "Solingen", "Heidelberg", "Herne", "Neuss", "Darmstadt", "Paderborn",
        "Regensburg", "Ingolstadt", "Wuerzburg", "Wolfsburg", "Fuerth", "Ulm", "Heilbronn",
        "Offenbach", "Goettingen", "Bottrop", "Pforzheim", "Recklinghausen", "Reutlingen",
        "Koblenz", "Remscheid", "Bergisch Gladbach", "Bremerhaven", "Jena", "Trier",
        "Erlangen", "Moers", "Siegen", "Hildesheim", "Salzgitter", "Cottbus", "Kaiserslautern",
        # Schweiz
        "Zuerich", "Genf", "Basel", "Bern", "Lausanne", "Winterthur", "Luzern", "St. Gallen",
        # Mit Umlauten
        "München", "Köln", "Düsseldorf", "Nürnberg", "Würzburg", "Zürich", "Pölten"
    ]
    
    text_lower = text.lower()
    for city in cities:
        if city.lower() in text_lower:
            return city
    
    # Versuche PLZ + Ort zu finden (z.B. "79618 Rheinfelden" oder "5020 Salzburg")
    plz_match = re.search(r'(\d{4,5})\s+([A-Z][a-zäöüß]+(?:\s+[A-Z][a-zäöüß]+)?)', text)
    if plz_match:
        return plz_match.group(2)
    
    return ""


async def fetch_detail_page(page, url: str) -> dict:
    """Holt Details von einer Ausschreibungs-Detailseite"""
    details = {"description": "", "authority": "", "location": "", "deadline": "", "published_at": "", "budget": ""}
    
    try:
        await page.goto(url, timeout=20000)
        await asyncio.sleep(1)
        
        # Hole den gesamten Text fuer Ortsextraktion
        body = await page.query_selector("body")
        full_text = ""
        if body:
            full_text = await body.text_content() or ""
        
        # Extrahiere Stadt aus dem Text
        city = extract_city_from_text(full_text)
        if city:
            details["location"] = city
        
        # Versuche verschiedene Selektoren fuer Beschreibung
        description_selectors = [
            ".description", ".content", ".detail-text", ".ausschreibung-text",
            "article", ".tender-description", "#description", ".main-content",
            "p", ".text-content"
        ]
        
        for selector in description_selectors:
            try:
                elem = await page.query_selector(selector)
                if elem:
                    text = await elem.text_content()
                    if text and len(text) > 50:
                        details["description"] = " ".join(text.split())[:2000]
                        break
            except:
                continue
        
        # Falls keine Beschreibung gefunden, nutze den Body-Text
        if not details["description"] and full_text:
            clean = " ".join(full_text.split())
            details["description"] = clean[:2000]
        
    except Exception as e:
        pass
    
    return details


async def crawl_ausschreibung_at() -> list:
    """Crawlt ausschreibung.at mit erweiterten Details"""
    print("  Crawle ausschreibung.at (mit Details)...")
    tenders = []
    
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page()
    
    try:
        await page.goto("https://www.ausschreibung.at", timeout=30000)
        await asyncio.sleep(2)
        
        # Finde alle Ausschreibungs-Links
        links = await page.query_selector_all('a[href*="/Ausschreibung/"]')
        found_urls = []
        
        for link in links[:15]:
            try:
                href = await link.get_attribute("href") or ""
                text = (await link.text_content() or "").strip()
                
                match = re.search(r'/Ausschreibung/(\d+)', href)
                if match and text and len(text) > 10:
                    tender_id = match.group(1)
                    full_url = f"https://www.ausschreibung.at{href}" if href.startswith("/") else href
                    
                    # Extrahiere Veroeffentlichungsdatum
                    date_match = re.search(r'vom (\d{2}\.\d{2}\.\d{4})', text)
                    published_at = ""
                    deadline = ""
                    
                    if date_match:
                        try:
                            dt = datetime.strptime(date_match.group(1), "%d.%m.%Y")
                            published_at = dt.strftime("%Y-%m-%d")
                            deadline = (dt + timedelta(days=21)).strftime("%Y-%m-%d")
                        except:
                            published_at = datetime.now().strftime("%Y-%m-%d")
                            deadline = (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d")
                    else:
                        published_at = datetime.now().strftime("%Y-%m-%d")
                        deadline = (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d")
                    
                    title = re.sub(r'\s*vom \d{2}\.\d{2}\.\d{4}', '', text).strip()
                    
                    found_urls.append({
                        "id": f"at_{tender_id}",
                        "title": title[:200],
                        "url": full_url,
                        "published_at": published_at,
                        "deadline": deadline
                    })
            except:
                continue
        
        # Hole Details fuer jede Ausschreibung
        for item in found_urls[:10]:  # Limitiere auf 10 fuer Performance
            try:
                details = await fetch_detail_page(page, item["url"])
                
                # Extrahiere Stadt aus Titel oder Details
                city = details.get("location") or extract_city_from_text(item["title"])
                location = f"{city}, Oesterreich" if city else "Oesterreich"
                
                description = details.get("description") or f"Ausschreibung: {item['title']}"
                tenders.append({
                    "id": item["id"],
                    "title": item["title"],
                    "authority": details.get("authority") or "Vergabestelle Oesterreich",
                    "location": location,
                    "deadline": item["deadline"],
                    "published_at": item["published_at"],
                    "budget": details.get("budget"),
                    "category": categorize_tender(item["title"], description),
                    "description": description,
                    "source_url": item["url"],
                    "source_portal": "ausschreibung.at"
                })
            except:
                # Fallback - versuche Stadt aus Titel
                city = extract_city_from_text(item["title"])
                location = f"{city}, Oesterreich" if city else "Oesterreich"
                
                fallback_desc = f"Ausschreibung von ausschreibung.at: {item['title']}"
                tenders.append({
                    "id": item["id"],
                    "title": item["title"],
                    "authority": "Vergabestelle Oesterreich",
                    "location": location,
                    "deadline": item["deadline"],
                    "published_at": item["published_at"],
                    "budget": None,
                    "category": categorize_tender(item["title"], fallback_desc),
                    "description": fallback_desc,
                    "source_url": item["url"],
                    "source_portal": "ausschreibung.at"
                })
        
        print(f"    -> {len(tenders)} Ausschreibungen mit Details")
        
    except Exception as e:
        print(f"    Fehler: {e}")
    finally:
        await browser.close()
        await pw.stop()
    
    return tenders


async def crawl_tender24() -> list:
    """Crawlt tender24.de mit erweiterten Details"""
    print("  Crawle tender24.de (mit Details)...")
    tenders = []
    
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page()
    
    try:
        await page.goto("https://www.tender24.de", timeout=30000)
        await asyncio.sleep(2)
        
        rows = await page.query_selector_all("table tr")
        found_items = []
        
        for row in rows[1:15]:
            try:
                cells = await row.query_selector_all("td")
                if len(cells) >= 3:
                    date_text = (await cells[0].text_content() or "").strip()
                    title_text = (await cells[1].text_content() or "").strip()
                    authority_text = (await cells[2].text_content() or "").strip()
                    
                    # Weitere Spalten
                    procedure = ""
                    if len(cells) > 3:
                        procedure = (await cells[3].text_content() or "").strip()
                    
                    deadline_text = ""
                    if len(cells) > 5:
                        deadline_text = (await cells[5].text_content() or "").strip()
                    
                    link_elem = await cells[1].query_selector("a")
                    url = "https://www.tender24.de"
                    if link_elem:
                        href = await link_elem.get_attribute("href") or ""
                        url = f"https://www.tender24.de{href}" if href.startswith("/") else href
                    
                    if title_text and len(title_text) > 5:
                        tender_id = hashlib.md5(f"{title_text}{date_text}".encode()).hexdigest()[:12]
                        
                        # Parse Datum
                        published_at = ""
                        deadline = ""
                        try:
                            dt = datetime.strptime(date_text, "%d.%m.%Y")
                            published_at = dt.strftime("%Y-%m-%d")
                        except:
                            published_at = datetime.now().strftime("%Y-%m-%d")
                        
                        # Parse Deadline
                        try:
                            if deadline_text:
                                dl = datetime.strptime(deadline_text, "%d.%m.%Y")
                                deadline = dl.strftime("%Y-%m-%d")
                            else:
                                deadline = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
                        except:
                            deadline = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
                        
                        found_items.append({
                            "id": f"t24_{tender_id}",
                            "title": title_text[:200],
                            "authority": authority_text[:150] if authority_text else "Diverse Vergabestellen",
                            "url": url,
                            "published_at": published_at,
                            "deadline": deadline,
                            "procedure": procedure
                        })
            except:
                continue
        
        # Hole Details fuer einige Ausschreibungen
        for item in found_items[:8]:
            try:
                description = f"Ausschreibung: {item['title']}. Vergabestelle: {item['authority']}."
                if item.get("procedure"):
                    description += f" Verfahrensart: {item['procedure']}."
                
                # Extrahiere Stadt aus Titel und Authority
                city = extract_city_from_text(item["title"]) or extract_city_from_text(item["authority"])
                location = f"{city}, Deutschland" if city else "Deutschland"
                
                # Versuche Detail-Seite zu laden
                if item["url"] != "https://www.tender24.de":
                    try:
                        details = await fetch_detail_page(page, item["url"])
                        if details.get("description"):
                            description = details["description"]
                        if details.get("location") and not city:
                            city = details["location"]
                            location = f"{city}, Deutschland"
                    except:
                        pass
                
                tenders.append({
                    "id": item["id"],
                    "title": item["title"],
                    "authority": item["authority"],
                    "location": location,
                    "deadline": item["deadline"],
                    "published_at": item["published_at"],
                    "budget": None,
                    "category": categorize_tender(item["title"], description),
                    "description": description,
                    "source_url": item["url"],
                    "source_portal": "tender24.de"
                })
            except:
                continue
        
        print(f"    -> {len(tenders)} Ausschreibungen mit Details")
        
    except Exception as e:
        print(f"    Fehler: {e}")
    finally:
        await browser.close()
        await pw.stop()
    
    return tenders


async def crawl_staatsanzeiger() -> list:
    """Crawlt staatsanzeiger-eservices.de mit erweiterten Details"""
    print("  Crawle staatsanzeiger-eservices.de (mit Details)...")
    tenders = []
    
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page()
    
    try:
        await page.goto("https://www.staatsanzeiger-eservices.de/sol-b.html", timeout=30000)
        await asyncio.sleep(2)
        
        links = await page.query_selector_all("a")
        found_items = []
        
        for link in links[:40]:
            try:
                href = await link.get_attribute("href") or ""
                text = (await link.text_content() or "").strip()
                
                if text and len(text) > 20 and any(x in text.lower() for x in ['ausschreibung', 'vergabe', 'bauauftrag', 'leistung', 'lieferung']):
                    tender_id = hashlib.md5(text.encode()).hexdigest()[:12]
                    full_url = f"https://www.staatsanzeiger-eservices.de/{href}" if href.startswith("/") or not href.startswith("http") else href
                    
                    if text not in [t.get("title") for t in found_items]:
                        found_items.append({
                            "id": f"sta_{tender_id}",
                            "title": text[:200],
                            "url": full_url,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
            except:
                continue
        
        for item in found_items[:10]:
            # Extrahiere Stadt aus Titel
            city = extract_city_from_text(item["title"])
            location = f"{city}, Baden-Wuerttemberg" if city else "Baden-Wuerttemberg, Deutschland"
            
            staatsanzeiger_desc = f"Ausschreibung vom Staatsanzeiger Baden-Wuerttemberg: {item['title']}"
            tenders.append({
                "id": item["id"],
                "title": item["title"],
                "authority": "Staatsanzeiger Baden-Wuerttemberg",
                "location": location,
                "deadline": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
                "published_at": item["published_at"],
                "budget": None,
                "category": categorize_tender(item["title"], staatsanzeiger_desc),
                "description": staatsanzeiger_desc,
                "source_url": item["url"],
                "source_portal": "staatsanzeiger-eservices.de"
            })
        
        print(f"    -> {len(tenders)} Ausschreibungen gefunden")
        
    except Exception as e:
        print(f"    Fehler: {e}")
    finally:
        await browser.close()
        await pw.stop()
    
    return tenders


async def crawl_deutsche_evergabe() -> list:
    """Crawlt deutsche-evergabe.de"""
    print("  Crawle deutsche-evergabe.de...")
    tenders = []
    
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page()
    
    try:
        await page.goto("https://www.deutsche-evergabe.de", timeout=30000)
        await asyncio.sleep(2)
        
        links = await page.query_selector_all("a")
        
        for link in links[:40]:
            try:
                href = await link.get_attribute("href") or ""
                text = (await link.text_content() or "").strip()
                
                if text and len(text) > 15 and any(x in text.lower() or x in href.lower() for x in ['ausschreibung', 'vergabe', 'projekt', 'auftrag']):
                    tender_id = hashlib.md5(text.encode()).hexdigest()[:12]
                    full_url = f"https://www.deutsche-evergabe.de{href}" if href.startswith("/") else href
                    
                    # Extrahiere Stadt
                    city = extract_city_from_text(text)
                    location = f"{city}, Deutschland" if city else "Deutschland"
                    
                    if text not in [t["title"] for t in tenders]:
                        devergabe_desc = f"Ausschreibung von Deutsche eVergabe: {text}"
                        tenders.append({
                            "id": f"dev_{tender_id}",
                            "title": text[:200],
                            "authority": "Deutsche eVergabe",
                            "location": location,
                            "deadline": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
                            "published_at": datetime.now().strftime("%Y-%m-%d"),
                            "budget": None,
                            "category": categorize_tender(text[:200], devergabe_desc),
                            "description": devergabe_desc,
                            "source_url": full_url if full_url.startswith("http") else "https://www.deutsche-evergabe.de",
                            "source_portal": "deutsche-evergabe.de"
                        })
            except:
                continue
        
        print(f"    -> {len(tenders)} Ausschreibungen gefunden")
        
    except Exception as e:
        print(f"    Fehler: {e}")
    finally:
        await browser.close()
        await pw.stop()
    
    return tenders


async def crawl_rib_meinauftrag() -> list:
    """Crawlt meinauftrag.rib.de"""
    print("  Crawle meinauftrag.rib.de...")
    tenders = []
    
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page()
    
    try:
        await page.goto("https://meinauftrag.rib.de/public/publications", timeout=30000)
        await asyncio.sleep(3)
        
        rows = await page.query_selector_all("table tr, .publication-item, .card, article")
        
        for row in rows[:20]:
            try:
                text = (await row.text_content() or "").strip()
                if text and len(text) > 30 and len(text) < 1000:
                    id_match = re.search(r'(\d+[A-Z]{2,}[-]?[A-Z0-9]+)', text)
                    tender_id = id_match.group(1) if id_match else hashlib.md5(text.encode()).hexdigest()[:12]
                    
                    clean_text = " ".join(text.split())
                    title_parts = clean_text.split()
                    title = " ".join(title_parts[:15])[:200]
                    
                    link_elem = await row.query_selector("a")
                    url = "https://meinauftrag.rib.de/public/publications"
                    if link_elem:
                        href = await link_elem.get_attribute("href") or ""
                        if href:
                            url = f"https://meinauftrag.rib.de{href}" if href.startswith("/") else href
                    
                    # Extrahiere Stadt
                    city = extract_city_from_text(clean_text)
                    location = f"{city}, Deutschland" if city else "Deutschland"
                    
                    rib_desc = clean_text[:1000]
                    tenders.append({
                        "id": f"rib_{tender_id}",
                        "title": title,
                        "authority": "RIB Vergabeplattform",
                        "location": location,
                        "deadline": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
                        "published_at": datetime.now().strftime("%Y-%m-%d"),
                        "budget": None,
                        "category": categorize_tender(title, rib_desc),
                        "description": rib_desc,
                        "source_url": url,
                        "source_portal": "meinauftrag.rib.de"
                    })
            except:
                continue
        
        print(f"    -> {len(tenders)} Ausschreibungen gefunden")
        
    except Exception as e:
        print(f"    Fehler: {e}")
    finally:
        await browser.close()
        await pw.stop()
    
    return tenders


def load_custom_portals() -> list:
    """Laedt benutzerdefinierte Portale aus settings.json"""
    import os
    import json
    
    settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")
    
    try:
        if os.path.exists(settings_file):
            with open(settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
                return settings.get("customPortals", [])
    except:
        pass
    
    return []


async def crawl_all_working_portals() -> list:
    """Crawlt ALLE konfigurierten Portale inkl. benutzerdefinierter Portale"""
    from crawlers.generic_crawler import crawl_custom_portal
    
    all_tenders = []
    
    # Lade benutzerdefinierte Portale
    custom_portals = load_custom_portals()
    total_portals = 5 + len(custom_portals)
    
    print("\n" + "="*60)
    print(f"Starte Crawling von {total_portals} Portalen...")
    print(f"  - 5 Standard-Portale")
    print(f"  - {len(custom_portals)} benutzerdefinierte Portale")
    print("="*60)
    
    portal_num = 1
    
    # Standard-Portale
    print(f"\n[{portal_num}/{total_portals}] Ausschreibung.at")
    tenders = await crawl_ausschreibung_at()
    all_tenders.extend(tenders)
    portal_num += 1
    
    print(f"\n[{portal_num}/{total_portals}] Staatsanzeiger")
    tenders = await crawl_staatsanzeiger()
    all_tenders.extend(tenders)
    portal_num += 1
    
    print(f"\n[{portal_num}/{total_portals}] Deutsche eVergabe")
    tenders = await crawl_deutsche_evergabe()
    all_tenders.extend(tenders)
    portal_num += 1
    
    print(f"\n[{portal_num}/{total_portals}] RIB Meinauftrag")
    tenders = await crawl_rib_meinauftrag()
    all_tenders.extend(tenders)
    portal_num += 1
    
    print(f"\n[{portal_num}/{total_portals}] Tender24")
    tenders = await crawl_tender24()
    all_tenders.extend(tenders)
    portal_num += 1
    
    # Benutzerdefinierte Portale
    for cp in custom_portals:
        if cp.get("enabled", True):
            print(f"\n[{portal_num}/{total_portals}] {cp.get('name', 'Benutzerdefiniert')} (benutzerdefiniert)")
            try:
                tenders = await crawl_custom_portal(cp)
                all_tenders.extend(tenders)
            except Exception as e:
                print(f"    Fehler: {e}")
            portal_num += 1
    
    print("\n" + "="*60)
    print(f"CRAWLING ABGESCHLOSSEN: {len(all_tenders)} Ausschreibungen")
    print("="*60)
    
    return all_tenders


if __name__ == "__main__":
    tenders = asyncio.run(crawl_all_working_portals())
    print("\n--- TOP 10 Ausschreibungen ---")
    for t in tenders[:10]:
        print(f"  [{t['source_portal']}] {t['title'][:50]}...")
        print(f"    Veroeffentlicht: {t.get('published_at', 'N/A')}")
        print(f"    Beschreibung: {t['description'][:100]}...")
