import React, { useState, useEffect } from 'react';
import { Save, Globe, Play, Loader2, CheckCircle, AlertCircle, Plus, X, Eye, EyeOff, Trash2 } from 'lucide-react';
import { fetchPortals, startCrawl, getCrawlStatus, Portal, CrawlStatus, addPortal, deletePortal } from '../services/tenderApi';

interface CrawlerConfigProps {
  onCrawlComplete?: () => void;
}

interface NewPortalForm {
  name: string;
  url: string;
  region: string;
  criteria: string;
  username: string;
  password: string;
  // Optionale CSS-Selektoren
  usernameSelector: string;
  passwordSelector: string;
  loginButtonSelector: string;
  tenderListSelector: string;
}

const emptyForm: NewPortalForm = {
  name: '',
  url: '',
  region: '',
  criteria: '',
  username: '',
  password: '',
  usernameSelector: '',
  passwordSelector: '',
  loginButtonSelector: '',
  tenderListSelector: ''
};

export const CrawlerConfig: React.FC<CrawlerConfigProps> = ({ onCrawlComplete }) => {
  const [portals, setPortals] = useState<Portal[]>([]);
  const [crawlStatus, setCrawlStatus] = useState<CrawlStatus | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newPortal, setNewPortal] = useState<NewPortalForm>(emptyForm);
  const [showPassword, setShowPassword] = useState(false);
  const [saving, setSaving] = useState(false);

  // Portale laden
  useEffect(() => {
    const loadPortals = async () => {
      try {
        const data = await fetchPortals();
        setPortals(data);
        setError(null);
      } catch (e) {
        setError('Backend nicht erreichbar');
      }
    };
    loadPortals();
  }, []);

  // Crawler-Status prüfen
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const status = await getCrawlStatus();
        setCrawlStatus(status);
        
        // Wenn Crawling beendet, Tenders neu laden
        if (!status.running && crawlStatus?.running) {
          onCrawlComplete?.();
        }
      } catch {
        // Ignore
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 3000);
    return () => clearInterval(interval);
  }, [crawlStatus?.running, onCrawlComplete]);

  const handleStartCrawl = async () => {
    setIsStarting(true);
    try {
      await startCrawl();
      const status = await getCrawlStatus();
      setCrawlStatus(status);
    } catch (e) {
      alert('Fehler beim Starten des Crawlers');
    } finally {
      setIsStarting(false);
    }
  };

  const handleAddPortal = async () => {
    if (!newPortal.name || !newPortal.url) {
      alert('Name und URL sind erforderlich');
      return;
    }
    
    setSaving(true);
    try {
      await addPortal(newPortal);
      // Portale neu laden
      const data = await fetchPortals();
      setPortals(data);
      setNewPortal(emptyForm);
      setShowAddForm(false);
    } catch (e) {
      alert('Fehler beim Speichern des Portals');
    } finally {
      setSaving(false);
    }
  };

  const handleDeletePortal = async (portalId: string) => {
    if (!confirm('Portal wirklich loeschen?')) return;
    
    try {
      await deletePortal(portalId);
      setPortals(prev => prev.filter(p => p.id !== portalId));
    } catch (e) {
      alert('Fehler beim Loeschen');
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900">Crawler Configuration</h2>
        <p className="text-slate-500">Manage your portal connections and start crawling.</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          <span>{error} - Starte das Backend mit: <code className="bg-red-100 px-2 py-0.5 rounded">cd backend && uvicorn api:app --reload</code></span>
        </div>
      )}

      <div className="space-y-6">
        {/* Crawler Control Panel */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Play className="w-5 h-5 text-emerald-500" />
                Crawler Control
              </h3>
              <p className="text-sm text-slate-500 mt-1">
                Starte den Crawler um alle Portale zu durchsuchen.
              </p>
            </div>
            
            <button 
              onClick={handleStartCrawl}
              disabled={isStarting || crawlStatus?.running}
              className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white font-medium rounded-lg flex items-center gap-2 shadow-lg shadow-emerald-900/20 transition-colors"
            >
              {crawlStatus?.running ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Crawler läuft...
                </>
              ) : isStarting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Starte...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Crawler starten
                </>
              )}
            </button>
          </div>

          {/* Status Info */}
          {crawlStatus && (
            <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-slate-500">Status:</span>
                  <div className="flex items-center gap-2 mt-1">
                    {crawlStatus.running ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                        <span className="font-medium text-blue-600">Läuft</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle className="w-4 h-4 text-emerald-500" />
                        <span className="font-medium text-emerald-600">Bereit</span>
                      </>
                    )}
                  </div>
                </div>
                <div>
                  <span className="text-slate-500">Letzter Lauf:</span>
                  <p className="font-medium text-slate-700 mt-1">
                    {crawlStatus.last_run 
                      ? new Date(crawlStatus.last_run).toLocaleString('de-DE')
                      : 'Noch nie'
                    }
                  </p>
                </div>
                <div>
                  <span className="text-slate-500">Ergebnis:</span>
                  <p className="font-medium text-slate-700 mt-1">
                    {crawlStatus.results || '-'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Add Portal Form */}
        {showAddForm && (
          <div className="bg-white rounded-xl border border-blue-200 shadow-sm p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Plus className="w-5 h-5 text-blue-500" />
                Neues Portal hinzufuegen
              </h3>
              <button onClick={() => setShowAddForm(false)} className="p-2 hover:bg-slate-100 rounded-lg">
                <X className="w-5 h-5 text-slate-500" />
              </button>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Portal Name *</label>
                <input
                  type="text"
                  placeholder="z.B. Mein Portal"
                  value={newPortal.name}
                  onChange={e => setNewPortal(prev => ({...prev, name: e.target.value}))}
                  className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Website URL *</label>
                <input
                  type="url"
                  placeholder="https://www.beispiel.de"
                  value={newPortal.url}
                  onChange={e => setNewPortal(prev => ({...prev, url: e.target.value}))}
                  className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Region</label>
                <input
                  type="text"
                  placeholder="z.B. Bayern, Wien, etc."
                  value={newPortal.region}
                  onChange={e => setNewPortal(prev => ({...prev, region: e.target.value}))}
                  className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Suchkriterien</label>
                <input
                  type="text"
                  placeholder="z.B. Tiefbau, Hochbau"
                  value={newPortal.criteria}
                  onChange={e => setNewPortal(prev => ({...prev, criteria: e.target.value}))}
                  className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Benutzername</label>
                <input
                  type="text"
                  placeholder="Login-Benutzername"
                  value={newPortal.username}
                  onChange={e => setNewPortal(prev => ({...prev, username: e.target.value}))}
                  className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Passwort</label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Login-Passwort"
                    value={newPortal.password}
                    onChange={e => setNewPortal(prev => ({...prev, password: e.target.value}))}
                    className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>
            
            {/* Optionale CSS-Selektoren */}
            <div className="border-t border-slate-200 pt-4 mt-4">
              <h4 className="text-sm font-semibold text-slate-700 mb-3">Optionale CSS-Selektoren (fuer Experten)</h4>
              <p className="text-xs text-slate-500 mb-4">
                Falls der Crawler die Felder nicht automatisch findet, kannst du hier CSS-Selektoren angeben.
              </p>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Username-Feld Selektor</label>
                  <input
                    type="text"
                    placeholder='z.B. input[name="email"]'
                    value={newPortal.usernameSelector}
                    onChange={e => setNewPortal(prev => ({...prev, usernameSelector: e.target.value}))}
                    className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Passwort-Feld Selektor</label>
                  <input
                    type="text"
                    placeholder='z.B. input[type="password"]'
                    value={newPortal.passwordSelector}
                    onChange={e => setNewPortal(prev => ({...prev, passwordSelector: e.target.value}))}
                    className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Login-Button Selektor</label>
                  <input
                    type="text"
                    placeholder='z.B. button[type="submit"]'
                    value={newPortal.loginButtonSelector}
                    onChange={e => setNewPortal(prev => ({...prev, loginButtonSelector: e.target.value}))}
                    className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Ausschreibungs-Liste Selektor</label>
                  <input
                    type="text"
                    placeholder='z.B. .tender-item, table tr'
                    value={newPortal.tenderListSelector}
                    onChange={e => setNewPortal(prev => ({...prev, tenderListSelector: e.target.value}))}
                    className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono"
                  />
                </div>
              </div>
            </div>
            
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowAddForm(false)}
                className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
              >
                Abbrechen
              </button>
              <button
                onClick={handleAddPortal}
                disabled={saving}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg flex items-center gap-2 disabled:opacity-50"
              >
                {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                Portal speichern
              </button>
            </div>
          </div>
        )}

        {/* Portal Table */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-200 flex justify-between items-center">
            <div>
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Globe className="w-5 h-5 text-blue-500" />
                Konfigurierte Portale
              </h3>
              <p className="text-sm text-slate-500 mt-1">
                Diese Portale werden vom Crawler durchsucht. Credentials sind sicher im Backend gespeichert.
              </p>
            </div>
            {!showAddForm && (
              <button
                onClick={() => setShowAddForm(true)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg flex items-center gap-2 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Portal hinzufuegen
              </button>
            )}
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-slate-700 font-semibold uppercase text-xs">
                <tr>
                  <th className="px-6 py-4">Portal</th>
                  <th className="px-6 py-4">Region</th>
                  <th className="px-6 py-4">Suchkriterien</th>
                  <th className="px-6 py-4">URL</th>
                  <th className="px-6 py-4 text-right">Aktionen</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {portals.length === 0 && !error && (
                  <tr>
                    <td colSpan={5} className="px-6 py-8 text-center text-slate-400">
                      <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
                      Lade Portale...
                    </td>
                  </tr>
                )}
                {portals.map((portal) => (
                  <tr key={portal.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-6 py-4 font-medium text-slate-900">
                      <div className="flex items-center gap-2">
                        {portal.name}
                        {portal.isCustom && (
                          <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">Benutzerdefiniert</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">{portal.region}</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
                        {portal.criteria}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <a 
                        href={portal.url} 
                        target="_blank" 
                        rel="noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        {portal.url.replace(/^https?:\/\/(www\.)?/, '')}
                      </a>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {portal.isCustom && (
                        <button
                          onClick={() => handleDeletePortal(portal.id)}
                          className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Portal loeschen"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 rounded-xl border border-blue-100 p-6">
          <h4 className="font-semibold text-blue-900 mb-2">Hinweis</h4>
          <p className="text-sm text-blue-700">
            Die Portal-Zugangsdaten sind sicher im Backend gespeichert (<code className="bg-blue-100 px-1 rounded">backend/.env</code>). 
            Die Crawler-Selektoren müssen möglicherweise an die tatsächliche Struktur der Portale angepasst werden.
          </p>
        </div>
      </div>
    </div>
  );
};
