import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './components/Dashboard';
import { TenderList } from './components/TenderList';
import { CrawlerConfig } from './components/CrawlerConfig';
import { Settings } from './components/Settings';
import { fetchTenders, Tender } from './services/tenderApi';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('tenders');
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Tenders von API laden
  const loadTenders = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchTenders();
      setTenders(data);
    } catch (e) {
      console.error('Fehler beim Laden:', e);
      setError('Backend nicht erreichbar. Starte das Backend mit: cd backend && uvicorn api:app --reload');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTenders();
  }, []);

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="ml-64 flex-1">
        <header className="bg-white border-b border-slate-200 h-16 flex items-center justify-end px-8">
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-500">Logged in as <b>Max Mustermann</b></span>
            <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold">M</div>
          </div>
        </header>

        {error && (
          <div className="m-8 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <p className="font-semibold">Verbindungsfehler</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {activeTab === 'dashboard' && <Dashboard tenders={tenders} />}
        {activeTab === 'tenders' && (
          <TenderList 
            tenders={tenders} 
            setTenders={setTenders} 
            loading={loading}
            onRefresh={loadTenders}
          />
        )}
        {activeTab === 'crawler' && <CrawlerConfig onCrawlComplete={loadTenders} />}
        {activeTab === 'settings' && <Settings />}
      </main>
    </div>
  );
};

export default App;
