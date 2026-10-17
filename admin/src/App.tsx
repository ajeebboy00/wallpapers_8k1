import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { AdminLayout } from './components/layout/AdminLayout';

import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Wallpapers } from './pages/Wallpapers';
import { Categories } from './pages/Categories';
import { Collections } from './pages/Collections';
import { Users } from './pages/Users';
import { Reports } from './pages/Reports';
import { Analytics } from './pages/Analytics';
import { Notifications } from './pages/Notifications';
import { Subscriptions } from './pages/Subscriptions';
import { AiSearch } from './pages/AiSearch';

export default function App() {
  const { checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Login Route */}
        <Route path="/login" element={<Login />} />

        {/* Protected Admin Console Routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="wallpapers" element={<Wallpapers />} />
          <Route path="categories" element={<Categories />} />
          <Route path="collections" element={<Collections />} />
          <Route path="users" element={<Users />} />
          <Route path="reports" element={<Reports />} />
          <Route path="notifications" element={<Notifications />} />
          <Route path="subscriptions" element={<Subscriptions />} />
          <Route path="ai-search" element={<AiSearch />} />
          <Route path="analytics" element={<Analytics />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
