import React, { useEffect, useState } from 'react';
import { adminApi } from '../services/api';
import { useAuthStore } from '../store/authStore';
import { User, UserRole } from '../types';
import {
  Search,
  ShieldCheck,
  ShieldAlert,
  UserX,
  UserCheck,
  ChevronLeft,
  ChevronRight,
  Loader2,
  AlertCircle,
  Clock,
} from 'lucide-react';

export const Users: React.FC = () => {
  const { user: currentAdmin, isSuperAdmin } = useAuthStore();
  const [users, setUsers] = useState<User[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const limit = 15;

  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await adminApi.listUsers({
        page,
        limit,
        search: search.trim() || undefined,
        role: (roleFilter as UserRole) || undefined,
      });

      if (resp.success) {
        setUsers(resp.data);
        setTotal(resp.meta.total);
        setTotalPages(resp.meta.total_pages);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch user accounts');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [page, roleFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchUsers();
  };

  const handleToggleStatus = async (user: User) => {
    setActionLoadingId(user.id);
    try {
      const resp = await adminApi.updateUserStatus(user.id, !user.is_active);
      if (resp.success && resp.data) {
        setUsers((prev) => prev.map((u) => (u.id === user.id ? resp.data : u)));
      }
    } catch (err: any) {
      alert(err.message || 'Failed to update user status');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleChangeRole = async (userId: string, newRole: UserRole) => {
    if (!isSuperAdmin()) {
      alert('Only Super Administrators can change user roles.');
      return;
    }
    setActionLoadingId(userId);
    try {
      const resp = await adminApi.updateUserRole(userId, newRole);
      if (resp.success && resp.data) {
        setUsers((prev) => prev.map((u) => (u.id === userId ? resp.data : u)));
      }
    } catch (err: any) {
      alert(err.message || 'Failed to change role');
    } finally {
      setActionLoadingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">User Accounts</h1>
          <p className="text-xs text-slate-400 mt-1">
            Manage user identity, account active status, and RBAC permissions.
          </p>
        </div>
        <div className="text-xs text-slate-400">
          Total accounts: <span className="font-bold text-white">{total}</span>
        </div>
      </div>

      {/* Filters */}
      <div className="p-4 rounded-2xl bg-[#121218] border border-[#222230] flex flex-wrap items-center gap-3">
        <form onSubmit={handleSearchSubmit} className="flex-1 min-w-[240px] relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name or email address..."
            className="w-full bg-[#181822] border border-[#2B2B3D] focus:border-purple-500 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 outline-none"
          />
        </form>

        <select
          value={roleFilter}
          onChange={(e) => {
            setRoleFilter(e.target.value);
            setPage(1);
          }}
          className="bg-[#181822] border border-[#2B2B3D] rounded-xl px-3 py-2 text-xs text-white outline-none cursor-pointer"
        >
          <option value="">All Roles</option>
          <option value="USER">USER</option>
          <option value="ADMIN">ADMIN</option>
          <option value="SUPER_ADMIN">SUPER_ADMIN</option>
        </select>

        <button
          onClick={() => {
            setPage(1);
            fetchUsers();
          }}
          className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold transition"
        >
          Search
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-xs text-rose-300">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* User Table */}
      <div className="rounded-2xl bg-[#121218] border border-[#222230] overflow-hidden">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-24 gap-3">
            <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
            <p className="text-xs text-slate-400">Loading user accounts...</p>
          </div>
        ) : users.length === 0 ? (
          <div className="py-20 text-center text-xs text-slate-500">No users found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#161622] text-slate-400 uppercase tracking-wider font-semibold border-b border-[#222230]">
                <tr>
                  <th className="py-3 px-4">User</th>
                  <th className="py-3 px-4">Email</th>
                  <th className="py-3 px-4">Role</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Registered Date</th>
                  <th className="py-3 px-4 text-right">Account Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1E1E2C] text-slate-300">
                {users.map((u) => {
                  const isOperating = actionLoadingId === u.id;
                  const isSelf = currentAdmin?.id === u.id;

                  return (
                    <tr key={u.id} className="hover:bg-[#161622]/60 transition">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-purple-600/20 border border-purple-500/30 flex items-center justify-center font-bold text-purple-300 uppercase shrink-0">
                            {u.name ? u.name[0] : 'U'}
                          </div>
                          <div>
                            <p className="font-semibold text-white">
                              {u.name} {isSelf && <span className="text-[10px] text-purple-400 font-normal">(You)</span>}
                            </p>
                            <p className="text-[10px] font-mono text-slate-500">{u.id.slice(0, 8)}...</p>
                          </div>
                        </div>
                      </td>

                      <td className="py-3 px-4 text-slate-300 font-mono text-[11px]">{u.email}</td>

                      <td className="py-3 px-4">
                        {isSuperAdmin() && !isSelf ? (
                          <select
                            value={u.role}
                            onChange={(e) => handleChangeRole(u.id, e.target.value as UserRole)}
                            disabled={isOperating}
                            className="bg-[#181822] border border-[#2B2B3D] rounded-lg px-2 py-1 text-xs text-white outline-none cursor-pointer font-semibold"
                          >
                            <option value="USER">USER</option>
                            <option value="ADMIN">ADMIN</option>
                            <option value="SUPER_ADMIN">SUPER_ADMIN</option>
                          </select>
                        ) : (
                          <span
                            className={`inline-flex items-center gap-1 font-semibold px-2 py-0.5 rounded text-[10px] ${
                              u.role === 'SUPER_ADMIN'
                                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                                : u.role === 'ADMIN'
                                ? 'bg-purple-500/10 text-purple-300 border border-purple-500/30'
                                : 'bg-slate-500/10 text-slate-300 border border-slate-500/20'
                            }`}
                          >
                            {u.role === 'SUPER_ADMIN' && <ShieldAlert className="w-2.5 h-2.5" />}
                            {u.role === 'ADMIN' && <ShieldCheck className="w-2.5 h-2.5" />}
                            {u.role}
                          </span>
                        )}
                      </td>

                      <td className="py-3 px-4">
                        <span
                          className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                            u.is_active
                              ? 'bg-emerald-500/20 text-emerald-300'
                              : 'bg-rose-500/20 text-rose-300'
                          }`}
                        >
                          {u.is_active ? 'Active' : 'Deactivated'}
                        </span>
                      </td>

                      <td className="py-3 px-4 text-slate-400 text-[11px]">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3 text-slate-500" />
                          <span>{new Date(u.created_at).toLocaleDateString()}</span>
                        </div>
                      </td>

                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleToggleStatus(u)}
                            disabled={isOperating || isSelf}
                            title={u.is_active ? 'Deactivate User' : 'Reactivate User'}
                            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-medium transition disabled:opacity-40 ${
                              u.is_active
                                ? 'border-rose-500/30 text-rose-400 hover:bg-rose-500/10'
                                : 'border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10'
                            }`}
                          >
                            {u.is_active ? (
                              <>
                                <UserX className="w-3.5 h-3.5" />
                                <span>Deactivate</span>
                              </>
                            ) : (
                              <>
                                <UserCheck className="w-3.5 h-3.5" />
                                <span>Activate</span>
                              </>
                            )}
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
    </div>
  );
};
