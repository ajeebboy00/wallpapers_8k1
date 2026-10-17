import React, { useEffect, useState } from 'react';
import { adminApi } from '../services/api';
import { Category, Wallpaper } from '../types';
import {
  Search,
  Eye,
  EyeOff,
  Star,
  Sparkles,
  Trash2,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Loader2,
  AlertCircle,
} from 'lucide-react';

export const Wallpapers: React.FC = () => {
  const [wallpapers, setWallpapers] = useState<Wallpaper[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const limit = 15;

  const [search, setSearch] = useState('');
  const [categoryId, setCategoryId] = useState<string>('');
  const [publishedFilter, setPublishedFilter] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Delete modal state
  const [deleteTarget, setDeleteTarget] = useState<Wallpaper | null>(null);

  const fetchWallpapers = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const is_published =
        publishedFilter === 'published'
          ? true
          : publishedFilter === 'unpublished'
          ? false
          : undefined;

      const resp = await adminApi.listWallpapers({
        page,
        limit,
        search: search.trim() || undefined,
        category_id: categoryId || undefined,
        is_published,
      });

      if (resp.success) {
        setWallpapers(resp.data);
        setTotal(resp.meta.total);
        setTotalPages(resp.meta.total_pages);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch wallpapers');
    } finally {
      setIsLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const resp = await adminApi.listCategories();
      if (resp.success && resp.data) {
        setCategories(resp.data);
      }
    } catch (err) {
      console.error('Failed to load categories', err);
    }
  };

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    fetchWallpapers();
  }, [page, categoryId, publishedFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchWallpapers();
  };

  const handleTogglePublish = async (wp: Wallpaper) => {
    setActionLoadingId(wp.id);
    try {
      const res = await adminApi.togglePublish(wp.id);
      if (res.success && res.data) {
        setWallpapers((prev) => prev.map((item) => (item.id === wp.id ? res.data : item)));
      }
    } catch (err: any) {
      alert(err.message || 'Failed to toggle publish status');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleToggleFeatured = async (wp: Wallpaper) => {
    setActionLoadingId(wp.id);
    try {
      const res = await adminApi.toggleFeatured(wp.id);
      if (res.success && res.data) {
        setWallpapers((prev) => prev.map((item) => (item.id === wp.id ? res.data : item)));
      }
    } catch (err: any) {
      alert(err.message || 'Failed to toggle featured status');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleSetDaily = async (wp: Wallpaper) => {
    setActionLoadingId(wp.id);
    try {
      const res = await adminApi.setDaily(wp.id);
      if (res.success && res.data) {
        setWallpapers((prev) => prev.map((item) => (item.id === wp.id ? res.data : item)));
      }
    } catch (err: any) {
      alert(err.message || 'Failed to set daily spotlight');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setActionLoadingId(deleteTarget.id);
    try {
      const res = await adminApi.deleteWallpaper(deleteTarget.id);
      if (res.success) {
        setWallpapers((prev) => prev.filter((item) => item.id !== deleteTarget.id));
        setTotal((prev) => Math.max(0, prev - 1));
        setDeleteTarget(null);
      }
    } catch (err: any) {
      alert(err.message || 'Failed to delete wallpaper');
    } finally {
      setActionLoadingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Wallpaper Catalog</h1>
          <p className="text-xs text-slate-400 mt-1">
            Manage 8K wallpaper assets, visibility, spotlights, and category assignments.
          </p>
        </div>
        <div className="text-xs text-slate-400">
          Total items: <span className="font-bold text-white">{total}</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-[#121218] border border-[#222230] flex flex-wrap items-center gap-3">
        <form onSubmit={handleSearchSubmit} className="flex-1 min-w-[240px] relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by title or slug..."
            className="w-full bg-[#181822] border border-[#2B2B3D] focus:border-purple-500 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 outline-none"
          />
        </form>

        {/* Category selector */}
        <select
          value={categoryId}
          onChange={(e) => {
            setCategoryId(e.target.value);
            setPage(1);
          }}
          className="bg-[#181822] border border-[#2B2B3D] rounded-xl px-3 py-2 text-xs text-white outline-none cursor-pointer"
        >
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>

        {/* Published Filter */}
        <select
          value={publishedFilter}
          onChange={(e) => {
            setPublishedFilter(e.target.value);
            setPage(1);
          }}
          className="bg-[#181822] border border-[#2B2B3D] rounded-xl px-3 py-2 text-xs text-white outline-none cursor-pointer"
        >
          <option value="all">All Statuses</option>
          <option value="published">Published</option>
          <option value="unpublished">Unpublished</option>
        </select>

        <button
          onClick={() => {
            setPage(1);
            fetchWallpapers();
          }}
          className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold transition"
        >
          Filter
        </button>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-xs text-rose-300">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Data Table */}
      <div className="rounded-2xl bg-[#121218] border border-[#222230] overflow-hidden">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-24 gap-3">
            <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
            <p className="text-xs text-slate-400">Loading catalog...</p>
          </div>
        ) : wallpapers.length === 0 ? (
          <div className="py-20 text-center text-xs text-slate-500">
            No wallpapers found matching the search criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#161622] text-slate-400 uppercase tracking-wider font-semibold border-b border-[#222230]">
                <tr>
                  <th className="py-3 px-4">Preview</th>
                  <th className="py-3 px-4">Title & Details</th>
                  <th className="py-3 px-4">Resolution</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Engagement</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Moderation Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1E1E2C] text-slate-300">
                {wallpapers.map((wp) => {
                  const isOperating = actionLoadingId === wp.id;
                  return (
                    <tr key={wp.id} className="hover:bg-[#161622]/60 transition">
                      <td className="py-3 px-4">
                        <img
                          src={wp.thumbnail_url}
                          alt={wp.title}
                          className="w-12 h-16 object-cover rounded-lg bg-black border border-[#2B2B3D]"
                        />
                      </td>
                      <td className="py-3 px-4 max-w-xs">
                        <p className="font-semibold text-white truncate">{wp.title}</p>
                        <p className="text-[10px] text-slate-500 font-mono mt-0.5">{wp.slug}</p>
                        <p className="text-[10px] text-slate-400 mt-1">
                          {wp.width} x {wp.height} px • {wp.file_format.toUpperCase()}
                        </p>
                      </td>
                      <td className="py-3 px-4">
                        <span className="font-bold px-2 py-0.5 rounded bg-purple-500/20 text-purple-300">
                          {wp.resolution}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-slate-300 font-medium">
                          {wp.category?.name || 'Unassigned'}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="text-[11px] space-y-0.5">
                          <p className="text-blue-400">{wp.view_count.toLocaleString()} views</p>
                          <p className="text-amber-400">{wp.download_count.toLocaleString()} dl</p>
                          <p className="text-rose-400">{wp.favorite_count.toLocaleString()} favs</p>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex flex-col gap-1 items-start">
                          <span
                            className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                              wp.is_published
                                ? 'bg-emerald-500/20 text-emerald-300'
                                : 'bg-rose-500/20 text-rose-300'
                            }`}
                          >
                            {wp.is_published ? 'Published' : 'Hidden'}
                          </span>
                          {wp.is_featured && (
                            <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300">
                              Featured
                            </span>
                          )}
                          {wp.is_daily && (
                            <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
                              Daily
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {/* Toggle Publish */}
                          <button
                            onClick={() => handleTogglePublish(wp)}
                            disabled={isOperating}
                            title={wp.is_published ? 'Unpublish' : 'Publish'}
                            className={`p-1.5 rounded-lg border transition ${
                              wp.is_published
                                ? 'border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10'
                                : 'border-rose-500/30 text-rose-400 hover:bg-rose-500/10'
                            }`}
                          >
                            {wp.is_published ? (
                              <Eye className="w-3.5 h-3.5" />
                            ) : (
                              <EyeOff className="w-3.5 h-3.5" />
                            )}
                          </button>

                          {/* Toggle Featured */}
                          <button
                            onClick={() => handleToggleFeatured(wp)}
                            disabled={isOperating}
                            title={wp.is_featured ? 'Remove from Featured' : 'Mark as Featured'}
                            className={`p-1.5 rounded-lg border transition ${
                              wp.is_featured
                                ? 'bg-amber-500/20 border-amber-500/40 text-amber-300'
                                : 'border-[#2B2B3D] text-slate-400 hover:text-amber-400 hover:bg-amber-500/10'
                            }`}
                          >
                            <Star className="w-3.5 h-3.5" />
                          </button>

                          {/* Set Daily Spotlight */}
                          <button
                            onClick={() => handleSetDaily(wp)}
                            disabled={isOperating}
                            title="Set as Daily Spotlight"
                            className={`p-1.5 rounded-lg border transition ${
                              wp.is_daily
                                ? 'bg-purple-500/20 border-purple-500/40 text-purple-300'
                                : 'border-[#2B2B3D] text-slate-400 hover:text-purple-400 hover:bg-purple-500/10'
                            }`}
                          >
                            <Sparkles className="w-3.5 h-3.5" />
                          </button>

                          {/* View Original */}
                          <a
                            href={wp.original_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            title="View Full Resolution Asset"
                            className="p-1.5 rounded-lg border border-[#2B2B3D] text-slate-400 hover:text-white hover:bg-[#1E1E2B] transition"
                          >
                            <ExternalLink className="w-3.5 h-3.5" />
                          </a>

                          {/* Delete */}
                          <button
                            onClick={() => setDeleteTarget(wp)}
                            disabled={isOperating}
                            title="Delete Wallpaper"
                            className="p-1.5 rounded-lg border border-red-500/20 text-red-400 hover:bg-red-500/10 transition"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
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

      {/* Delete Confirmation Modal */}
      {deleteTarget && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#14141C] border border-red-500/30 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center gap-3 text-rose-400">
              <Trash2 className="w-6 h-6" />
              <h3 className="text-base font-bold text-white">Confirm Asset Deletion</h3>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Are you sure you want to permanently delete{' '}
              <strong className="text-white">"{deleteTarget.title}"</strong>? This will remove all
              8K, 4K, preview, and thumbnail records permanently.
            </p>
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setDeleteTarget(null)}
                className="px-4 py-2 rounded-xl bg-[#1E1E2A] text-slate-300 hover:text-white text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white text-xs font-semibold"
              >
                Confirm Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
