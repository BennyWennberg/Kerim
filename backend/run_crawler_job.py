
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
