import React, { useEffect, useState } from 'react';
import { adminApi } from '../services/api';
import { AdminAnalyticsPoint, AdminDashboardMetrics } from '../types';
import {
  Image as ImageIcon,
  Users,
  Eye,
  Download,
  FolderTree,
  AlertTriangle,
  HardDrive,
  Heart,
  TrendingUp,
  ArrowRight,
  ShieldCheck,
  Loader2,
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<AdminDashboardMetrics | null>(null);
  const [analytics, setAnalytics] = useState<AdminAnalyticsPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [metricsResp, analyticsResp] = await Promise.all([
        adminApi.getDashboardMetrics(),
        adminApi.getAnalytics(7),
      ]);
      if (metricsResp.success && metricsResp.data) {
        setMetrics(metricsResp.data);
      }
      if (analyticsResp.success && analyticsResp.data) {
        setAnalytics(analyticsResp.data);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
        <p className="text-sm text-slate-400">Loading system metrics and telemetry...</p>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="p-8 bg-rose-500/10 border border-rose-500/20 rounded-2xl text-center">
        <AlertTriangle className="w-10 h-10 text-rose-400 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-white mb-1">Failed to Load Dashboard</h3>
        <p className="text-sm text-rose-300 mb-4">{error}</p>
        <button
          onClick={loadData}
          className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold"
        >
          Try Again
        </button>
      </div>
    );
  }

  const kpis = [
    {
      title: 'Total Wallpapers',
      value: metrics.total_wallpapers.toLocaleString(),
      icon: ImageIcon,
      color: 'text-purple-400',
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/20',
      link: '/wallpapers',
    },
    {
      title: 'Registered Users',
      value: metrics.total_users.toLocaleString(),
      icon: Users,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/20',
      link: '/users',
    },
    {
      title: 'Total Views',
      value: metrics.total_views.toLocaleString(),
      icon: Eye,
      color: 'text-blue-400',
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/20',
      link: '/analytics',
    },
    {
      title: 'Total Downloads',
      value: metrics.total_downloads.toLocaleString(),
      icon: Download,
      color: 'text-amber-400',
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/20',
      link: '/analytics',
    },
    {
      title: 'Favorites Logged',
      value: metrics.total_favorites.toLocaleString(),
      icon: Heart,
      color: 'text-rose-400',
      bg: 'bg-rose-500/10',
      border: 'border-rose-500/20',
      link: '/analytics',
    },
    {
      title: 'Pending Reports',
      value: metrics.pending_reports.length.toLocaleString(),
      icon: AlertTriangle,
      color: 'text-red-400',
      bg: 'bg-red-500/10',
      border: 'border-red-500/20',
      link: '/reports',
      alert: metrics.pending_reports.length > 0,
    },
    {
      title: 'Storage Consumed',
      value: formatBytes(metrics.storage_used_bytes),
      icon: HardDrive,
      color: 'text-cyan-400',
      bg: 'bg-cyan-500/10',
      border: 'border-cyan-500/20',
    },
    {
      title: 'Taxonomies',
      value: `${metrics.total_categories} Cats / ${metrics.total_collections} Colls`,
      icon: FolderTree,
      color: 'text-indigo-400',
      bg: 'bg-indigo-500/10',
      border: 'border-indigo-500/20',
      link: '/categories',
    },
  ];

  const maxDailyViews = Math.max(...analytics.map((a) => a.views), 1);

  return (
    <div className="space-y-8">
      {/* Title & Overview Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Operations Dashboard</h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time platform vitals, catalog moderation, and user engagement metrics.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            className="px-3.5 py-1.5 rounded-lg bg-[#181822] hover:bg-[#20202E] border border-[#2B2B3D] text-xs font-semibold text-slate-300 transition"
          >
            Refresh Vitals
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          const CardContent = (
            <div
              className={`p-5 rounded-2xl bg-[#121218] border ${kpi.border} transition-all hover:bg-[#161620] relative overflow-hidden group`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">{kpi.title}</span>
                <div className={`p-2 rounded-xl ${kpi.bg}`}>
                  <Icon className={`w-4 h-4 ${kpi.color}`} />
                </div>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-2xl font-bold text-white tracking-tight">{kpi.value}</span>
                {kpi.alert && (
                  <span className="text-[10px] font-semibold text-red-400 bg-red-500/10 px-2 py-0.5 rounded border border-red-500/20 animate-pulse">
                    Action Required
                  </span>
                )}
              </div>
            </div>
          );

          return kpi.link ? (
            <Link key={idx} to={kpi.link}>
              {CardContent}
            </Link>
          ) : (
            <div key={idx}>{CardContent}</div>
          );
        })}
      </div>

      {/* 7-Day Engagement Chart */}
      <div className="p-6 rounded-2xl bg-[#121218] border border-[#222230]">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-purple-400" />
            <h2 className="text-base font-bold text-white">7-Day Engagement Trend</h2>
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

        {analytics.length === 0 ? (
          <p className="text-xs text-slate-500 text-center py-12">No activity recorded in the past 7 days</p>
        ) : (
          <div className="grid grid-cols-7 gap-3 h-48 items-end pt-6 border-b border-[#1F1F2B] pb-2">
            {analytics.map((pt, i) => {
              const viewHeight = Math.max((pt.views / maxDailyViews) * 100, 8);
              const downloadHeight = Math.max((pt.downloads / maxDailyViews) * 100, 4);
              const favHeight = Math.max((pt.favorites / maxDailyViews) * 100, 4);

              return (
                <div key={i} className="flex flex-col items-center h-full justify-end group">
                  <div className="w-full flex items-end justify-center gap-1 h-36">
                    {/* Views bar */}
                    <div
                      style={{ height: `${viewHeight}%` }}
                      className="w-3 sm:w-4 bg-purple-600 rounded-t-sm group-hover:bg-purple-500 transition-all relative"
                      title={`Views: ${pt.views}`}
                    ></div>
                    {/* Downloads bar */}
                    <div
                      style={{ height: `${downloadHeight}%` }}
                      className="w-3 sm:w-4 bg-amber-500 rounded-t-sm group-hover:bg-amber-400 transition-all relative"
                      title={`Downloads: ${pt.downloads}`}
                    ></div>
                    {/* Favorites bar */}
                    <div
                      style={{ height: `${favHeight}%` }}
                      className="w-3 sm:w-4 bg-rose-500 rounded-t-sm group-hover:bg-rose-400 transition-all relative"
                      title={`Favorites: ${pt.favorites}`}
                    ></div>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400 mt-2">
                    {pt.date.slice(5)}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Two Column Section: Recent Wallpapers & Pending Moderation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Wallpapers */}
        <div className="p-6 rounded-2xl bg-[#121218] border border-[#222230]">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-white">Recent Additions</h2>
            <Link
              to="/wallpapers"
              className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1 font-medium"
            >
              <span>View All</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {metrics.recent_wallpapers.length === 0 ? (
            <p className="text-xs text-slate-500 py-8 text-center">No wallpapers uploaded yet</p>
          ) : (
            <div className="space-y-3">
              {metrics.recent_wallpapers.slice(0, 5).map((wp) => (
                <div
                  key={wp.id}
                  className="flex items-center gap-3 p-2.5 rounded-xl bg-[#181822] border border-[#232332] hover:border-purple-500/30 transition"
                >
                  <img
                    src={wp.thumbnail_url}
                    alt={wp.title}
                    className="w-12 h-16 object-cover rounded-lg bg-black"
                  />
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-semibold text-slate-200 truncate">{wp.title}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300">
                        {wp.resolution}
                      </span>
                      <span className="text-[10px] text-slate-400">
                        {wp.category?.name || 'Uncategorized'}
                      </span>
                    </div>
                  </div>
                  <div className="text-right text-xs">
                    <span
                      className={`inline-block w-2 h-2 rounded-full ${
                        wp.is_published ? 'bg-emerald-500' : 'bg-rose-500'
                      }`}
                      title={wp.is_published ? 'Published' : 'Unpublished'}
                    ></span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Pending Moderation Reports */}
        <div className="p-6 rounded-2xl bg-[#121218] border border-[#222230]">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-white">Pending Moderation Queue</h2>
            <Link
              to="/reports"
              className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1 font-medium"
            >
              <span>Manage Queue</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {metrics.pending_reports.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10 text-center">
              <ShieldCheck className="w-10 h-10 text-emerald-400 mb-2" />
              <p className="text-sm font-semibold text-slate-300">Moderation Queue Clear</p>
              <p className="text-xs text-slate-500 mt-0.5">No reported content pending review.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {metrics.pending_reports.slice(0, 5).map((rep) => (
                <div
                  key={rep.id}
                  className="flex items-center justify-between p-3 rounded-xl bg-rose-500/5 border border-rose-500/20"
                >
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-rose-500/20 text-rose-300">
                      {rep.reason}
                    </span>
                    <p className="text-xs text-slate-300 mt-1 line-clamp-1">
                      {rep.description || 'No description provided'}
                    </p>
                  </div>
                  <Link
                    to="/reports"
                    className="px-3 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold shrink-0"
                  >
                    Review
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
