from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio

from database import get_db, Tender, TenderStatus, init_db
from config import PORTALS

# FastAPI App
app = FastAPI(
    title="TenderScout AI API",
    description="API für Ausschreibungsverwaltung",
    version="1.0.0"
)

# CORS für Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Alle Origins erlauben für Entwicklung
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models
class AIAnalysis(BaseModel):
    summary: Optional[str] = None
    relevanceScore: Optional[int] = None
    keyRisks: Optional[List[str]] = None
    recommendation: Optional[str] = None


class TenderResponse(BaseModel):
    id: str
    title: str
    authority: str
    location: str
    deadline: str
    budget: Optional[str] = None
    category: str
    description: str
    status: str
    sourceUrl: str
    sourcePortal: str
    crawledAt: str
    aiAnalysis: Optional[AIAnalysis] = None

    class Config:
        from_attributes = True


class TenderStatusUpdate(BaseModel):
    status: str


class AIAnalysisUpdate(BaseModel):
    summary: str
    relevanceScore: int
    keyRisks: List[str]
    recommendation: str


class StatsResponse(BaseModel):
    total: int
    new: int
    interesting: int
    applied: int
    rejected: int
    deadlineSoon: int


class CrawlResponse(BaseModel):
    message: str
    status: str


# Startup Event
@app.on_event("startup")
def startup():
    init_db()


# Helper Functions
def tender_to_response(tender: Tender) -> dict:
    """Konvertiert DB Tender zu Response Format"""
    ai_analysis = None
    if tender.ai_summary:
        key_risks = []
        if tender.ai_key_risks:
            try:
                key_risks = json.loads(tender.ai_key_risks)
            except:
                key_risks = []
        
        ai_analysis = {
            "summary": tender.ai_summary,
            "relevanceScore": tender.ai_relevance_score,
            "keyRisks": key_risks,
            "recommendation": tender.ai_recommendation
        }
    
    return {
        "id": tender.id,
        "title": tender.title,
        "authority": tender.authority,
        "location": tender.location,
        "deadline": tender.deadline,
        "publishedAt": tender.published_at if hasattr(tender, 'published_at') else None,
        "budget": tender.budget,
        "category": tender.category,
        "description": tender.description,
        "status": tender.status.value,
        "sourceUrl": tender.source_url,
        "sourcePortal": tender.source_portal,
        "crawledAt": tender.crawled_at.isoformat() if tender.crawled_at else "",
        "aiAnalysis": ai_analysis
    }


# API Endpoints

@app.get("/api/tenders", response_model=List[dict])
def get_tenders(
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in title and authority"),
    db: Session = Depends(get_db)
):
    """Alle Ausschreibungen abrufen"""
    query = db.query(Tender)
    
    # Status Filter
    if status and status != "ALL":
        try:
            status_enum = TenderStatus(status)
            query = query.filter(Tender.status == status_enum)
        except ValueError:
            pass
    
    # Suche
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Tender.title.ilike(search_term)) | 
            (Tender.authority.ilike(search_term))
        )
    
    # Neueste zuerst
    tenders = query.order_by(Tender.crawled_at.desc()).all()
    
    return [tender_to_response(t) for t in tenders]


@app.get("/api/tenders/{tender_id}", response_model=dict)
def get_tender(tender_id: str, db: Session = Depends(get_db)):
    """Einzelne Ausschreibung abrufen"""
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender nicht gefunden")
    return tender_to_response(tender)


@app.put("/api/tenders/{tender_id}/status")
def update_tender_status(
    tender_id: str, 
    update: TenderStatusUpdate,
    db: Session = Depends(get_db)
):
    """Status einer Ausschreibung ändern"""
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender nicht gefunden")
    
    try:
        tender.status = TenderStatus(update.status)
        db.commit()
        return {"message": "Status aktualisiert", "status": update.status}
    except ValueError:
        raise HTTPException(status_code=400, detail="Ungültiger Status")


@app.put("/api/tenders/{tender_id}/analysis")
def update_tender_analysis(
    tender_id: str,
    analysis: AIAnalysisUpdate,
    db: Session = Depends(get_db)
):
    """AI-Analyse für Ausschreibung speichern"""
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender nicht gefunden")
    
    tender.ai_summary = analysis.summary
    tender.ai_relevance_score = analysis.relevanceScore
    tender.ai_key_risks = json.dumps(analysis.keyRisks)
    tender.ai_recommendation = analysis.recommendation
    
    db.commit()
    return {"message": "Analyse gespeichert"}


