import React, { useEffect, useState } from 'react';
import { adminApi } from '../services/api';
import { SubscriberItem, SubscriptionMetrics } from '../types';
import {
  CreditCard,
  TrendingUp,
  DollarSign,
  Users,
  Video,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Search,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  Crown,
  Sparkles,
} from 'lucide-react';

export const Subscriptions: React.FC = () => {
  const [metrics, setMetrics] = useState<SubscriptionMetrics | null>(null);
  const [subscribers, setSubscribers] = useState<SubscriberItem[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [limit] = useState(15);

  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  const fetchData = async () => {
    setError(null);
    try {
      const [metricsResp, subscribersResp] = await Promise.all([
        adminApi.getSubscriptionMetrics(),
        adminApi.getSubscribers(page, limit),
      ]);

      if (metricsResp.success && metricsResp.data) {
        setMetrics(metricsResp.data);
      }

      if (subscribersResp.success && subscribersResp.data) {
        setSubscribers(subscribersResp.data);
        setTotal(subscribersResp.meta.total);
        setTotalPages(subscribersResp.meta.total_pages);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load subscription analytics');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [page]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    fetchData();
  };

  const filteredSubscribers = subscribers.filter((sub) => {
    if (!search.trim()) return true;
    const term = search.toLowerCase();
    return (
      sub.id.toLowerCase().includes(term) ||
      sub.user_id.toLowerCase().includes(term) ||
      (sub.order_id && sub.order_id.toLowerCase().includes(term)) ||
      sub.plan.toLowerCase().includes(term)
    );
  });

  const getPlanBadge = (plan: string) => {
    switch (plan) {
      case 'PRO_LIFETIME':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <Crown className="w-3 h-3 text-amber-400" />
            Lifetime Ultra
          </span>
        );
      case 'PRO_ANNUAL':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
            <Sparkles className="w-3 h-3 text-indigo-400" />
            Annual Pro
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/30">
            Monthly Pro
          </span>
        );
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" />
            Active
          </span>
        );
      case 'CANCELLED':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <XCircle className="w-3 h-3" />
            Cancelled
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-slate-500/10 text-slate-400 border border-slate-500/20">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <CreditCard className="w-7 h-7 text-purple-400" />
            Monetization & Subscriptions
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time subscriber ledger, MRR analytics, and store transaction auditing
          </p>
        </div>

        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#1A1A22] text-slate-300 hover:text-white hover:bg-[#22222E] border border-[#22222E] transition"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-purple-400' : ''}`} />
          <span className="text-sm font-medium">Refresh</span>
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* KPI Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-[#121217] border border-[#22222E] shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Active Subscribers</span>
            <Users className="w-5 h-5 text-purple-400" />
          </div>
          <div className="mt-3 text-2xl font-bold text-white">
            {metrics ? metrics.active_subscribers.toLocaleString() : '—'}
          </div>
          <p className="text-xs text-slate-400 mt-1">Paying VIP accounts</p>
        </div>

        <div className="p-5 rounded-xl bg-[#121217] border border-[#22222E] shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Estimated MRR</span>
            <TrendingUp className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="mt-3 text-2xl font-bold text-white">
            {metrics ? `$${metrics.mrr.toFixed(2)}` : '—'}
          </div>
          <p className="text-xs text-slate-400 mt-1">Monthly Recurring Run-rate</p>
        </div>

        <div className="p-5 rounded-xl bg-[#121217] border border-[#22222E] shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Gross Platform Revenue</span>
            <DollarSign className="w-5 h-5 text-blue-400" />
          </div>
          <div className="mt-3 text-2xl font-bold text-white">
            {metrics ? `$${metrics.total_revenue.toFixed(2)}` : '—'}
          </div>
          <p className="text-xs text-slate-400 mt-1">Total verified sales</p>
        </div>

        <div className="p-5 rounded-xl bg-[#121217] border border-[#22222E] shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Rewarded Ad Unlocks</span>
            <Video className="w-5 h-5 text-amber-400" />
          </div>
          <div className="mt-3 text-2xl font-bold text-white">
            {metrics ? metrics.total_ad_unlocks.toLocaleString() : '—'}
          </div>
          <p className="text-xs text-slate-400 mt-1">24h 8K passes claimed</p>
        </div>
      </div>

      {/* Plan Breakdown Section */}
      {metrics && metrics.plan_breakdown && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-[#121217] border border-[#22222E] flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase">Monthly Subscribers</p>
              <p className="text-xl font-bold text-white mt-1">
                {metrics.plan_breakdown['PRO_MONTHLY'] || 0}
              </p>
              <p className="text-xs text-purple-400 mt-0.5">$4.99 / month</p>
            </div>
            <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-400">
              <CreditCard className="w-5 h-5" />
            </div>
          </div>

          <div className="p-4 rounded-xl bg-[#121217] border border-[#22222E] flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase">Annual Subscribers</p>
              <p className="text-xl font-bold text-white mt-1">
                {metrics.plan_breakdown['PRO_ANNUAL'] || 0}
              </p>
              <p className="text-xs text-indigo-400 mt-0.5">$29.99 / year (Save 50%)</p>
            </div>
            <div className="p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Sparkles className="w-5 h-5" />
            </div>
          </div>

          <div className="p-4 rounded-xl bg-[#121217] border border-[#22222E] flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase">Lifetime Members</p>
              <p className="text-xl font-bold text-white mt-1">
                {metrics.plan_breakdown['PRO_LIFETIME'] || 0}
              </p>
              <p className="text-xs text-amber-400 mt-0.5">$79.99 one-time</p>
            </div>
            <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <Crown className="w-5 h-5" />
            </div>
          </div>
        </div>
      )}

      {/* Subscriber Ledger Table */}
      <div className="rounded-xl bg-[#121217] border border-[#22222E] overflow-hidden shadow-sm">
        {/* Table Controls */}
        <div className="p-4 border-b border-[#22222E] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search by User ID, Order ID, or Plan..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-[#1A1A22] border border-[#22222E] rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 transition"
            />
          </div>

          <div className="text-xs text-slate-400">
            Showing <span className="font-semibold text-white">{filteredSubscribers.length}</span> of{' '}
            <span className="font-semibold text-white">{total}</span> total subscribers
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-[#16161D] text-xs font-semibold text-slate-400 uppercase tracking-wider border-b border-[#22222E]">
              <tr>
                <th className="px-6 py-3.5">User Identifier</th>
                <th className="px-6 py-3.5">Tier Plan</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5">Store / Platform</th>
                <th className="px-6 py-3.5">Order ID</th>
                <th className="px-6 py-3.5">Price</th>
                <th className="px-6 py-3.5">Expires At</th>
                <th className="px-6 py-3.5">Auto Renew</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#22222E]">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-slate-500">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-purple-400" />
                    Loading subscriber ledger...
                  </td>
                </tr>
              ) : filteredSubscribers.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-slate-500">
                    No subscribers found matching criteria.
                  </td>
                </tr>
              ) : (
                filteredSubscribers.map((sub) => (
                  <tr key={sub.id} className="hover:bg-[#1A1A22]/50 transition">
                    <td className="px-6 py-4 font-mono text-xs text-slate-300">
                      {sub.user_id.slice(0, 8)}...{sub.user_id.slice(-6)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">{getPlanBadge(sub.plan)}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{getStatusBadge(sub.status)}</td>
                    <td className="px-6 py-4 text-xs font-medium text-slate-300 capitalize">
                      {sub.store.replace('_', ' ')}
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-400">
                      {sub.order_id || 'GPA.DIRECT'}
                    </td>
                    <td className="px-6 py-4 font-semibold text-white">
                      ${sub.price_amount.toFixed(2)} {sub.currency}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      {sub.expires_at ? new Date(sub.expires_at).toLocaleDateString() : 'Lifetime'}
                    </td>
                    <td className="px-6 py-4 text-center">
                      {sub.auto_renewing ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 inline" />
                      ) : (
                        <XCircle className="w-4 h-4 text-slate-500 inline" />
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="p-4 border-t border-[#22222E] flex items-center justify-between">
            <span className="text-xs text-slate-400">
              Page {page} of {totalPages}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="p-1.5 rounded-lg bg-[#1A1A22] text-slate-300 hover:text-white disabled:opacity-40 transition"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="p-1.5 rounded-lg bg-[#1A1A22] text-slate-300 hover:text-white disabled:opacity-40 transition"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
