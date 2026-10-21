import '../../../core/data/mock_feed_data.dart';
import '../../../shared/models/category_model.dart';
import '../../../shared/models/collection_model.dart';
import '../../../shared/models/wallpaper_model.dart';
import 'home_remote_data_source.dart';

class HomeBundle {
  final WallpaperModel? dailyWallpaper;
  final List<WallpaperModel> featuredWallpapers;
  final List<WallpaperModel> trendingWallpapers;
  final List<CategoryModel> categories;
  final List<CollectionModel> featuredCollections;
  final List<WallpaperModel> newestWallpapers;

  const HomeBundle({
    this.dailyWallpaper,
    this.featuredWallpapers = const [],
    this.trendingWallpapers = const [],
    this.categories = const [],
    this.featuredCollections = const [],
    this.newestWallpapers = const [],
  });
}

class HomeRepository {
  final IHomeRemoteDataSource _remoteDataSource;

  HomeRepository(this._remoteDataSource);

  Future<HomeBundle> getHomeFeed() async {
    try {
      // Concurrently fetch all home feed sections in parallel for optimal load times
      final results = await Future.wait([
        _remoteDataSource.getDailyWallpaper(),
        _remoteDataSource.getFeaturedWallpapers(),
        _remoteDataSource.getTrendingWallpapers(),
        _remoteDataSource.getCategories(),
        _remoteDataSource.getFeaturedCollections(),
        _remoteDataSource.getNewestWallpapers(),
      ]);

      return HomeBundle(
        dailyWallpaper: results[0] as WallpaperModel?,
        featuredWallpapers: results[1] as List<WallpaperModel>,
        trendingWallpapers: results[2] as List<WallpaperModel>,
        categories: results[3] as List<CategoryModel>,
        featuredCollections: results[4] as List<CollectionModel>,
        newestWallpapers: results[5] as List<WallpaperModel>,
      );
    } catch (_) {
      // Bulletproof fallback: return built-in 8K feed so the app ALWAYS opens and renders immediately
      return MockFeedData.getHomeBundle();
    }
  }
}
