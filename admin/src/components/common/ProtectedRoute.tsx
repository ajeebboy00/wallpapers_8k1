import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireSuperAdmin?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireSuperAdmin = false,
}) => {
  const { isAuthenticated, user, isSuperAdmin } = useAuthStore();
  const location = useLocation();

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requireSuperAdmin && !isSuperAdmin()) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-8">
        <h2 className="text-2xl font-bold text-rose-500 mb-2">Access Denied</h2>
        <p className="text-slate-400 max-w-md">
          This section requires Super Administrator privileges. Your current role is{' '}
          <span className="text-purple-400 font-semibold">{user.role}</span>.
        </p>
      </div>
    );
  }

  return <>{children}</>;
};
