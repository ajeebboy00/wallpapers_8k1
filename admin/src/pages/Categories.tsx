import React, { useEffect, useState } from 'react';
import { adminApi } from '../services/api';
import { Category } from '../types';
import {
  FolderTree,
  Plus,
  Edit2,
  Trash2,
  Eye,
  EyeOff,
  Loader2,
  AlertCircle,
  X,
} from 'lucide-react';

export const Categories: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    description: '',
    cover_url: '',
    order_index: 0,
    is_active: true,
  });
  const [submitting, setSubmitting] = useState(false);

  const fetchCategories = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await adminApi.listCategories();
      if (resp.success && resp.data) {
        setCategories(resp.data);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch categories');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  const openCreateModal = () => {
    setEditingCategory(null);
    setFormData({
      name: '',
      slug: '',
      description: '',
      cover_url: '',
      order_index: categories.length,
      is_active: true,
    });
    setIsModalOpen(true);
  };

  const openEditModal = (cat: Category) => {
    setEditingCategory(cat);
    setFormData({
      name: cat.name,
      slug: cat.slug,
      description: cat.description || '',
      cover_url: cat.cover_url || '',
      order_index: cat.order_index,
      is_active: cat.is_active,
    });
    setIsModalOpen(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (editingCategory) {
        const resp = await adminApi.updateCategory(editingCategory.id, formData);
        if (resp.success && resp.data) {
          setCategories((prev) =>
            prev.map((c) => (c.id === editingCategory.id ? resp.data : c))
          );
        }
      } else {
        const resp = await adminApi.createCategory(formData);
        if (resp.success && resp.data) {
          setCategories((prev) => [...prev, resp.data]);
        }
      }
      setIsModalOpen(false);
    } catch (err: any) {
      alert(err.message || 'Failed to save category');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete category "${name}"?`)) return;
    try {
      const resp = await adminApi.deleteCategory(id);
      if (resp.success) {
        setCategories((prev) => prev.filter((c) => c.id !== id));
      }
    } catch (err: any) {
      alert(err.message || 'Failed to delete category');
    }
  };

  const handleToggleActive = async (cat: Category) => {
    try {
      const resp = await adminApi.updateCategory(cat.id, { is_active: !cat.is_active });
      if (resp.success && resp.data) {
        setCategories((prev) => prev.map((c) => (c.id === cat.id ? resp.data : c)));
      }
    } catch (err: any) {
      alert(err.message || 'Failed to update category status');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Categories Management</h1>
          <p className="text-xs text-slate-400 mt-1">
            Organize wallpaper taxonomy, sort orders, and discovery cover artwork.
          </p>
        </div>
        <button
          onClick={openCreateModal}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow-lg shadow-purple-600/30 transition self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>New Category</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-xs text-rose-300">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Grid of Categories */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-24 gap-3">
          <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
          <p className="text-xs text-slate-400">Loading categories...</p>
        </div>
      ) : categories.length === 0 ? (
        <div className="py-20 text-center text-xs text-slate-500 bg-[#121218] rounded-2xl border border-[#222230]">
          No categories configured yet.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {categories.map((cat) => (
            <div
              key={cat.id}
              className="rounded-2xl bg-[#121218] border border-[#222230] overflow-hidden flex flex-col group hover:border-purple-500/30 transition"
            >
              <div className="h-32 bg-[#1A1A24] relative overflow-hidden">
                {cat.cover_url ? (
                  <img
                    src={cat.cover_url}
                    alt={cat.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition duration-300"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-slate-600">
                    <FolderTree className="w-10 h-10" />
                  </div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-[#121218] via-transparent to-transparent"></div>
                <div className="absolute top-3 right-3 flex items-center gap-2">
                  <span
                    className={`text-[10px] font-semibold px-2 py-0.5 rounded backdrop-blur-md ${
                      cat.is_active
                        ? 'bg-emerald-500/30 text-emerald-200 border border-emerald-500/40'
                        : 'bg-rose-500/30 text-rose-200 border border-rose-500/40'
                    }`}
                  >
                    {cat.is_active ? 'Active' : 'Hidden'}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-black/60 text-slate-300 border border-white/10">
                    Order #{cat.order_index}
                  </span>
                </div>
              </div>

              <div className="p-5 flex-1 flex flex-col justify-between">
                <div>
                  <h3 className="text-base font-bold text-white">{cat.name}</h3>
                  <p className="text-[11px] font-mono text-purple-400 mt-0.5">/{cat.slug}</p>
                  <p className="text-xs text-slate-400 mt-2 line-clamp-2">
                    {cat.description || 'No description provided'}
                  </p>
                </div>

                <div className="mt-5 pt-3 border-t border-[#1F1F2C] flex items-center justify-between">
                  <span className="text-xs text-slate-400">
                    {cat.wallpaper_count ?? 0} Wallpapers
                  </span>
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => handleToggleActive(cat)}
                      title={cat.is_active ? 'Deactivate' : 'Activate'}
                      className="p-1.5 rounded-lg border border-[#2B2B3D] text-slate-400 hover:text-white hover:bg-[#1E1E2B] transition"
                    >
                      {cat.is_active ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                    </button>
                    <button
                      onClick={() => openEditModal(cat)}
                      title="Edit Category"
                      className="p-1.5 rounded-lg border border-[#2B2B3D] text-slate-400 hover:text-purple-300 hover:bg-[#1E1E2B] transition"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => handleDelete(cat.id, cat.name)}
                      title="Delete Category"
                      className="p-1.5 rounded-lg border border-red-500/20 text-red-400 hover:bg-red-500/10 transition"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create / Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#14141C] border border-[#2B2B3D] rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-[#222230] pb-4">
              <h3 className="text-base font-bold text-white">
                {editingCategory ? 'Edit Category' : 'Create New Category'}
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-white p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSave} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1.5">
                    Category Name
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => {
                      const name = e.target.value;
                      setFormData((prev) => ({
                        ...prev,
                        name,
                        slug: prev.slug || name.toLowerCase().replace(/[^a-z0-9]+/g, '-'),
                      }));
                    }}
                    placeholder="e.g. Cyberpunk"
                    className="w-full bg-[#181822] border border-[#2B2B3D] focus:border-purple-500 rounded-xl px-3 py-2 text-xs text-white outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1.5">
                    Slug
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.slug}
                    onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                    placeholder="e.g. cyberpunk"
                    className="w-full bg-[#181822] border border-[#2B2B3D] focus:border-purple-500 rounded-xl px-3 py-2 text-xs text-white outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1.5">
                  Description
                </label>
                <textarea
                  rows={2}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Short taxonomy summary..."
                  className="w-full bg-[#181822] border border-[#2B2B3D] focus:border-purple-500 rounded-xl p-3 text-xs text-white outline-none resize-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1.5">
                  Cover Artwork URL
                </label>
                <input
                  type="url"
                  value={formData.cover_url}
                  onChange={(e) => setFormData({ ...formData, cover_url: e.target.value })}
                  placeholder="https://storage.wallpapers8k1.com/covers/..."
                  className="w-full bg-[#181822] border border-[#2B2B3D] focus:border-purple-500 rounded-xl px-3 py-2 text-xs text-white outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4 items-center">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1.5">
                    Display Order Index
                  </label>
                  <input
                    type="number"
                    value={formData.order_index}
                    onChange={(e) =>
                      setFormData({ ...formData, order_index: parseInt(e.target.value) || 0 })
                    }
                    className="w-full bg-[#181822] border border-[#2B2B3D] focus:border-purple-500 rounded-xl px-3 py-2 text-xs text-white outline-none"
                  />
                </div>
                <div className="pt-5">
                  <label className="inline-flex items-center gap-2 cursor-pointer text-xs text-slate-300">
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                      className="w-4 h-4 accent-purple-600 rounded"
                    />
                    <span>Active in Discovery Feed</span>
                  </label>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#222230]">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-[#1E1E2A] text-slate-300 hover:text-white text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold flex items-center gap-2"
                >
                  {submitting && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  <span>{editingCategory ? 'Update Category' : 'Create Category'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
