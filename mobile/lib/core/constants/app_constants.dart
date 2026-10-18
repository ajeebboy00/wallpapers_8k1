/// Application-wide constants for Wallpapers_8k1
class AppConstants {
  static const String appName = 'Wallpapers_8k1';
  static const String appShortBrand = 'W8K1';
  static const String appVersion = '1.0.0';

  // API Default Endpoints
  static const String defaultBaseUrl = 'http://10.0.2.2:8000/api/v1'; // Android emulator localhost alias
  static const Duration connectTimeout = Duration(seconds: 15);
  static const Duration receiveTimeout = Duration(seconds: 25);

  // Storage Keys
  static const String accessTokenKey = 'w8k1_access_token';
  static const String refreshTokenKey = 'w8k1_refresh_token';
  static const String userProfileKey = 'w8k1_user_profile';
  static const String themeModeKey = 'w8k1_theme_mode';
  static const String recentSearchesKey = 'w8k1_recent_searches';

  // Resolutions
  static const String res8K = '8K UHD';
  static const String res4K = '4K UHD';
  static const String res2K = '2K QHD';
  static const String resFHD = 'FHD 1080p';
}
