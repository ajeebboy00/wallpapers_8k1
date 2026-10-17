import axios, { AxiosError } from 'axios';
import {
  AdminAnalyticsPoint,
  AdminDashboardMetrics,
  AuthTokens,
  Category,
  Collection,
  PaginatedResponse,
  Report,
  ReportStatus,
  SearchAnalytics,
  SimilarWallpaperItem,
  StandardResponse,
  SubscriberItem,
  SubscriptionMetrics,
  User,
  UserRole,
  Wallpaper,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_access_token');
      localStorage.removeItem('admin_refresh_token');
      localStorage.removeItem('admin_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Admin API Endpoints
export const adminApi = {
  // Auth
  login: async (email: string, password: string): Promise<StandardResponse<AuthTokens>> => {
    const res = await apiClient.post<StandardResponse<AuthTokens>>('/auth/login', { email, password });
    return res.data;
  },

  getMe: async (): Promise<StandardResponse<User>> => {
    const res = await apiClient.get<StandardResponse<User>>('/users/me');
    return res.data;
  },

  // Dashboard Metrics
  getDashboardMetrics: async (): Promise<StandardResponse<AdminDashboardMetrics>> => {
    const res = await apiClient.get<StandardResponse<AdminDashboardMetrics>>('/admin/dashboard');
    return res.data;
  },

  // Wallpapers Management
  listWallpapers: async (params?: {
    page?: number;
    limit?: number;
    search?: string;
    is_published?: boolean;
    category_id?: string;
  }): Promise<PaginatedResponse<Wallpaper>> => {
    const res = await apiClient.get<PaginatedResponse<Wallpaper>>('/admin/wallpapers', { params });
    return res.data;
  },

  togglePublish: async (wallpaperId: string): Promise<StandardResponse<Wallpaper>> => {
    const res = await apiClient.patch<StandardResponse<Wallpaper>>(`/admin/wallpapers/${wallpaperId}/publish`);
    return res.data;
  },

  toggleFeatured: async (wallpaperId: string): Promise<StandardResponse<Wallpaper>> => {
    const res = await apiClient.patch<StandardResponse<Wallpaper>>(`/admin/wallpapers/${wallpaperId}/feature`);
    return res.data;
  },

  setDaily: async (wallpaperId: string): Promise<StandardResponse<Wallpaper>> => {
    const res = await apiClient.patch<StandardResponse<Wallpaper>>(`/admin/wallpapers/${wallpaperId}/daily`);
    return res.data;
  },

  deleteWallpaper: async (wallpaperId: string): Promise<StandardResponse<{ deleted: boolean }>> => {
    const res = await apiClient.delete<StandardResponse<{ deleted: boolean }>>(`/admin/wallpapers/${wallpaperId}`);
    return res.data;
  },

  // Categories
  listCategories: async (): Promise<StandardResponse<Category[]>> => {
    const res = await apiClient.get<StandardResponse<Category[]>>('/categories');
    return res.data;
  },

  createCategory: async (data: Partial<Category>): Promise<StandardResponse<Category>> => {
    const res = await apiClient.post<StandardResponse<Category>>('/categories', data);
    return res.data;
  },

  updateCategory: async (id: string, data: Partial<Category>): Promise<StandardResponse<Category>> => {
    const res = await apiClient.put<StandardResponse<Category>>(`/categories/${id}`, data);
    return res.data;
  },

  deleteCategory: async (id: string): Promise<StandardResponse<{ deleted: boolean }>> => {
    const res = await apiClient.delete<StandardResponse<{ deleted: boolean }>>(`/categories/${id}`);
    return res.data;
  },

  // Collections
  listCollections: async (): Promise<StandardResponse<Collection[]>> => {
    const res = await apiClient.get<StandardResponse<Collection[]>>('/collections');
    return res.data;
  },

  createCollection: async (data: Partial<Collection>): Promise<StandardResponse<Collection>> => {
    const res = await apiClient.post<StandardResponse<Collection>>('/collections', data);
    return res.data;
  },

  updateCollection: async (id: string, data: Partial<Collection>): Promise<StandardResponse<Collection>> => {
    const res = await apiClient.put<StandardResponse<Collection>>(`/collections/${id}`, data);
    return res.data;
  },

  deleteCollection: async (id: string): Promise<StandardResponse<{ deleted: boolean }>> => {
    const res = await apiClient.delete<StandardResponse<{ deleted: boolean }>>(`/collections/${id}`);
    return res.data;
  },

  // Users Management
  listUsers: async (params?: {
    page?: number;
    limit?: number;
    search?: string;
    role?: UserRole;
  }): Promise<PaginatedResponse<User>> => {
    const res = await apiClient.get<PaginatedResponse<User>>('/admin/users', { params });
    return res.data;
  },

  updateUserStatus: async (userId: string, isActive: boolean): Promise<StandardResponse<User>> => {
    const res = await apiClient.patch<StandardResponse<User>>(`/admin/users/${userId}/status`, { is_active: isActive });
    return res.data;
  },

  updateUserRole: async (userId: string, role: UserRole): Promise<StandardResponse<User>> => {
    const res = await apiClient.patch<StandardResponse<User>>(`/admin/users/${userId}/role`, { role });
    return res.data;
  },

  // Reports Moderation Queue
  listReports: async (params?: {
    page?: number;
    limit?: number;
    status?: ReportStatus;
  }): Promise<PaginatedResponse<Report>> => {
    const res = await apiClient.get<PaginatedResponse<Report>>('/admin/reports', { params });
    return res.data;
  },

  resolveReport: async (
    reportId: string,
    payload: { status: ReportStatus; unpublish_wallpaper: boolean }
  ): Promise<StandardResponse<Report>> => {
    const res = await apiClient.patch<StandardResponse<Report>>(`/admin/reports/${reportId}/resolve`, payload);
    return res.data;
  },

  // Analytics
  getAnalytics: async (days: number = 7): Promise<StandardResponse<AdminAnalyticsPoint[]>> => {
    const res = await apiClient.get<StandardResponse<AdminAnalyticsPoint[]>>('/admin/analytics', { params: { days } });
    return res.data;
  },

  // Push Notifications Broadcast
  broadcastNotification: async (payload: {
    title: string;
    message: string;
    type?: string;
    topic?: string;
    data?: Record<string, any>;
    save_to_inbox?: boolean;
  }): Promise<StandardResponse<{
    success: boolean;
    sent_count: number;
    failure_count: number;
    message: string;
    delivery_mode: string;
  }>> => {
    const res = await apiClient.post('/notifications/admin/broadcast', payload);
    return res.data;
  },

  triggerDailySpotlight: async (wallpaperId?: string): Promise<StandardResponse<{
    success: boolean;
    sent_count: number;
    failure_count: number;
    message: string;
    delivery_mode: string;
  }>> => {
    const res = await apiClient.post('/notifications/admin/daily-spotlight', null, {
      params: wallpaperId ? { wallpaper_id: wallpaperId } : undefined,
    });
    return res.data;
  },

  // Subscriptions & Monetization
  getSubscriptionMetrics: async (): Promise<StandardResponse<SubscriptionMetrics>> => {
    const res = await apiClient.get<StandardResponse<SubscriptionMetrics>>('/monetization/admin/metrics');
    return res.data;
  },

  getSubscribers: async (page: number = 1, limit: number = 20): Promise<PaginatedResponse<SubscriberItem>> => {
    const res = await apiClient.get<PaginatedResponse<SubscriberItem>>('/monetization/admin/subscribers', {
      params: { page, limit },
    });
    return res.data;
  },

  // AI Search, Vision Tagging & Similarity Engine
  getSearchAnalytics: async (): Promise<StandardResponse<SearchAnalytics>> => {
    const res = await apiClient.get<StandardResponse<SearchAnalytics>>('/search/analytics');
    return res.data;
  },

  batchAiTagging: async (payload: {
    limit?: number;
    force_reprocess?: boolean;
    wallpaper_id?: string;
  }): Promise<StandardResponse<{
    processed_count: number;
    updated_wallpapers: Wallpaper[];
    message: string;
  }>> => {
    const res = await apiClient.post('/search/ai/tag-batch', payload);
    return res.data;
  },

  getSimilarWallpapers: async (wallpaperId: string, limit: number = 10): Promise<StandardResponse<{
    source_wallpaper_id: string;
    similar: SimilarWallpaperItem[];
  }>> => {
    const res = await apiClient.get(`/search/similar/${wallpaperId}`, { params: { limit } });
    return res.data;
  },
};

