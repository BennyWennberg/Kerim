# TenderScout AI - Schnellstart

## Voraussetzungen
- Node.js (v18+)
- Python (v3.10+)
- Playwright Browser installiert

## Installation (einmalig)

```bash
# Frontend Dependencies
npm install

# Backend Dependencies
cd backend
pip install -r requirements.txt
playwright install chromium
cd ..
```

## Starten

### Alles auf einmal starten:
```bash
npm run dev
```

Dies startet:
- **Frontend** auf http://localhost:3000
- **Backend API** auf http://localhost:8000

### Einzeln starten:
```bash
# Nur Frontend
npm run frontend

# Nur Backend
npm run backend

# Crawler manuell starten
npm run crawl
```

## Verfügbare Befehle

| Befehl | Beschreibung |
|--------|-------------|
| `npm run dev` | Startet Frontend + Backend |
| `npm run frontend` | Startet nur das Frontend |
| `npm run backend` | Startet nur das Backend |
| `npm run crawl` | Führt den Crawler aus |
| `npm run build` | Erstellt Production Build |

## Konfiguration

### OpenAI API Key (.env.local)
```
OPENAI_API_KEY=sk-dein-api-key
```

### Portal Credentials (backend/.env)
```
AUSSCHREIBUNG_AT_USERNAME=...
AUSSCHREIBUNG_AT_PASSWORD=...
# etc.
```

