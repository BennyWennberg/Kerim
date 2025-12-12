"""
Einmaliges manuelles Ausführen des Crawlers

Ausführen mit: cd backend && python run_now.py
"""
import asyncio
import os
import sys

# Pfad konfigurieren
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from crawlers.run_all import run_all_crawlers


if __name__ == "__main__":
    print("Starte Crawler manuell...")
    asyncio.run(run_all_crawlers())

