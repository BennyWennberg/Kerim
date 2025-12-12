import React, { useState } from 'react';
import { Search, ExternalLink, Calendar, MapPin, BrainCircuit, X, Bookmark, Loader2, AlertTriangle, Building2, RefreshCw, Clock, Tag, Globe, FileText, ChevronRight } from 'lucide-react';
import { Tender, updateTenderStatus, saveTenderAnalysis } from '../services/tenderApi';
import { analyzeTender } from '../services/openaiService';

interface TenderListProps {
  tenders: Tender[];
  setTenders: React.Dispatch<React.SetStateAction<Tender[]>>;
  loading?: boolean;
  onRefresh?: () => void;
}

// Detail Modal Komponente
const TenderDetailModal: React.FC<{
  tender: Tender;
  onClose: () => void;
  onStatusChange: (status: string) => void;
  onAnalyze: () => void;
  analyzing: boolean;
}> = ({ tender, onClose, onStatusChange, onAnalyze, analyzing }) => {
  const [descriptionExpanded, setDescriptionExpanded] = React.useState(false);
  const [apiKeyMissing, setApiKeyMissing] = React.useState(false);

  const handleAnalyzeClick = () => {
    if (!process.env.API_KEY) {
      setApiKeyMissing(true);
      return;
    }
    onAnalyze();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div 
        className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-6">
          <div className="flex justify-between items-start">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                  tender.status === 'NEW' ? 'bg-white/20 text-white' :
                  tender.status === 'INTERESTING' ? 'bg-emerald-400 text-emerald-900' :
                  tender.status === 'APPLIED' ? 'bg-purple-400 text-purple-900' :
                  'bg-slate-400 text-slate-900'
                }`}>
                  {tender.status}
                </span>
                <span className="text-white/70 text-sm">{tender.sourcePortal}</span>
              </div>
              <h2 className="text-2xl font-bold mb-1">{tender.title}</h2>
              <p className="text-white/80 text-sm">ID: {tender.id}</p>
            </div>
            <button 
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-full transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {/* Info Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-slate-50 rounded-lg p-4">
              <div className="flex items-center gap-2 text-slate-500 text-sm mb-1">
                <Building2 className="w-4 h-4" />
                Auftraggeber
              </div>
              <p className="font-semibold text-slate-900">{tender.authority}</p>
            </div>
            <div className="bg-slate-50 rounded-lg p-4">
              <div className="flex items-center gap-2 text-slate-500 text-sm mb-1">
                <MapPin className="w-4 h-4" />
                Standort
              </div>
              <p className="font-semibold text-slate-900">{tender.location}</p>
            </div>
            <div className="bg-slate-50 rounded-lg p-4">
              <div className="flex items-center gap-2 text-slate-500 text-sm mb-1">
                <Tag className="w-4 h-4" />
                Kategorie
              </div>
              <p className="font-semibold text-slate-900">{tender.category}</p>
            </div>
          </div>

          {/* Datum-Infos */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-emerald-50 rounded-lg p-4">
              <div className="flex items-center gap-2 text-emerald-600 text-sm mb-1">
                <Calendar className="w-4 h-4" />
                Ausstellungsdatum
              </div>
              <p className="font-semibold text-emerald-700">
                {tender.publishedAt ? new Date(tender.publishedAt).toLocaleDateString('de-DE') : 'Nicht angegeben'}
              </p>
            </div>
            <div className="bg-orange-50 rounded-lg p-4">
              <div className="flex items-center gap-2 text-orange-600 text-sm mb-1">
                <Clock className="w-4 h-4" />
                Abgabefrist
              </div>
              <p className="font-semibold text-orange-700">
                {new Date(tender.deadline).toLocaleDateString('de-DE')}
              </p>
            </div>
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center gap-2 text-blue-600 text-sm mb-1">
                <Globe className="w-4 h-4" />
                Gefunden am
              </div>
              <p className="font-semibold text-blue-700">
                {tender.crawledAt ? new Date(tender.crawledAt).toLocaleDateString('de-DE', {
                  day: '2-digit',
                  month: '2-digit', 
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                }) : 'Nicht angegeben'}
              </p>
            </div>
          </div>

          {/* Budget */}
          {tender.budget && (
            <div className="bg-emerald-50 rounded-lg p-4 mb-6">
              <div className="flex items-center gap-2 text-emerald-600 text-sm mb-1">
                <FileText className="w-4 h-4" />
                Budget
              </div>
              <p className="font-bold text-2xl text-emerald-700">{tender.budget}</p>
            </div>
          )}

          {/* Description - Collapsible */}
          <div className="mb-6">
            <button 
              onClick={() => setDescriptionExpanded(!descriptionExpanded)}
              className="w-full flex items-center justify-between font-semibold text-slate-900 mb-2 hover:text-blue-600 transition-colors"
            >
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-slate-400" />
                Beschreibung
              </div>
              <ChevronRight className={`w-5 h-5 transition-transform ${descriptionExpanded ? 'rotate-90' : ''}`} />
            </button>
            <div className={`bg-slate-50 rounded-lg overflow-hidden transition-all duration-300 ${
              descriptionExpanded ? 'max-h-[500px] p-4' : 'max-h-24 p-4'
            }`}>
              <p className="text-slate-600 leading-relaxed whitespace-pre-wrap">
                {tender.description}
              </p>
            </div>
            {!descriptionExpanded && tender.description.length > 200 && (
              <button 
                onClick={() => setDescriptionExpanded(true)}
                className="mt-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Mehr anzeigen...
              </button>
            )}
          </div>

          {/* Crawled Info */}
          <div className="flex items-center gap-4 text-sm text-slate-500 mb-6">
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              Gecrawlt: {tender.crawledAt ? new Date(tender.crawledAt).toLocaleString('de-DE') : 'Unbekannt'}
            </div>
            <div className="flex items-center gap-1">
              <Globe className="w-4 h-4" />
              Quelle: {tender.sourcePortal}
            </div>
          </div>

          {/* AI Analysis */}
          {tender.aiAnalysis && tender.aiAnalysis.relevanceScore > 0 ? (
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-6 border border-indigo-100">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <BrainCircuit className="w-6 h-6 text-indigo-600" />
                  <span className="font-bold text-lg text-slate-900">KI-Analyse</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-slate-500">Relevanz:</span>
                  <div className="w-32 h-3 bg-slate-200 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${tender.aiAnalysis.relevanceScore > 75 ? 'bg-emerald-500' : tender.aiAnalysis.relevanceScore > 40 ? 'bg-yellow-500' : 'bg-red-500'}`} 
                      style={{ width: `${tender.aiAnalysis.relevanceScore}%` }}
                    ></div>
                  </div>
                  <span className="text-lg font-bold text-slate-700">{tender.aiAnalysis.relevanceScore}%</span>
                </div>
              </div>
              
              <p className="text-slate-700 mb-4 italic border-l-4 border-indigo-300 pl-4">
                "{tender.aiAnalysis.summary}"
              </p>
              
              <div className="flex flex-wrap gap-2">
                {tender.aiAnalysis.keyRisks.map((risk, idx) => (
                  <span key={idx} className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-red-100 text-red-700 text-sm border border-red-200">
                    <AlertTriangle className="w-4 h-4" />
                    {risk}
                  </span>
                ))}
                <span className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-sm border font-semibold ${
                  tender.aiAnalysis.recommendation === 'STRONG_BID' ? 'bg-emerald-100 text-emerald-700 border-emerald-200' :
                  tender.aiAnalysis.recommendation === 'IGNORE' ? 'bg-slate-200 text-slate-600 border-slate-300' :
                  'bg-yellow-100 text-yellow-700 border-yellow-200'
                }`}>
                  Empfehlung: {tender.aiAnalysis.recommendation.replace('_', ' ')}
                </span>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {apiKeyMissing && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                  <p className="font-semibold mb-1">API Key fehlt!</p>
                  <p className="text-sm">Bitte erstelle eine Datei <code className="bg-red-100 px-1 rounded">.env.local</code> im Projektordner mit:</p>
                  <code className="block mt-2 bg-red-100 p-2 rounded text-xs">OPENAI_API_KEY=sk-dein-api-key-hier</code>
                  <p className="text-sm mt-2">Danach Frontend neu starten mit: <code className="bg-red-100 px-1 rounded">npm run dev</code></p>
                </div>
              )}
              <button 
                onClick={handleAnalyzeClick}
                disabled={analyzing}
                className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white rounded-lg font-semibold transition-all disabled:opacity-50"
              >
                {analyzing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analysiere mit KI...
                  </>
                ) : (
                  <>
                    <BrainCircuit className="w-5 h-5" />
                    Mit KI analysieren
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-slate-200 p-4 bg-slate-50 flex justify-between items-center">
          <div className="flex gap-2">
            <button 
              onClick={() => onStatusChange('INTERESTING')}
              className="px-4 py-2 bg-emerald-100 hover:bg-emerald-200 text-emerald-700 rounded-lg font-medium flex items-center gap-2 transition-colors"
            >
              <Bookmark className="w-4 h-4" />
              Interessant
            </button>
            <button 
              onClick={() => onStatusChange('APPLIED')}
              className="px-4 py-2 bg-purple-100 hover:bg-purple-200 text-purple-700 rounded-lg font-medium flex items-center gap-2 transition-colors"
            >
              Beworben
            </button>
            <button 
              onClick={() => onStatusChange('REJECTED')}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg font-medium flex items-center gap-2 transition-colors"
            >
              <X className="w-4 h-4" />
              Ablehnen
            </button>
          </div>
          <a 
            href={tender.sourceUrl} 
            target="_blank" 
            rel="noreferrer"
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium flex items-center gap-2 transition-colors"
          >
            Zur Ausschreibung <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
};

export const TenderList: React.FC<TenderListProps> = ({ tenders, setTenders, loading, onRefresh }) => {
  const [filter, setFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [deadlineFilter, setDeadlineFilter] = useState<string>('ALL');
  const [portalFilter, setPortalFilter] = useState<string>('ALL');
  const [locationFilter, setLocationFilter] = useState<string>('ALL');
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const [selectedTender, setSelectedTender] = useState<Tender | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  // Extrahiere eindeutige Portale und Laender aus den Daten
  const uniquePortals = React.useMemo(() => {
    const portals = new Set(tenders.map(t => t.sourcePortal).filter(Boolean));
    return Array.from(portals).sort();
  }, [tenders]);

  const uniqueLocations = React.useMemo(() => {
    const locations = new Set(tenders.map(t => {
      // Extrahiere Land aus Location (z.B. "Stuttgart, Deutschland" -> "Deutschland")
      const parts = t.location.split(',');
      return parts[parts.length - 1]?.trim() || t.location;
    }).filter(Boolean));
    return Array.from(locations).sort();
  }, [tenders]);

  const uniqueCategories = React.useMemo(() => {
    const categories = new Set(tenders.map(t => t.category).filter(Boolean));
    return Array.from(categories).sort();
  }, [tenders]);

  const handleStatusChange = async (id: string, newStatus: string) => {
    try {
      await updateTenderStatus(id, newStatus);
      setTenders(prev => prev.map(t => t.id === id ? { ...t, status: newStatus as Tender['status'] } : t));
    } catch (e) {
      console.error('Fehler beim Status-Update:', e);
      alert('Fehler beim Aktualisieren des Status');
    }
  };

  const handleAnalyze = async (id: string, text: string) => {
    if (!process.env.API_KEY) {
      alert("Bitte OPENAI_API_KEY in .env.local setzen.");
      return;
    }
    setAnalyzingId(id);
    try {
      const analysis = await analyzeTender(text);
      
      // Analyse in DB speichern
      await saveTenderAnalysis(id, analysis);
      
      // Lokal aktualisieren
      setTenders(prev => prev.map(t => t.id === id ? { ...t, aiAnalysis: analysis } : t));
    } catch (e) {
      console.error(e);
      alert("Analyse fehlgeschlagen. Siehe Konsole.");
    } finally {
      setAnalyzingId(null);
    }
  };

  const filteredTenders = tenders.filter(t => {
    // Text-Suche
    const matchesText = t.title.toLowerCase().includes(filter.toLowerCase()) || 
                        t.authority.toLowerCase().includes(filter.toLowerCase());
    
    // Status-Filter
    const matchesStatus = statusFilter === 'ALL' || t.status === statusFilter;
    
    // Deadline-Filter
    let matchesDeadline = true;
    if (deadlineFilter !== 'ALL' && t.deadline) {
      const deadline = new Date(t.deadline);
      const now = new Date();
      const diffDays = Math.ceil((deadline.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
      
      switch (deadlineFilter) {
        case 'EXPIRED':
          matchesDeadline = diffDays < 0;
          break;
        case '1DAY':
          matchesDeadline = diffDays >= 0 && diffDays <= 1;
          break;
        case '1WEEK':
          matchesDeadline = diffDays >= 0 && diffDays <= 7;
          break;
        case '2WEEKS':
          matchesDeadline = diffDays >= 0 && diffDays <= 14;
          break;
        case '1MONTH':
          matchesDeadline = diffDays >= 0 && diffDays <= 30;
          break;
        case 'FUTURE':
          matchesDeadline = diffDays > 30;
          break;
      }
    }
    
    // Portal-Filter
    const matchesPortal = portalFilter === 'ALL' || t.sourcePortal === portalFilter;
    
    // Location-Filter
    const matchesLocation = locationFilter === 'ALL' || t.location.includes(locationFilter);
    
    // Kategorie-Filter
    const matchesCategory = categoryFilter === 'ALL' || t.category === categoryFilter;
    
    return matchesText && matchesStatus && matchesDeadline && matchesPortal && matchesLocation && matchesCategory;
  });

  // Anzahl aktiver Filter
  const activeFilterCount = [deadlineFilter, portalFilter, locationFilter, categoryFilter].filter(f => f !== 'ALL').length;

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header & Filters */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4 gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Ausschreibungen</h2>
          <p className="text-slate-500">{filteredTenders.length} von {tenders.length} Ausschreibungen</p>
        </div>
        
        <div className="flex gap-3 w-full md:w-auto">
          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={loading}
              className="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-50"
              title="Aktualisieren"
            >
              <RefreshCw className={`w-5 h-5 text-slate-600 ${loading ? 'animate-spin' : ''}`} />
            </button>
          )}
          <div className="relative flex-1 md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Suche..." 
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />
          </div>
          <select 
            className="px-4 py-2 rounded-lg border border-slate-200 bg-white text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="ALL">Alle Status</option>
            <option value="NEW">Neu</option>
            <option value="INTERESTING">Interessant</option>
            <option value="APPLIED">Beworben</option>
            <option value="REJECTED">Abgelehnt</option>
          </select>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-4 py-2 rounded-lg border flex items-center gap-2 transition-colors ${
              showFilters || activeFilterCount > 0
                ? 'bg-blue-50 border-blue-200 text-blue-700'
                : 'border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            <Tag className="w-4 h-4" />
            Filter
            {activeFilterCount > 0 && (
              <span className="bg-blue-600 text-white text-xs px-1.5 py-0.5 rounded-full">{activeFilterCount}</span>
            )}
          </button>
        </div>
      </div>

      {/* Erweiterte Filter */}
      {showFilters && (
        <div className="bg-white rounded-xl border border-slate-200 p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Ablaufdatum Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                <Clock className="w-4 h-4 inline mr-1" />
                Ablaufdatum
              </label>
              <select
                className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-white text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={deadlineFilter}
                onChange={(e) => setDeadlineFilter(e.target.value)}
              >
                <option value="ALL">Alle Fristen</option>
                <option value="EXPIRED">Abgelaufen</option>
                <option value="1DAY">Innerhalb 1 Tag</option>
                <option value="1WEEK">Innerhalb 1 Woche</option>
                <option value="2WEEKS">Innerhalb 2 Wochen</option>
                <option value="1MONTH">Innerhalb 1 Monat</option>
                <option value="FUTURE">Mehr als 1 Monat</option>
              </select>
            </div>

            {/* Portal Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                <Globe className="w-4 h-4 inline mr-1" />
                Portal/Website
              </label>
              <select
                className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-white text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={portalFilter}
                onChange={(e) => setPortalFilter(e.target.value)}
              >
                <option value="ALL">Alle Portale</option>
                {uniquePortals.map(portal => (
                  <option key={portal} value={portal}>{portal}</option>
                ))}
              </select>
            </div>

            {/* Land/Region Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                <MapPin className="w-4 h-4 inline mr-1" />
                Land/Region
              </label>
              <select
                className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-white text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={locationFilter}
                onChange={(e) => setLocationFilter(e.target.value)}
              >
                <option value="ALL">Alle Regionen</option>
                {uniqueLocations.map(loc => (
                  <option key={loc} value={loc}>{loc}</option>
                ))}
              </select>
            </div>

            {/* Kategorie Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                <Tag className="w-4 h-4 inline mr-1" />
                Kategorie/Gewerk
              </label>
              <select
                className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-white text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
              >
                <option value="ALL">Alle Kategorien</option>
                {uniqueCategories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Filter zuruecksetzen */}
          {activeFilterCount > 0 && (
            <div className="mt-4 pt-4 border-t border-slate-100">
              <button
                onClick={() => {
                  setDeadlineFilter('ALL');
                  setPortalFilter('ALL');
                  setLocationFilter('ALL');
                  setCategoryFilter('ALL');
                }}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Alle Filter zuruecksetzen
              </button>
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-500 mb-2" />
          <p className="text-slate-500">Lade Ausschreibungen...</p>
        </div>
      )}

      {/* Tender Cards */}
      {!loading && (
        <div className="space-y-4">
          {filteredTenders.length === 0 && (
            <div className="text-center py-12 bg-white rounded-xl border border-slate-200 border-dashed">
              <p className="text-slate-500">
                {tenders.length === 0 
                  ? "Keine Ausschreibungen vorhanden. Starte den Crawler um Daten zu laden."
                  : "Keine Ausschreibungen gefunden für diese Filterkriterien."
                }
              </p>
            </div>
          )}

          {filteredTenders.map((tender) => (
            <div 
              key={tender.id} 
              className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-lg hover:border-blue-300 transition-all duration-200 cursor-pointer group"
              onClick={() => setSelectedTender(tender)}
            >
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                        tender.status === 'NEW' ? 'bg-blue-100 text-blue-700' :
                        tender.status === 'INTERESTING' ? 'bg-emerald-100 text-emerald-700' :
                        tender.status === 'APPLIED' ? 'bg-purple-100 text-purple-700' :
                        'bg-slate-100 text-slate-600'
                      }`}>
                        {tender.status}
                      </span>
                      {tender.sourcePortal && (
                        <span className="text-xs text-blue-500 bg-blue-50 px-2 py-0.5 rounded">
                          {tender.sourcePortal}
                        </span>
                      )}
                      {tender.aiAnalysis && (
                        <span className="text-xs text-indigo-500 bg-indigo-50 px-2 py-0.5 rounded flex items-center gap-1">
                          <BrainCircuit className="w-3 h-3" />
                          {tender.aiAnalysis.relevanceScore}%
                        </span>
                      )}
                    </div>
                    <h3 className="text-lg font-bold text-slate-900 mb-1 group-hover:text-blue-600 transition-colors">
                      {tender.title}
                    </h3>
                    <div className="flex flex-wrap items-center gap-4 text-sm text-slate-500">
                      <div className="flex items-center gap-1">
                        <Building2 className="w-4 h-4" />
                        {tender.authority}
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        {tender.location}
                      </div>
                      {tender.publishedAt && (
                        <div className="flex items-center gap-1 text-emerald-600">
                          <Calendar className="w-4 h-4" />
                          Ausgestellt: {new Date(tender.publishedAt).toLocaleDateString('de-DE')}
                        </div>
                      )}
                      <div className="flex items-center gap-1 text-orange-600 font-medium">
                        <Clock className="w-4 h-4" />
                        Frist: {new Date(tender.deadline).toLocaleDateString('de-DE')}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2" onClick={e => e.stopPropagation()}>
                    <button 
                      onClick={() => handleStatusChange(tender.id, 'INTERESTING')}
                      className={`p-2 rounded-lg transition-colors ${
                        tender.status === 'INTERESTING' 
                          ? 'bg-emerald-100 text-emerald-600' 
                          : 'hover:bg-emerald-50 text-slate-400 hover:text-emerald-600'
                      }`}
                      title="Interessant markieren"
                    >
                      <Bookmark className="w-5 h-5" />
                    </button>
                    <button 
                      onClick={() => handleStatusChange(tender.id, 'REJECTED')}
                      className="p-2 hover:bg-red-50 text-slate-400 hover:text-red-600 rounded-lg transition-colors"
                      title="Ablehnen"
                    >
                      <X className="w-5 h-5" />
                    </button>
                    <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-blue-500 transition-colors" />
                  </div>
                </div>

                <p className="text-slate-600 text-sm leading-relaxed line-clamp-2">
                  {tender.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detail Modal */}
      {selectedTender && (
        <TenderDetailModal
          tender={selectedTender}
          onClose={() => setSelectedTender(null)}
          onStatusChange={async (status) => {
            await handleStatusChange(selectedTender.id, status);
            setSelectedTender(prev => prev ? {...prev, status: status as Tender['status']} : null);
          }}
          onAnalyze={async () => {
            await handleAnalyze(selectedTender.id, selectedTender.description);
            // Update selected tender with analysis
            const updated = tenders.find(t => t.id === selectedTender.id);
            if (updated) setSelectedTender(updated);
          }}
          analyzing={analyzingId === selectedTender.id}
        />
      )}
    </div>
  );
};
