import React, { useEffect, useState } from 'react';
import { adminApi } from '../services/api';
import { AdminAnalyticsPoint } from '../types';
import {
  BarChart3,
  Eye,
  Download,
  Heart,
  TrendingUp,
  Percent,
  Loader2,
  AlertCircle,
} from 'lucide-react';

export const Analytics: React.FC = () => {
  const [days, setDays] = useState<number>(7);
  const [points, setPoints] = useState<AdminAnalyticsPoint[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await adminApi.getAnalytics(days);
      if (resp.success && resp.data) {
        setPoints(resp.data);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load analytics time-series');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [days]);

  const totalViews = points.reduce((acc, p) => acc + p.views, 0);
  const totalDownloads = points.reduce((acc, p) => acc + p.downloads, 0);
  const totalFavorites = points.reduce((acc, p) => acc + p.favorites, 0);

  const downloadRate = totalViews > 0 ? ((totalDownloads / totalViews) * 100).toFixed(1) : '0.0';
  const favoriteRate = totalViews > 0 ? ((totalFavorites / totalViews) * 100).toFixed(1) : '0.0';

  const maxViews = Math.max(...points.map((p) => p.views), 1);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Platform Analytics</h1>
          <p className="text-xs text-slate-400 mt-1">
            Analyze 8K wallpaper discovery performance, retention, and conversion trends.
          </p>
        </div>

        {/* Days selector */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-[#121218] border border-[#222230]">
          {[7, 14, 30].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                days === d
                  ? 'bg-purple-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-[#1A1A24]'
              }`}
            >
              {d} Days
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-xs text-rose-300">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="p-5 rounded-2xl bg-[#121218] border border-purple-500/20">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Total Views</span>
            <div className="p-2 rounded-xl bg-purple-500/10">
              <Eye className="w-4 h-4 text-purple-400" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-3">{totalViews.toLocaleString()}</p>
        </div>

        <div className="p-5 rounded-2xl bg-[#121218] border border-amber-500/20">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Downloads</span>
            <div className="p-2 rounded-xl bg-amber-500/10">
              <Download className="w-4 h-4 text-amber-400" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-3">{totalDownloads.toLocaleString()}</p>
        </div>

        <div className="p-5 rounded-2xl bg-[#121218] border border-rose-500/20">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Favorites</span>
            <div className="p-2 rounded-xl bg-rose-500/10">
              <Heart className="w-4 h-4 text-rose-400" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-3">{totalFavorites.toLocaleString()}</p>
        </div>

        <div className="p-5 rounded-2xl bg-[#121218] border border-emerald-500/20">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Download Rate</span>
            <div className="p-2 rounded-xl bg-emerald-500/10">
              <Percent className="w-4 h-4 text-emerald-400" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-3">{downloadRate}%</p>
          <span className="text-[10px] text-slate-500">Downloads per View</span>
        </div>

        <div className="p-5 rounded-2xl bg-[#121218] border border-indigo-500/20">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Engagement</span>
            <div className="p-2 rounded-xl bg-indigo-500/10">
              <TrendingUp className="w-4 h-4 text-indigo-400" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-3">{favoriteRate}%</p>
          <span className="text-[10px] text-slate-500">Favorites per View</span>
        </div>
      </div>

      {/* Main Chart Card */}
      <div className="p-6 rounded-2xl bg-[#121218] border border-[#222230]">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-purple-400" />
            <h2 className="text-base font-bold text-white">Daily Engagement Breakdown</h2>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-sm bg-purple-500"></span>
              <span className="text-slate-400">Views</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-sm bg-amber-500"></span>
              <span className="text-slate-400">Downloads</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-sm bg-rose-500"></span>
              <span className="text-slate-400">Favorites</span>
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-3">
            <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
            <p className="text-xs text-slate-400">Compiling time-series metrics...</p>
          </div>
        ) : points.length === 0 ? (
          <p className="text-xs text-slate-500 text-center py-16">No records found for period.</p>
        ) : (
          <div
            className={`grid gap-2 h-64 items-end border-b border-[#1F1F2B] pb-2`}
            style={{ gridTemplateColumns: `repeat(${points.length}, minmax(0, 1fr))` }}
          >
            {points.map((pt, i) => {
              const viewH = Math.max((pt.views / maxViews) * 100, 6);
              const dlH = Math.max((pt.downloads / maxViews) * 100, 3);
              const favH = Math.max((pt.favorites / maxViews) * 100, 3);

              return (
                <div key={i} className="flex flex-col items-center h-full justify-end group">
                  <div className="w-full flex items-end justify-center gap-1 h-52">
                    <div
                      style={{ height: `${viewH}%` }}
                      className="w-full max-w-[12px] bg-purple-600 rounded-t-sm group-hover:bg-purple-500 transition-all cursor-pointer"
                      title={`${pt.date}: ${pt.views} Views`}
                    ></div>
                    <div
                      style={{ height: `${dlH}%` }}
                      className="w-full max-w-[12px] bg-amber-500 rounded-t-sm group-hover:bg-amber-400 transition-all cursor-pointer"
                      title={`${pt.date}: ${pt.downloads} Downloads`}
                    ></div>
                    <div
                      style={{ height: `${favH}%` }}
                      className="w-full max-w-[12px] bg-rose-500 rounded-t-sm group-hover:bg-rose-400 transition-all cursor-pointer"
                      title={`${pt.date}: ${pt.favorites} Favorites`}
                    ></div>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400 mt-2 truncate w-full text-center">
                    {pt.date.slice(5)}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Daily Data Table */}
      <div className="rounded-2xl bg-[#121218] border border-[#222230] overflow-hidden">
        <div className="p-4 border-b border-[#222230] font-bold text-white text-xs">
          Daily Ledger Metrics
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#161622] text-slate-400 uppercase tracking-wider font-semibold border-b border-[#222230]">
              <tr>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Impressions / Views</th>
                <th className="py-3 px-4">Asset Downloads</th>
                <th className="py-3 px-4">Saved Favorites</th>
                <th className="py-3 px-4">Conversion</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E1E2C] text-slate-300">
              {points.map((pt, i) => {
                const dayRate = pt.views > 0 ? ((pt.downloads / pt.views) * 100).toFixed(1) : '0.0';
                return (
                  <tr key={i} className="hover:bg-[#161622]/60 transition">
                    <td className="py-3 px-4 font-mono text-slate-200">{pt.date}</td>
                    <td className="py-3 px-4 text-purple-300 font-semibold">{pt.views.toLocaleString()}</td>
                    <td className="py-3 px-4 text-amber-300 font-semibold">{pt.downloads.toLocaleString()}</td>
                    <td className="py-3 px-4 text-rose-300 font-semibold">{pt.favorites.toLocaleString()}</td>
                    <td className="py-3 px-4 text-emerald-400 font-medium">{dayRate}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
