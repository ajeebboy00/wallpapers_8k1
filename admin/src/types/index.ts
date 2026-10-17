export type UserRole = 'USER' | 'ADMIN' | 'SUPER_ADMIN';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  is_active: boolean;
  avatar_url?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: string;
  name: string;
  slug: string;
}

export interface CategorySummary {
  id: string;
  name: string;
  slug: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  cover_url?: string | null;
  icon_name?: string | null;
  order_index: number;
  is_active: boolean;
  wallpaper_count?: number;
  created_at?: string;
}

export interface Collection {
  id: string;
  title: string;
  slug: string;
  description?: string | null;
  cover_url?: string | null;
  is_featured: boolean;
  is_active: boolean;
  wallpaper_count?: number;
  created_at?: string;
}

export interface Wallpaper {
  id: string;
  title: string;
  slug: string;
  description?: string | null;
  original_url: string;
  image_url: string;
  thumbnail_url: string;
  preview_url: string;
  width: number;
  height: number;
  aspect_ratio: number;
  file_size: number;
  file_format: string;
  resolution: string;
  category_id: string;
  uploader_id?: string | null;
  view_count: number;
  download_count: number;
  favorite_count: number;
  share_count: number;
  is_featured: boolean;
  is_trending: boolean;
  is_daily: boolean;
  is_published: boolean;
  is_premium?: boolean;
  dominant_color?: string | null;
  color_palette?: string[] | null;
  perceptual_hash?: string | null;
  ai_tags?: string[] | null;
  ai_description?: string | null;
  is_ai_generated?: boolean;
  trending_score: number;
  created_at: string;
  updated_at: string;
  category?: CategorySummary | null;
  tags?: Tag[];
}

export type ReportReason = 'COPYRIGHT' | 'INAPPROPRIATE' | 'SPAM' | 'MISLEADING' | 'OTHER';
export type ReportStatus = 'PENDING' | 'REVIEWING' | 'RESOLVED' | 'REJECTED';

export interface Report {
  id: string;
  wallpaper_id: string;
  reporter_id: string;
  reason: ReportReason;
  description?: string | null;
  status: ReportStatus;
  reviewed_by?: string | null;
  reviewed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AdminDashboardMetrics {
  total_wallpapers: number;
  total_categories: number;
  total_collections: number;
  total_users: number;
  total_views: number;
  total_downloads: number;
  total_favorites: number;
  total_reports: number;
  storage_used_bytes: number;
  recent_wallpapers: Wallpaper[];
  pending_reports: Report[];
}

export interface AdminAnalyticsPoint {
  date: string;
  views: number;
  downloads: number;
  favorites: number;
}

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  meta: PaginationMeta;
  message?: string;
}

export interface StandardResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface SubscriptionMetrics {
  active_subscribers: number;
  mrr: number;
  total_revenue: number;
  total_ad_unlocks: number;
  plan_breakdown: Record<string, number>;
}

export interface SubscriberItem {
  id: string;
  user_id: string;
  plan: string;
  status: string;
  store: string;
  product_id?: string;
  order_id?: string;
  price_amount: number;
  currency: string;
  starts_at?: string;
  expires_at?: string;
  auto_renewing: boolean;
  created_at?: string;
}

export interface ColorStat {
  name: string;
  hex: string;
  count: number;
}

export interface SearchAnalytics {
  total_wallpapers: number;
  ai_indexed_wallpapers: number;
  color_distribution: ColorStat[];
  popular_searches: string[];
}

export interface SimilarWallpaperItem {
  wallpaper: Wallpaper;
  similarity_score: number;
  matching_factors: string[];
}


