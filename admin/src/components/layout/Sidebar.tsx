import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Image as ImageIcon,
  FolderTree,
  Layers,
  Users,
  AlertTriangle,
  BarChart3,
  LogOut,
  ShieldAlert,
  Sparkles,
  Bell,
  CreditCard,
} from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuthStore();

  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/wallpapers', label: 'Wallpapers', icon: ImageIcon },
    { to: '/categories', label: 'Categories', icon: FolderTree },
    { to: '/collections', label: 'Collections', icon: Layers },
    { to: '/users', label: 'User Accounts', icon: Users },
    { to: '/reports', label: 'Content Reports', icon: AlertTriangle },
    { to: '/notifications', label: 'Push Alerts', icon: Bell },
    { to: '/subscriptions', label: 'Subscriptions', icon: CreditCard },
    { to: '/ai-search', label: 'AI Search & Vision', icon: Sparkles },
    { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  ];

  return (
    <aside className="w-64 border-r border-[#22222E] bg-[#121217] flex flex-col min-h-screen select-none">
      {/* Brand Header */}
      <div className="p-6 border-b border-[#22222E] flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-400" />
            <h1 className="text-lg font-bold tracking-wider text-white">W8K1</h1>
          </div>
          <p className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold mt-0.5">
            Admin Control Panel
          </p>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-950/60 text-purple-400 border border-purple-800/40">
          v1.0
        </span>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4 space-y-1.5 text-sm font-medium overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                  isActive
                    ? 'bg-purple-600/20 text-purple-300 border border-purple-500/30 shadow-sm shadow-purple-900/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-[#1A1A22]'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* User Footer Profile & Logout */}
      <div className="p-4 border-t border-[#22222E] bg-[#0E0E12]">
        <div className="flex items-center justify-between gap-3 mb-3">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-purple-600/30 border border-purple-500/40 flex items-center justify-center text-xs font-bold text-purple-200 uppercase shrink-0">
              {user?.name ? user.name[0] : 'A'}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-slate-200 truncate">{user?.name || 'Admin'}</p>
              <p className="text-[10px] text-slate-400 truncate">{user?.email}</p>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span
            className={`inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded ${
              user?.role === 'SUPER_ADMIN'
                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                : 'bg-purple-500/10 text-purple-300 border border-purple-500/30'
            }`}
          >
            {user?.role === 'SUPER_ADMIN' && <ShieldAlert className="w-2.5 h-2.5" />}
            {user?.role || 'ADMIN'}
          </span>

          <button
            onClick={logout}
            title="Log Out"
            className="flex items-center gap-1 px-2.5 py-1 text-xs text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 rounded transition"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Exit</span>
          </button>
        </div>
      </div>
    </aside>
  );
};
