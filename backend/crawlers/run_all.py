"""
Führt alle Crawler aus und speichert die Ergebnisse in der Datenbank.
Ausführen mit: cd backend && python -m crawlers.run_all
"""
import asyncio
import os
import sys

# Füge Backend-Ordner zum Pfad hinzu
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import json

from config import PORTALS
from database import SessionLocal, Tender, TenderStatus, init_db
from crawlers.working_crawlers import crawl_all_working_portals


def load_settings() -> dict:
    """Lädt gespeicherte Einstellungen"""
    settings_file = os.path.join(backend_dir, "settings.json")
    try:
        if os.path.exists(settings_file):
            with open(settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {}


def get_portal_config(portal_key: str) -> dict:
    """Holt Portal-Config mit überschriebenen Settings"""
    base_config = PORTALS.get(portal_key, {}).copy()
    
    # Lade gespeicherte Einstellungen
    settings = load_settings()
    saved_portals = {p["id"]: p for p in settings.get("portals", [])}
    
    # Überschreibe mit gespeicherten Werten
    if portal_key in saved_portals:
        saved = saved_portals[portal_key]
        if saved.get("region"):
            base_config["region"] = saved["region"]
        if saved.get("criteria"):
            base_config["criteria"] = saved["criteria"]
        base_config["enabled"] = saved.get("enabled", True)
    else:
        base_config["enabled"] = True
    
    # Globale Keywords hinzufügen
    global_keywords = settings.get("globalKeywords", "")
    if global_keywords and base_config.get("criteria"):
        base_config["criteria"] = f"{base_config['criteria']}, {global_keywords}"
    elif global_keywords:
        base_config["criteria"] = global_keywords
    
    return base_config


def save_tenders_to_db(tenders: list) -> list:
    """
    Speichert gefundene Tenders in der Datenbank.
    Gibt Liste der NEUEN Tenders zurueck (fuer Benachrichtigung).
    
    WICHTIG: Nur Ausschreibungen die in DIESEM Crawl-Durchlauf
    neu hinzugefuegt werden, bekommen Status "NEW".
    Bisherige "NEW" Ausschreibungen werden zu "INTERESTING" geaendert.
    """
    db = SessionLocal()
    new_count = 0
    updated_count = 0
    new_tenders = []  # Fuer E-Mail-Benachrichtigung
    
    try:
        # SCHRITT 1: Alle bisherigen "NEW" Ausschreibungen auf "INTERESTING" setzen
        # Damit sind nur die Ausschreibungen aus dem aktuellen Scan "NEW"
        old_new_count = db.query(Tender).filter(Tender.status == TenderStatus.NEW).update(
            {Tender.status: TenderStatus.INTERESTING}
        )
        if old_new_count > 0:
            print(f"  {old_new_count} bisherige 'NEW' Ausschreibungen -> 'INTERESTING'")
        
        # SCHRITT 2: Neue Ausschreibungen speichern
        for tender_data in tenders:
            # Pruefen ob Tender schon existiert
            existing = db.query(Tender).filter(Tender.id == tender_data["id"]).first()
            
            if existing:
                # Update existierenden Tender (ausser Status - der bleibt!)
                existing.title = tender_data["title"]
                existing.description = tender_data["description"]
                existing.deadline = tender_data["deadline"]
                existing.budget = tender_data.get("budget")
                existing.published_at = tender_data.get("published_at")
                existing.location = tender_data.get("location", existing.location)
                updated_count += 1
            else:
                # Neuen Tender erstellen - NUR DIESE bekommen "NEW"
                new_tender = Tender(
                    id=tender_data["id"],
                    title=tender_data["title"],
                    authority=tender_data["authority"],
                    location=tender_data["location"],
                    deadline=tender_data["deadline"],
                    published_at=tender_data.get("published_at"),
                    budget=tender_data.get("budget"),
                    category=tender_data["category"],
                    description=tender_data["description"],
                    status=TenderStatus.NEW,
                    source_url=tender_data["source_url"],
                    source_portal=tender_data["source_portal"],
                )
                db.add(new_tender)
                new_count += 1
                new_tenders.append(tender_data)  # Fuer Benachrichtigung merken
        
        db.commit()
        print(f"Datenbank aktualisiert: {new_count} neue, {updated_count} aktualisierte Tenders")
        
    except Exception as e:
        print(f"Datenbankfehler: {e}")
        db.rollback()
    finally:
        db.close()
    
    return new_tenders


async def run_single_crawler(portal_key: str):
    """Führt einen einzelnen Crawler aus"""
    if portal_key not in PORTALS:
        print(f"Portal '{portal_key}' nicht gefunden!")
        return []
    
    if portal_key not in CRAWLER_CLASSES:
        print(f"Kein Crawler für '{portal_key}' implementiert!")
        return []
    
    # Hole Config mit überschriebenen Settings
    config = get_portal_config(portal_key)
    
    # Prüfe ob Portal aktiviert ist
    if not config.get("enabled", True):
        print(f"\n[{config['name']}] Portal deaktiviert - überspringe")
        return []
    
    crawler_class = CRAWLER_CLASSES[portal_key]
    
    print(f"\n{'='*50}")
    print(f"Starte Crawler: {config['name']}")
    print(f"  Region: {config.get('region', 'Alle')}")
    print(f"  Kriterien: {config.get('criteria', 'Keine')}")
    print(f"{'='*50}")
    
    crawler = crawler_class(config)
    tenders = await crawler.run()
    
    return tenders


async def run_all_crawlers():
    """Fuehrt alle funktionierenden Crawler aus"""
    print("="*60)
    print("TenderScout AI - Crawler gestartet")
    print("="*60)
    
    # Datenbank initialisieren
    init_db()
    
    # Nutze die funktionierenden Crawler
    all_tenders = await crawl_all_working_portals()
    
    # Alle Tenders speichern und neue zurueckbekommen
    new_tenders = []
    if all_tenders:
        new_tenders = save_tenders_to_db(all_tenders)
    
    # E-Mail-Benachrichtigung senden wenn neue Tenders gefunden
    if new_tenders:
        try:
            from notifier import send_notification
            print(f"\nSende E-Mail-Benachrichtigung fuer {len(new_tenders)} neue Ausschreibungen...")
            send_notification(new_tenders)
        except Exception as e:
            print(f"E-Mail-Versand fehlgeschlagen: {e}")
    
    print("\n" + "="*60)
    print(f"Crawling abgeschlossen!")
    print(f"  - Gesamt gefunden: {len(all_tenders)}")
    print(f"  - Davon NEU: {len(new_tenders)}")
    print("="*60)
    
    return all_tenders


if __name__ == "__main__":
    asyncio.run(run_all_crawlers())

