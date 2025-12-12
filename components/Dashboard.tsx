import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Tender } from '../services/tenderApi';
import { ArrowUpRight, Clock, CheckCircle2, Inbox } from 'lucide-react';

interface DashboardProps {
  tenders: Tender[];
}

export const Dashboard: React.FC<DashboardProps> = ({ tenders }) => {
  const stats = {
    total: tenders.length,
    new: tenders.filter(t => t.status === 'NEW').length,
    interesting: tenders.filter(t => t.status === 'INTERESTING').length,
    deadlineSoon: tenders.filter(t => {
      try {
        const days = (new Date(t.deadline).getTime() - new Date().getTime()) / (1000 * 3600 * 24);
        return days > 0 && days < 14;
      } catch {
        return false;
      }
    }).length,
  };

  // Prepare data for chart
  const categoryData = tenders.reduce((acc, curr) => {
    const existing = acc.find(i => i.name === curr.category);
    if (existing) {
      existing.count += 1;
    } else {
      acc.push({ name: curr.category, count: 1 });
    }
    return acc;
  }, [] as { name: string; count: number }[]);

  // Portal-Verteilung
  const portalData = tenders.reduce((acc, curr) => {
    const portal = curr.sourcePortal || 'Unbekannt';
    const existing = acc.find(i => i.name === portal);
    if (existing) {
      existing.count += 1;
    } else {
      acc.push({ name: portal, count: 1 });
    }
    return acc;
  }, [] as { name: string; count: number }[]);

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <h2 className="text-2xl font-bold text-slate-900 mb-6">Dashboard Overview</h2>
      
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-blue-50 rounded-lg text-blue-600">
              <Inbox className="w-6 h-6" />
            </div>
            {stats.new > 0 && (
              <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-1 rounded">
                {stats.new} neu
              </span>
            )}
          </div>
          <p className="text-slate-500 text-sm font-medium">New Tenders</p>
          <h3 className="text-3xl font-bold text-slate-900">{stats.new}</h3>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-indigo-50 rounded-lg text-indigo-600">
              <CheckCircle2 className="w-6 h-6" />
            </div>
          </div>
          <p className="text-slate-500 text-sm font-medium">Marked Interesting</p>
          <h3 className="text-3xl font-bold text-slate-900">{stats.interesting}</h3>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-orange-50 rounded-lg text-orange-600">
              <Clock className="w-6 h-6" />
            </div>
          </div>
          <p className="text-slate-500 text-sm font-medium">Deadlines (14 days)</p>
          <h3 className="text-3xl font-bold text-slate-900">{stats.deadlineSoon}</h3>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-purple-50 rounded-lg text-purple-600">
              <ArrowUpRight className="w-6 h-6" />
            </div>
          </div>
          <p className="text-slate-500 text-sm font-medium">Total Tracked</p>
          <h3 className="text-3xl font-bold text-slate-900">{stats.total}</h3>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Chart */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm h-96">
          <h3 className="text-lg font-bold text-slate-900 mb-6">Tenders by Category</h3>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height="80%">
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
                <Tooltip 
                  cursor={{ fill: '#f1f5f9' }}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={40} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-slate-400">
              Keine Daten verfügbar
            </div>
          )}
        </div>

        {/* Portal Chart */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm h-96">
          <h3 className="text-lg font-bold text-slate-900 mb-6">Tenders by Portal</h3>
          {portalData.length > 0 ? (
            <ResponsiveContainer width="100%" height="80%">
              <BarChart data={portalData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
                <YAxis type="category" dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} width={120} />
                <Tooltip 
                  cursor={{ fill: '#f1f5f9' }}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Bar dataKey="count" fill="#8b5cf6" radius={[0, 4, 4, 0]} barSize={24} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-slate-400">
              Keine Daten verfügbar
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
