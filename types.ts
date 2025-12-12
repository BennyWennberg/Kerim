// Diese Datei wird nicht mehr benötigt - Types sind jetzt in services/tenderApi.ts definiert
// Behalten für Rückwärtskompatibilität

export enum TenderStatus {
  NEW = 'NEW',
  INTERESTING = 'INTERESTING',
  APPLIED = 'APPLIED',
  REJECTED = 'REJECTED'
}

export interface AIAnalysis {
  summary: string;
  relevanceScore: number;
  keyRisks: string[];
  recommendation: 'STRONG_BID' | 'POSSIBLE' | 'IGNORE';
}

export interface Tender {
  id: string;
  title: string;
  authority: string;
  location: string;
  deadline: string;
  publishedAt?: string;  // Veroeffentlichungsdatum
  budget?: string;
  category: string;
  description: string;
  status: TenderStatus;
  sourceUrl: string;
  sourcePortal?: string;
  crawledAt: string;
  aiAnalysis?: AIAnalysis;
}

export interface Stats {
  totalFound: number;
  newToday: number;
  deadlinesSoon: number;
  appliedCount: number;
}
