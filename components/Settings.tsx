import React, { useState, useEffect } from 'react';
import { Save, Globe, Search, MapPin, Briefcase, Loader2, CheckCircle } from 'lucide-react';

interface PortalSettings {
  id: string;
  name: string;
  url: string;
  region: string;
  criteria: string;
  enabled: boolean;
}

interface CrawlerSettings {
  globalKeywords: string;
  minBudget: string;
  excludeKeywords: string;
  portals: PortalSettings[];
}

export const Settings: React.FC = () => {
  const [settings, setSettings] = useState<CrawlerSettings>({
    globalKeywords: '',
    minBudget: '50000',
    excludeKeywords: 'Reinigung, Catering, Gebäudereinigung',
    portals: []
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  // Portale laden
  useEffect(() => {
    const loadSettings = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/portals');
        if (response.ok) {
          const portals = await response.json();
          setSettings(prev => ({
            ...prev,
            portals: portals.map((p: any) => ({
              ...p,
              enabled: true
            }))
          }));
        }
      } catch (e) {
        console.error('Fehler beim Laden:', e);
      } finally {
        setLoading(false);
      }
    };
    loadSettings();
  }, []);

  const handlePortalChange = (id: string, field: string, value: string | boolean) => {
    setSettings(prev => ({
      ...prev,
      portals: prev.portals.map(p => 
        p.id === id ? { ...p, [field]: value } : p
      )
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const response = await fetch('http://localhost:8000/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });
      
      if (response.ok) {
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
      }
    } catch (e) {
      alert('Fehler beim Speichern');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900">Crawler Einstellungen</h2>
        <p className="text-slate-500">Konfiguriere die Suchkriterien für jeden Portal.</p>
      </div>

      <div className="space-y-6">
        {/* Globale Filter */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Search className="w-5 h-5 text-blue-500" />
            Globale Suchkriterien
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Suchbegriffe (Keywords)
              </label>
              <input 
                type="text"
                placeholder="z.B. Hochbau, Rohbau, Tiefbau"
                value={settings.globalKeywords}
                onChange={(e) => setSettings(prev => ({ ...prev, globalKeywords: e.target.value }))}
                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-slate-400 mt-1">Kommagetrennt</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Mindest-Budget (€)
              </label>
              <input 
                type="number"
                value={settings.minBudget}
                onChange={(e) => setSettings(prev => ({ ...prev, minBudget: e.target.value }))}
                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Ausschließen (Keywords)
              </label>
              <input 
                type="text"
                placeholder="z.B. Reinigung, Catering"
                value={settings.excludeKeywords}
                onChange={(e) => setSettings(prev => ({ ...prev, excludeKeywords: e.target.value }))}
                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Portal-spezifische Einstellungen */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-200">
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Globe className="w-5 h-5 text-emerald-500" />
              Portal-Einstellungen
            </h3>
            <p className="text-sm text-slate-500 mt-1">
              Passe die Suchkriterien für jedes Portal individuell an.
            </p>
          </div>
          
          <div className="divide-y divide-slate-100">
            {settings.portals.map((portal) => (
              <div key={portal.id} className="p-6 hover:bg-slate-50/50 transition-colors">
                <div className="flex items-start gap-4">
                  {/* Enabled Toggle */}
                  <div className="pt-1">
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input 
                        type="checkbox"
                        checked={portal.enabled}
                        onChange={(e) => handlePortalChange(portal.id, 'enabled', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-100 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                  
                  {/* Portal Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-4">
                      <h4 className="font-semibold text-slate-900">{portal.name}</h4>
                      <a 
                        href={portal.url} 
                        target="_blank" 
                        rel="noreferrer"
                        className="text-xs text-blue-500 hover:underline"
                      >
                        {portal.url.replace(/^https?:\/\/(www\.)?/, '')}
                      </a>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm text-slate-600 flex items-center gap-1 mb-1">
                          <MapPin className="w-4 h-4" />
                          Region / Bundesland
                        </label>
                        <input 
                          type="text"
                          value={portal.region}
                          onChange={(e) => handlePortalChange(portal.id, 'region', e.target.value)}
                          placeholder="z.B. Bayern, Tirol, Vorarlberg"
                          className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      
                      <div>
                        <label className="text-sm text-slate-600 flex items-center gap-1 mb-1">
                          <Briefcase className="w-4 h-4" />
                          Gewerk / Kategorie
                        </label>
                        <input 
                          type="text"
                          value={portal.criteria}
                          onChange={(e) => handlePortalChange(portal.id, 'criteria', e.target.value)}
                          placeholder="z.B. Tiefbau, Erdarbeiten, Straßenbau"
                          className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end gap-4">
          {saved && (
            <div className="flex items-center gap-2 text-emerald-600">
              <CheckCircle className="w-5 h-5" />
              <span>Gespeichert!</span>
            </div>
          )}
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium rounded-lg flex items-center gap-2 shadow-lg shadow-blue-900/20 transition-colors"
          >
            {saving ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Speichert...
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                Einstellungen speichern
              </>
            )}
          </button>
        </div>

        {/* Info Box */}
        <div className="bg-amber-50 rounded-xl border border-amber-100 p-6">
          <h4 className="font-semibold text-amber-900 mb-2">💡 Tipp</h4>
          <p className="text-sm text-amber-700">
            Die Suchkriterien werden beim nächsten Crawler-Lauf verwendet. 
            Der Crawler läuft automatisch 2x täglich (06:00 und 18:00 Uhr) 
            oder kann manuell über den "Crawler"-Tab gestartet werden.
          </p>
        </div>
      </div>
    </div>
  );
};

