import '../../../core/network/api_client.dart';
import '../../../shared/models/category_model.dart';
import '../../../shared/models/collection_model.dart';
import '../../../shared/models/wallpaper_model.dart';

abstract class IHomeRemoteDataSource {
  Future<WallpaperModel?> getDailyWallpaper();
  Future<List<WallpaperModel>> getFeaturedWallpapers({int limit = 6});
  Future<List<WallpaperModel>> getTrendingWallpapers({int limit = 10});
  Future<List<CategoryModel>> getCategories();
  Future<List<CollectionModel>> getFeaturedCollections({int limit = 5});
  Future<List<WallpaperModel>> getNewestWallpapers({int limit = 10});
}

class HomeRemoteDataSource implements IHomeRemoteDataSource {
  final ApiClient _client;

  HomeRemoteDataSource(this._client);

  @override
  Future<WallpaperModel?> getDailyWallpaper() async {
    try {
      final response = await _client.get('/wallpapers/daily');
      if (response.statusCode == 200 && response.data['data'] != null) {
        return WallpaperModel.fromJson(response.data['data'] as Map<String, dynamic>);
      }
      return null;
    } catch (_) {
      // If no daily wallpaper set yet, gracefully return null
      return null;
    }
  }

  @override
  Future<List<WallpaperModel>> getFeaturedWallpapers({int limit = 6}) async {
    final response = await _client.get(
      '/wallpapers',
      queryParameters: {
        'is_featured': true,
        'limit': limit,
        'sort': 'newest',
      },
    );
    final data = response.data['data'] as List<dynamic>? ?? [];
    return data.map((json) => WallpaperModel.fromJson(json as Map<String, dynamic>)).toList();
  }

  @override
  Future<List<WallpaperModel>> getTrendingWallpapers({int limit = 10}) async {
    final response = await _client.get(
      '/wallpapers',
      queryParameters: {
        'is_trending': true,
        'limit': limit,
        'sort': 'trending',
      },
    );
    final data = response.data['data'] as List<dynamic>? ?? [];
    return data.map((json) => WallpaperModel.fromJson(json as Map<String, dynamic>)).toList();
  }

  @override
  Future<List<CategoryModel>> getCategories() async {
    final response = await _client.get(
      '/categories',
      queryParameters: {'active_only': true},
    );
    final data = response.data['data'] as List<dynamic>? ?? [];
    return data.map((json) => CategoryModel.fromJson(json as Map<String, dynamic>)).toList();
  }

  @override
  Future<List<CollectionModel>> getFeaturedCollections({int limit = 5}) async {
    final response = await _client.get(
      '/collections',
      queryParameters: {
        'is_featured': true,
        'limit': limit,
      },
    );
    final data = response.data['data'] as List<dynamic>? ?? [];
    return data.map((json) => CollectionModel.fromJson(json as Map<String, dynamic>)).toList();
  }

  @override
  Future<List<WallpaperModel>> getNewestWallpapers({int limit = 10}) async {
    final response = await _client.get(
      '/wallpapers',
      queryParameters: {
        'limit': limit,
        'sort': 'newest',
      },
    );
    final data = response.data['data'] as List<dynamic>? ?? [];
    return data.map((json) => WallpaperModel.fromJson(json as Map<String, dynamic>)).toList();
  }
}
