import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Database, Server } from 'lucide-react';

export const AdminLayout: React.FC = () => {
  return (
    <div className="flex min-h-screen bg-[#0A0A0C] text-slate-100 font-sans antialiased selection:bg-purple-600 selection:text-white">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="h-16 border-b border-[#22222E] bg-[#121217]/70 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-30">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-xs font-medium text-emerald-400">System Healthy</span>
            </div>
            <span className="text-[#333344]">|</span>
            <div className="flex items-center gap-1.5 text-xs text-slate-400">
              <Database className="w-3.5 h-3.5 text-blue-400" />
              <span>PostgreSQL 18.4 Active</span>
            </div>
            <span className="text-[#333344]">|</span>
            <div className="flex items-center gap-1.5 text-xs text-slate-400">
              <Server className="w-3.5 h-3.5 text-purple-400" />
              <span>FastAPI Backend Live</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-[11px] font-mono text-slate-400 bg-[#1A1A24] px-2.5 py-1 rounded border border-[#2B2B3D]">
              Environment: Production
            </span>
          </div>
        </header>

        {/* Dynamic page content */}
        <main className="flex-1 p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
