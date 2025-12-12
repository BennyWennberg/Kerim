# TenderScout AI - Backend

## Schnellstart

### 1. Dependencies installieren
```bash
cd backend
pip install -r requirements.txt
python -m playwright install chromium
```

### 2. Konfiguration
Erstelle/bearbeite `.env` im backend-Ordner:
```env
# Portal-Credentials (bereits eingetragen)
AUSSCHREIBUNG_AT_USERNAME=...
AUSSCHREIBUNG_AT_PASSWORD=...
# ... weitere Portale

# E-Mail (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=deine-email@gmail.com
SMTP_PASSWORD=app-passwort
SENDER_EMAIL=deine-email@gmail.com
RECIPIENT_EMAIL=empfaenger@example.com
```

### 3. API starten
```bash
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### 4. Crawler manuell ausführen
```bash
python run_now.py
```

### 5. Scheduler starten (läuft 24/7)
```bash
python scheduler.py
```

## Automatisches Crawling einrichten

### Option A: Python Scheduler (einfach)
```bash
python scheduler.py
```
Läuft im Vordergrund und führt Crawler um 06:00 und 18:00 aus.

### Option B: Windows Task Scheduler (empfohlen für Produktion)

1. Öffne "Aufgabenplanung" (Task Scheduler)
2. Klicke "Aufgabe erstellen..."
3. **Allgemein:**
   - Name: "TenderScout Crawler"
   - "Unabhängig von der Benutzeranmeldung ausführen"
4. **Trigger:**
   - Täglich, 06:00 Uhr
   - Wiederholen alle 12 Stunden
5. **Aktionen:**
   - Programm: `C:\...\Python312\python.exe`
   - Argumente: `run_now.py`
   - Starten in: `C:\tenderscout-ai\backend`

## Ordnerstruktur

```
backend/
├── api.py              # FastAPI REST-Endpoints
├── database.py         # SQLite Datenbankmodell
├── config.py           # Portal-Konfiguration
├── notifier.py         # E-Mail-Benachrichtigung
├── scheduler.py        # Automatischer Scheduler
├── run_now.py          # Manueller Crawler-Start
├── requirements.txt    # Python Dependencies
├── .env                # Credentials (nicht committen!)
└── crawlers/
    ├── base.py             # Basis-Crawler-Klasse
    ├── ausschreibung_at.py # Portal-Crawler
    ├── staatsanzeiger.py
    ├── deutsche_evergabe.py
    ├── rib.py
    ├── tender24.py
    └── run_all.py          # Führt alle Crawler aus
```

## Portal-Selektoren anpassen

Die CSS-Selektoren in den Crawler-Dateien sind generisch und müssen
an die tatsächliche Struktur der Websites angepasst werden:

1. Öffne das Portal im Browser
2. Melde dich an
3. Öffne DevTools (F12)
4. Inspiziere Login-Formular, Suchergebnisse, etc.
5. Kopiere die CSS-Selektoren in die entsprechende Crawler-Datei

## E-Mail einrichten (Gmail)

1. Aktiviere 2-Faktor-Authentifizierung in Gmail
2. Erstelle ein App-Passwort: 
   https://myaccount.google.com/apppasswords
3. Trage SMTP_USER und SMTP_PASSWORD in .env ein

## API-Endpunkte

| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| /api/tenders | GET | Alle Ausschreibungen |
| /api/tenders/{id} | GET | Einzelne Ausschreibung |
| /api/tenders/{id}/status | PUT | Status ändern |
| /api/stats | GET | Dashboard-Statistiken |
| /api/portals | GET | Konfigurierte Portale |
| /api/crawl | POST | Crawler manuell starten |
| /api/crawl/status | GET | Crawler-Status |
| /docs | GET | Swagger API-Dokumentation |

