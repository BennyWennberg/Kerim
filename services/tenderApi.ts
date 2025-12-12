const API_BASE = "http://localhost:8000/api";

export interface AIAnalysis {
  summary: string;
  relevanceScore: number;
  keyRisks: string[];
  recommendation: "STRONG_BID" | "POSSIBLE" | "IGNORE";
}

export interface Tender {
  id: string;
  title: string;
  authority: string;
  location: string;
  deadline: string;
  publishedAt?: string;
  budget?: string;
  category: string;
  description: string;
  status: "NEW" | "INTERESTING" | "APPLIED" | "REJECTED";
  sourceUrl: string;
  sourcePortal: string;
  crawledAt: string;
  aiAnalysis?: AIAnalysis;
}

export interface Stats {
  total: number;
  new: number;
  interesting: number;
  applied: number;
  rejected: number;
  deadlineSoon: number;
}

export interface Portal {
  id: string;
  name: string;
  url: string;
  region: string;
  criteria: string;
  isCustom?: boolean;
}

export interface NewPortal {
  name: string;
  url: string;
  region: string;
  criteria: string;
  username: string;
  password: string;
  usernameSelector?: string;
  passwordSelector?: string;
  loginButtonSelector?: string;
  tenderListSelector?: string;
}

export interface CrawlStatus {
  running: boolean;
  last_run: string | null;
  results: string | null;
}

// API Funktionen

export async function fetchTenders(
  status?: string,
  search?: string
): Promise<Tender[]> {
  const params = new URLSearchParams();
  if (status && status !== "ALL") params.append("status", status);
  if (search) params.append("search", search);

  const url = `${API_BASE}/tenders${params.toString() ? "?" + params.toString() : ""}`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error("Fehler beim Laden der Ausschreibungen");
  }

  return response.json();
}

export async function fetchTender(id: string): Promise<Tender> {
  const response = await fetch(`${API_BASE}/tenders/${id}`);

  if (!response.ok) {
    throw new Error("Ausschreibung nicht gefunden");
  }

  return response.json();
}

export async function updateTenderStatus(
  id: string,
  status: string
): Promise<void> {
  const response = await fetch(`${API_BASE}/tenders/${id}/status`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });

  if (!response.ok) {
    throw new Error("Fehler beim Aktualisieren des Status");
  }
}

export async function saveTenderAnalysis(
  id: string,
  analysis: AIAnalysis
): Promise<void> {
  const response = await fetch(`${API_BASE}/tenders/${id}/analysis`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      summary: analysis.summary,
      relevanceScore: analysis.relevanceScore,
      keyRisks: analysis.keyRisks,
      recommendation: analysis.recommendation,
    }),
  });

  if (!response.ok) {
    throw new Error("Fehler beim Speichern der Analyse");
  }
}

export async function fetchStats(): Promise<Stats> {
  const response = await fetch(`${API_BASE}/stats`);

  if (!response.ok) {
    throw new Error("Fehler beim Laden der Statistiken");
  }

  return response.json();
}

export async function fetchPortals(): Promise<Portal[]> {
  const response = await fetch(`${API_BASE}/portals`);

  if (!response.ok) {
    throw new Error("Fehler beim Laden der Portale");
  }

  return response.json();
}

export async function startCrawl(): Promise<{ message: string; status: string }> {
  const response = await fetch(`${API_BASE}/crawl`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Fehler beim Starten des Crawlers");
  }

  return response.json();
}

export async function getCrawlStatus(): Promise<CrawlStatus> {
  const response = await fetch(`${API_BASE}/crawl/status`);

  if (!response.ok) {
    throw new Error("Fehler beim Abrufen des Crawler-Status");
  }

  return response.json();
}

export async function addPortal(portal: NewPortal): Promise<Portal> {
  const response = await fetch(`${API_BASE}/portals`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(portal),
  });

  if (!response.ok) {
    throw new Error("Fehler beim Hinzufuegen des Portals");
  }

  return response.json();
}

export async function deletePortal(portalId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/portals/${portalId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Fehler beim Loeschen des Portals");
  }
}

