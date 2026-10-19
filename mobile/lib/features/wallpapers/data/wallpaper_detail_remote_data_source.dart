import 'package:wallpapers_8k1/core/network/api_client.dart';
import 'package:wallpapers_8k1/shared/models/wallpaper_model.dart';

class WallpaperDetailRemoteDataSource {
  final ApiClient _apiClient;

  WallpaperDetailRemoteDataSource(this._apiClient);

  Future<WallpaperModel> getWallpaperById(String identifier) async {
    final response = await _apiClient.get('/wallpapers/$identifier');
    return WallpaperModel.fromJson(response.data['data'] as Map<String, dynamic>);
  }

  Future<List<WallpaperModel>> getRelatedWallpapers(String identifier, {int limit = 8}) async {
    final response = await _apiClient.get(
      '/wallpapers/$identifier/related',
      queryParameters: {'limit': limit},
    );
    final list = response.data['data'] as List<dynamic>? ?? [];
    return list.map((e) => WallpaperModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<WallpaperModel>> getSimilarWallpapers(String identifier, {int limit = 8}) async {
    final response = await _apiClient.get(
      '/wallpapers/$identifier/similar',
      queryParameters: {'limit': limit},
    );
    final list = response.data['data'] as List<dynamic>? ?? [];
    return list.map((e) => WallpaperModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<int> recordView(String identifier, {String? sessionIdentifier}) async {
    final response = await _apiClient.post(
      '/wallpapers/$identifier/view',
      data: sessionIdentifier != null ? {'session_identifier': sessionIdentifier} : null,
    );
    return (response.data['data']['view_count'] as num?)?.toInt() ?? 0;
  }

  Future<Map<String, dynamic>> addFavorite(String identifier) async {
    final response = await _apiClient.post('/wallpapers/$identifier/favorite');
    return response.data['data'] as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> removeFavorite(String identifier) async {
    final response = await _apiClient.delete('/wallpapers/$identifier/favorite');
    return response.data['data'] as Map<String, dynamic>;
  }

  Future<bool> checkFavorite(String identifier) async {
    try {
      final response = await _apiClient.get('/wallpapers/$identifier/favorite');
      return (response.data['data']['is_favorite'] as bool?) ?? false;
    } catch (_) {
      return false;
    }
  }

  Future<Map<String, dynamic>> recordDownload(String identifier) async {
    final response = await _apiClient.post('/wallpapers/$identifier/download');
    return response.data['data'] as Map<String, dynamic>;
  }

  Future<int> recordShare(String identifier, {String? platform}) async {
    final response = await _apiClient.post(
      '/wallpapers/$identifier/share',
      data: {'platform': platform ?? 'native'},
    );
    return (response.data['data']['share_count'] as num?)?.toInt() ?? 0;
  }

  Future<void> reportWallpaper(
    String identifier, {
    required String reason,
    String? description,
  }) async {
    await _apiClient.post(
      '/wallpapers/$identifier/report',
      data: {
        'reason': reason,
        'description': description,
      },
    );
  }
}
