import React, { useEffect, useState } from 'react';
import { adminApi } from '../services/api';
import { Report, ReportStatus } from '../types';
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  ChevronLeft,
  ChevronRight,
  Loader2,
  AlertCircle,
  ShieldCheck,
  X,
} from 'lucide-react';

export const Reports: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('PENDING');
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const limit = 15;

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Modal resolution state
  const [resolvingReport, setResolvingReport] = useState<Report | null>(null);
  const [unpublishWallpaper, setUnpublishWallpaper] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchReports = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await adminApi.listReports({
        page,
        limit,
        status: (statusFilter as ReportStatus) || undefined,
      });

      if (resp.success) {
        setReports(resp.data);
        setTotal(resp.meta.total);
        setTotalPages(resp.meta.total_pages);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch content reports');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [page, statusFilter]);

  const handleResolveAction = async (status: ReportStatus, unpublish: boolean) => {
    if (!resolvingReport) return;
    setIsSubmitting(true);
    try {
      const resp = await adminApi.resolveReport(resolvingReport.id, {
        status,
        unpublish_wallpaper: unpublish,
      });

      if (resp.success && resp.data) {
        setReports((prev) =>
          prev.map((r) => (r.id === resolvingReport.id ? resp.data : r))
        );
        setResolvingReport(null);
      }
    } catch (err: any) {
      alert(err.message || 'Failed to resolve report');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getReasonColor = (reason: string) => {
    switch (reason) {
      case 'COPYRIGHT':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      case 'INAPPROPRIATE':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
      case 'SPAM':
        return 'bg-orange-500/20 text-orange-300 border-orange-500/30';
      default:
        return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Content Moderation Queue</h1>
          <p className="text-xs text-slate-400 mt-1">
            Review user-submitted infringement and guideline reports with 1-click takedown.
          </p>
        </div>
        <div className="text-xs text-slate-400">
          Reports in queue: <span className="font-bold text-white">{total}</span>
        </div>
      </div>

      {/* Status Filter Tabs */}
      <div className="flex items-center gap-2 p-1.5 rounded-2xl bg-[#121218] border border-[#222230] w-fit">
        {['PENDING', 'REVIEWING', 'RESOLVED', 'REJECTED'].map((st) => (
          <button
            key={st}
            onClick={() => {
              setStatusFilter(st);
              setPage(1);
            }}
            className={`px-4 py-1.5 rounded-xl text-xs font-semibold transition ${
              statusFilter === st
                ? 'bg-purple-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-[#1A1A24]'
            }`}
          >
            {st}
          </button>
        ))}
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-xs text-rose-300">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Reports Table / Card List */}
      <div className="rounded-2xl bg-[#121218] border border-[#222230] overflow-hidden">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-24 gap-3">
            <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
            <p className="text-xs text-slate-400">Loading moderation queue...</p>
          </div>
        ) : reports.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <ShieldCheck className="w-12 h-12 text-emerald-400 mb-3" />
            <p className="text-sm font-semibold text-slate-200">No {statusFilter} Reports</p>
            <p className="text-xs text-slate-500 mt-1">All reports in this category have been processed.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#161622] text-slate-400 uppercase tracking-wider font-semibold border-b border-[#222230]">
                <tr>
                  <th className="py-3 px-4">Reason</th>
                  <th className="py-3 px-4">Description & Evidence</th>
                  <th className="py-3 px-4">Wallpaper ID</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Filed At</th>
                  <th className="py-3 px-4 text-right">Review Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1E1E2C] text-slate-300">
                {reports.map((rep) => (
                  <tr key={rep.id} className="hover:bg-[#161622]/60 transition">
                    <td className="py-3 px-4">
                      <span
                        className={`inline-block text-[10px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider ${getReasonColor(
                          rep.reason
                        )}`}
                      >
                        {rep.reason}
                      </span>
                    </td>

                    <td className="py-3 px-4 max-w-sm">
                      <p className="text-slate-200 leading-relaxed font-medium">
                        {rep.description || 'No detailed explanation provided by reporter'}
                      </p>
                      <p className="text-[10px] text-slate-500 font-mono mt-1">
                        Reporter: {rep.reporter_id}
                      </p>
                    </td>

                    <td className="py-3 px-4">
                      <span className="font-mono text-purple-300 text-[11px]">
                        {rep.wallpaper_id.slice(0, 8)}...
                      </span>
                    </td>

                    <td className="py-3 px-4">
                      <span
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                          rep.status === 'RESOLVED'
                            ? 'bg-emerald-500/20 text-emerald-300'
                            : rep.status === 'REJECTED'
                            ? 'bg-slate-500/20 text-slate-400'
                            : 'bg-amber-500/20 text-amber-300 animate-pulse'
                        }`}
                      >
                        {rep.status}
                      </span>
                    </td>

                    <td className="py-3 px-4 text-slate-400 text-[11px]">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-500" />
                        <span>{new Date(rep.created_at).toLocaleString()}</span>
                      </div>
                    </td>

                    <td className="py-3 px-4 text-right">
                      {rep.status === 'PENDING' || rep.status === 'REVIEWING' ? (
                        <button
                          onClick={() => setResolvingReport(rep)}
                          className="px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs transition shadow-sm"
                        >
                          Resolve / Action
                        </button>
                      ) : (
                        <span className="text-[11px] text-slate-500 italic">Resolved</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        {totalPages > 1 && (
          <div className="p-4 border-t border-[#222230] flex items-center justify-between">
            <span className="text-xs text-slate-400">
              Page {page} of {totalPages}
            </span>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1 || isLoading}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="p-1.5 rounded-lg bg-[#181822] border border-[#2B2B3D] text-slate-400 hover:text-white disabled:opacity-40 transition"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                disabled={page >= totalPages || isLoading}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className="p-1.5 rounded-lg bg-[#181822] border border-[#2B2B3D] text-slate-400 hover:text-white disabled:opacity-40 transition"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Report Resolution Modal */}
      {resolvingReport && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#14141C] border border-[#2B2B3D] rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-[#222230] pb-3">
              <div className="flex items-center gap-2 text-purple-400 font-bold">
                <AlertTriangle className="w-5 h-5 text-amber-400" />
                <h3 className="text-base text-white">Resolve Content Report</h3>
              </div>
              <button
                onClick={() => setResolvingReport(null)}
                className="text-slate-400 hover:text-white p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-3 rounded-xl bg-[#181822] border border-[#232332] text-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Violation Reason:</span>
                <span className="font-bold text-white uppercase">{resolvingReport.reason}</span>
              </div>
              <div>
                <span className="text-slate-400 block mb-1">Details:</span>
                <p className="text-slate-300 bg-[#0E0E12] p-2 rounded-lg border border-[#22222E]">
                  {resolvingReport.description || 'No user comments'}
                </p>
              </div>
              <div className="text-slate-400 text-[10px] font-mono">
                Target Wallpaper ID: {resolvingReport.wallpaper_id}
              </div>
            </div>

            <div className="pt-2">
              <label className="flex items-start gap-2.5 cursor-pointer text-xs text-slate-300">
                <input
                  type="checkbox"
                  checked={unpublishWallpaper}
                  onChange={(e) => setUnpublishWallpaper(e.target.checked)}
                  className="w-4 h-4 mt-0.5 accent-rose-600 rounded"
                />
                <div>
                  <span className="font-semibold text-rose-300">
                    Immediately Unpublish Wallpaper
                  </span>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Hides the wallpaper from public discovery feed and search results.
                  </p>
                </div>
              </label>
            </div>

            <div className="flex items-center justify-between gap-3 pt-4 border-t border-[#222230]">
              <button
                type="button"
                disabled={isSubmitting}
                onClick={() => handleResolveAction('REJECTED', false)}
                className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center gap-1.5 transition"
              >
                <XCircle className="w-4 h-4 text-slate-400" />
                <span>Dismiss Report</span>
              </button>

              <button
                type="button"
                disabled={isSubmitting}
                onClick={() => handleResolveAction('RESOLVED', unpublishWallpaper)}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-emerald-600/30 transition"
              >
                {isSubmitting ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <CheckCircle2 className="w-4 h-4" />
                )}
                <span>Confirm Resolution</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
