import { create } from 'zustand';
import { adminApi } from '../services/api';
import { User } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  isSuperAdmin: () => boolean;
  isAdmin: () => boolean;
}

const getStoredUser = (): User | null => {
  try {
    const raw = localStorage.getItem('admin_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const useAuthStore = create<AuthState>((set, get) => ({
  user: getStoredUser(),
  token: localStorage.getItem('admin_access_token'),
  refreshToken: localStorage.getItem('admin_refresh_token'),
  isAuthenticated: !!localStorage.getItem('admin_access_token'),
  isLoading: false,
  error: null,

  login: async (email: string, password: string): Promise<boolean> => {
    set({ isLoading: true, error: null });
    try {
      const resp = await adminApi.login(email, password);
      if (!resp.success || !resp.data) {
        set({ isLoading: false, error: resp.message || 'Login failed' });
        return false;
      }

      const { access_token, refresh_token } = resp.data;
      localStorage.setItem('admin_access_token', access_token);
      localStorage.setItem('admin_refresh_token', refresh_token);

      // Fetch user profile to ensure admin role
      const meResp = await adminApi.getMe();
      if (!meResp.success || !meResp.data) {
        set({ isLoading: false, error: 'Could not fetch user profile' });
        get().logout();
        return false;
      }

      const user = meResp.data;
      if (user.role !== 'ADMIN' && user.role !== 'SUPER_ADMIN') {
        set({ isLoading: false, error: 'Access denied: Administrator privileges required.' });
        get().logout();
        return false;
      }

      localStorage.setItem('admin_user', JSON.stringify(user));
      set({
        user,
        token: access_token,
        refreshToken: refresh_token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
      return true;
    } catch (err: any) {
      const msg = err.response?.data?.message || err.message || 'Authentication error';
      set({ isLoading: false, error: msg });
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem('admin_access_token');
    localStorage.removeItem('admin_refresh_token');
    localStorage.removeItem('admin_user');
    set({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('admin_access_token');
    if (!token) {
      set({ isAuthenticated: false, user: null });
      return;
    }

    try {
      const meResp = await adminApi.getMe();
      if (meResp.success && meResp.data) {
        const user = meResp.data;
        if (user.role === 'ADMIN' || user.role === 'SUPER_ADMIN') {
          localStorage.setItem('admin_user', JSON.stringify(user));
          set({ user, isAuthenticated: true });
        } else {
          get().logout();
        }
      } else {
        get().logout();
      }
    } catch {
      get().logout();
    }
  },

  isSuperAdmin: () => {
    const user = get().user;
    return user?.role === 'SUPER_ADMIN';
  },

  isAdmin: () => {
    const user = get().user;
    return user?.role === 'ADMIN' || user?.role === 'SUPER_ADMIN';
  },
}));
