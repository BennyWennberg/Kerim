import os
from dotenv import load_dotenv

load_dotenv()

# Portal-Konfigurationen
PORTALS = {
    "ausschreibung_at": {
        "name": "Ausschreibung.at",
        "url": "https://www.ausschreibung.at",
        "region": "Tirol",
        "criteria": "Tiefbau",
        "username": os.getenv("AUSSCHREIBUNG_AT_USERNAME"),
        "password": os.getenv("AUSSCHREIBUNG_AT_PASSWORD"),
    },
    "staatsanzeiger_1": {
        "name": "Staatsanzeiger (Account 1)",
        "url": "https://www.staatsanzeiger-eservices.de",
        "region": "Salzburg",
        "criteria": "Leitungsbau",
        "username": os.getenv("STAATSANZEIGER_1_USERNAME"),
        "password": os.getenv("STAATSANZEIGER_1_PASSWORD"),
    },
    "staatsanzeiger_2": {
        "name": "Staatsanzeiger (Account 2)",
        "url": "https://www.staatsanzeiger-eservices.de",
        "region": "Salzburg",
        "criteria": "Leitungsbau",
        "username": os.getenv("STAATSANZEIGER_2_USERNAME"),
        "password": os.getenv("STAATSANZEIGER_2_PASSWORD"),
    },
    "deutsche_evergabe": {
        "name": "Deutsche eVergabe",
        "url": "https://www.deutsche-evergabe.de",
        "region": "Vorarlberg",
        "criteria": "Aushubarbeiten",
        "username": os.getenv("DEUTSCHE_EVERGABE_USERNAME"),
        "password": os.getenv("DEUTSCHE_EVERGABE_PASSWORD"),
    },
    "rib": {
        "name": "RIB Meinauftrag",
        "url": "https://meinauftrag.rib.de",
        "region": "Bayern",
        "criteria": "Erdarbeiten",
        "username": os.getenv("RIB_USERNAME"),
        "password": os.getenv("RIB_PASSWORD"),
    },
    "tender24": {
        "name": "Tender24",
        "url": "https://www.tender24.de",
        "region": "Baden-Württemberg",
        "criteria": "Straßenbau",
        "username": os.getenv("TENDER24_USERNAME"),
        "password": os.getenv("TENDER24_PASSWORD"),
    },
}

# Datenbank
DATABASE_URL = "sqlite:///./tenders.db"

# Crawler Einstellungen
CRAWL_DELAY_SECONDS = 2  # Wartezeit zwischen Requests
HEADLESS_MODE = True  # Browser ohne GUI

