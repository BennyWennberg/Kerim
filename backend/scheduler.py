"""
Scheduler für automatisches Crawling (2x täglich)

Ausführen mit: python scheduler.py

Der Scheduler läuft kontinuierlich und startet den Crawler:
- Morgens um 06:00 Uhr
- Abends um 18:00 Uhr
"""
import schedule
import time
import asyncio
import os
import sys
from datetime import datetime

# Pfad konfigurieren
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


def run_crawler():
    """Startet den Crawler synchron"""
    print(f"\n{'='*60}")
    print(f"⏰ Scheduler startet Crawling um {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        from crawlers.run_all import run_all_crawlers
        
        # Neuen Event-Loop erstellen
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_all_crawlers())
        finally:
            loop.close()
            
        print(f"\n✅ Crawling erfolgreich abgeschlossen um {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ Fehler beim Crawling: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Hauptfunktion - startet den Scheduler"""
    print("="*60)
    print("🚀 TenderScout AI - Scheduler gestartet")
    print("="*60)
    print()
    print("Geplante Crawl-Zeiten:")
    print("  - 06:00 Uhr (morgens)")
    print("  - 18:00 Uhr (abends)")
    print()
    print("Drücke Ctrl+C zum Beenden")
    print("="*60)
    print()
    
    # Jobs planen
    schedule.every().day.at("06:00").do(run_crawler)
    schedule.every().day.at("18:00").do(run_crawler)
    
    # Optional: Beim Start einmal ausführen
    # run_crawler()
    
    # Scheduler-Loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Jede Minute prüfen


if __name__ == "__main__":
    main()