@app.get("/api/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Dashboard-Statistiken"""
    from datetime import datetime, timedelta
    
    total = db.query(Tender).count()
    new = db.query(Tender).filter(Tender.status == TenderStatus.NEW).count()
    interesting = db.query(Tender).filter(Tender.status == TenderStatus.INTERESTING).count()
    applied = db.query(Tender).filter(Tender.status == TenderStatus.APPLIED).count()
    rejected = db.query(Tender).filter(Tender.status == TenderStatus.REJECTED).count()
    
    # Deadlines in den nächsten 14 Tagen
    # Da deadline als String gespeichert ist, machen wir eine einfache Zählung
    deadline_soon = 0  # TODO: Implementieren wenn Datumsformat bekannt
    
    return StatsResponse(
        total=total,
        new=new,
        interesting=interesting,
        applied=applied,
        rejected=rejected,
        deadlineSoon=deadline_soon
    )


@app.get("/api/portals")
def get_portals():
    """Liste aller konfigurierten Portale"""
    saved_settings = load_settings()
    saved_portals = {p["id"]: p for p in saved_settings.get("portals", [])}
    custom_portals = saved_settings.get("customPortals", [])
    
    # Standard-Portale
    result = [
        {
            "id": key,
            "name": config["name"],
            "url": config["url"],
            "region": saved_portals.get(key, {}).get("region", config["region"]),
            "criteria": saved_portals.get(key, {}).get("criteria", config["criteria"]),
            "enabled": saved_portals.get(key, {}).get("enabled", True),
            "isCustom": False,
        }
        for key, config in PORTALS.items()
    ]
    
    # Benutzerdefinierte Portale hinzufuegen
    for cp in custom_portals:
        result.append({
            "id": cp["id"],
            "name": cp["name"],
            "url": cp["url"],
            "region": cp.get("region", ""),
            "criteria": cp.get("criteria", ""),
            "enabled": cp.get("enabled", True),
            "isCustom": True,
        })
    
    return result


class NewPortalRequest(BaseModel):
    name: str
    url: str
    region: str = ""
    criteria: str = ""
    username: str = ""
    password: str = ""
    usernameSelector: str = ""
    passwordSelector: str = ""
    loginButtonSelector: str = ""
    tenderListSelector: str = ""


@app.post("/api/portals")
def add_portal(portal: NewPortalRequest):
    """Neues benutzerdefiniertes Portal hinzufuegen"""
    import uuid
    
    settings = load_settings()
    custom_portals = settings.get("customPortals", [])
    
    # Generiere eindeutige ID
    portal_id = f"custom_{uuid.uuid4().hex[:8]}"
    
    new_portal = {
        "id": portal_id,
        "name": portal.name,
        "url": portal.url,
        "region": portal.region,
        "criteria": portal.criteria,
        "username": portal.username,
        "password": portal.password,
        "enabled": True,
        "selectors": {
            "username": portal.usernameSelector,
            "password": portal.passwordSelector,
            "loginButton": portal.loginButtonSelector,
            "tenderList": portal.tenderListSelector,
        }
    }
    
    custom_portals.append(new_portal)
    settings["customPortals"] = custom_portals
    save_settings_to_file(settings)
    
    return {
        "id": portal_id,
        "name": portal.name,
        "url": portal.url,
        "region": portal.region,
        "criteria": portal.criteria,
        "isCustom": True,
    }


@app.delete("/api/portals/{portal_id}")
def delete_portal(portal_id: str):
    """Benutzerdefiniertes Portal loeschen"""
    settings = load_settings()
    custom_portals = settings.get("customPortals", [])
    
    # Nur benutzerdefinierte Portale koennen geloescht werden
    if not portal_id.startswith("custom_"):
        raise HTTPException(status_code=400, detail="Standard-Portale koennen nicht geloescht werden")
    
    # Portal entfernen
    settings["customPortals"] = [p for p in custom_portals if p["id"] != portal_id]
    save_settings_to_file(settings)
    
    return {"message": "Portal geloescht"}


# Settings Speicherung
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

def load_settings() -> dict:
    """Lädt gespeicherte Einstellungen"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {}


def save_settings_to_file(settings: dict):
    """Speichert Einstellungen in Datei"""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


class PortalSettingsModel(BaseModel):
    id: str
    region: str
    criteria: str
    enabled: bool = True


class SettingsModel(BaseModel):
    globalKeywords: str = ""
    minBudget: str = "50000"
    excludeKeywords: str = ""
    portals: List[PortalSettingsModel] = []


@app.get("/api/settings")
def get_settings():
    """Crawler-Einstellungen abrufen"""
    return load_settings()


@app.post("/api/settings")
def update_settings(settings: SettingsModel):
    """Crawler-Einstellungen speichern"""
    settings_dict = settings.dict()
    save_settings_to_file(settings_dict)
    return {"message": "Einstellungen gespeichert"}


# Crawler im Hintergrund ausfuehren
CRAWL_STATUS_FILE = os.path.join(os.path.dirname(__file__), "crawl_status.json")

def get_crawl_status():
    """Liest Crawler-Status aus Datei"""
    try:
        if os.path.exists(CRAWL_STATUS_FILE):
            with open(CRAWL_STATUS_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return {"running": False, "last_run": None, "results": None}

def set_crawl_status(status: dict):
    """Speichert Crawler-Status in Datei"""
    with open(CRAWL_STATUS_FILE, "w") as f:
        json.dump(status, f)

def run_crawl_sync():
    """Fuehrt Crawler synchron in einem Thread aus"""
    status = {"running": True, "last_run": None, "results": "Crawler laeuft..."}
    set_crawl_status(status)
    
    try:
        import asyncio
        import sys
        
        # Stelle sicher dass der Pfad korrekt ist
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        from crawlers.working_crawlers import crawl_all_working_portals
        from crawlers.run_all import save_tenders_to_db
        
        # Neuen Event-Loop fuer diesen Thread erstellen
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(crawl_all_working_portals())
            
            # Speichere in DB
            if results:
                new_tenders = save_tenders_to_db(results)
                status["results"] = f"{len(results)} gefunden, {len(new_tenders)} neu"
            else:
                status["results"] = "Keine Ausschreibungen gefunden"
        finally:
            loop.close()
    except Exception as e:
        status["results"] = f"Fehler: {str(e)}"
        import traceback
        traceback.print_exc()
    finally:
        from datetime import datetime
        status["running"] = False
        status["last_run"] = datetime.now().isoformat()
        set_crawl_status(status)


@app.post("/api/crawl")
async def start_crawl_endpoint(background_tasks: BackgroundTasks):
    """Startet den Crawler manuell"""
    import subprocess
    import sys
    
    status = get_crawl_status()
    
    if status.get("running", False):
        return {"message": "Crawler laeuft bereits", "status": "running"}
    
    # Setze Status auf running
    set_crawl_status({"running": True, "last_run": None, "results": "Crawler gestartet..."})
    
    # Starte Crawler als separaten Prozess
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    crawler_script = os.path.join(backend_dir, "run_crawler_job.py")
    
    # Erstelle ein einfaches Script das den Crawler ausfuehrt
    script_content = '''
import asyncio
import sys
import os
import json

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from crawlers.working_crawlers import crawl_all_working_portals
from crawlers.run_all import save_tenders_to_db
from datetime import datetime

status_file = os.path.join(backend_dir, "crawl_status.json")

try:
    results = asyncio.run(crawl_all_working_portals())
    if results:
        new_tenders = save_tenders_to_db(results)
        status = {"running": False, "last_run": datetime.now().isoformat(), "results": f"{len(results)} gefunden, {len(new_tenders)} neu"}
    else:
        status = {"running": False, "last_run": datetime.now().isoformat(), "results": "Keine Ausschreibungen gefunden"}
except Exception as e:
    status = {"running": False, "last_run": datetime.now().isoformat(), "results": f"Fehler: {str(e)}"}

with open(status_file, "w") as f:
    json.dump(status, f)
'''
    
    with open(crawler_script, "w") as f:
        f.write(script_content)
    
    # Starte den Prozess im Hintergrund
    subprocess.Popen([sys.executable, crawler_script], 
                     cwd=backend_dir,
                     creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
    
    return {"message": "Crawler gestartet - durchsucht alle 6 Portale", "status": "started"}


@app.get("/api/crawl/status")
def get_crawl_status_endpoint():
    """Status des Crawlers abrufen"""
    return get_crawl_status()


# Health Check
@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "TenderScout AI API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

