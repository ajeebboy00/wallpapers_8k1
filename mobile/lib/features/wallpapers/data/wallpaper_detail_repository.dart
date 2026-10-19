import 'package:share_plus/share_plus.dart';
import 'package:wallpapers_8k1/core/services/download_service.dart';
import 'package:wallpapers_8k1/core/services/wallpaper_setter_service.dart';
import 'package:wallpapers_8k1/shared/models/wallpaper_model.dart';
import 'wallpaper_detail_remote_data_source.dart';

class WallpaperDetailBundle {
  final WallpaperModel wallpaper;
  final List<WallpaperModel> relatedWallpapers;
  final bool isFavorite;

  const WallpaperDetailBundle({
    required this.wallpaper,
    required this.relatedWallpapers,
    required this.isFavorite,
  });
}

abstract class IWallpaperDetailRepository {
  Future<WallpaperDetailBundle> getWallpaperDetail(String identifier);
  Future<Map<String, dynamic>> toggleFavorite(String identifier, bool currentStatus);
  Future<String> downloadWallpaper(
    WallpaperModel wallpaper, {
    DownloadProgressCallback? onProgress,
  });
  Future<bool> setWallpaper({
    required WallpaperModel wallpaper,
    required WallpaperDestination destination,
    DownloadProgressCallback? onProgress,
  });
  Future<void> shareWallpaper(WallpaperModel wallpaper);
  Future<void> reportWallpaper(String identifier, {required String reason, String? description});
}

class WallpaperDetailRepository implements IWallpaperDetailRepository {
  final WallpaperDetailRemoteDataSource _remoteDataSource;
  final IDownloadService _downloadService;
  final IWallpaperSetterService _wallpaperSetterService;

  WallpaperDetailRepository({
    required WallpaperDetailRemoteDataSource remoteDataSource,
    required IDownloadService downloadService,
    required IWallpaperSetterService wallpaperSetterService,
  })  : _remoteDataSource = remoteDataSource,
        _downloadService = downloadService,
        _wallpaperSetterService = wallpaperSetterService;

  @override
  Future<WallpaperDetailBundle> getWallpaperDetail(String identifier) async {
    // 1. Fetch wallpaper details
    final wallpaper = await _remoteDataSource.getWallpaperById(identifier);

    // 2. Concurrently fetch AI-similar wallpapers and check favorite status
    final similarFuture = _remoteDataSource.getSimilarWallpapers(wallpaper.id).catchError((_) => <WallpaperModel>[]);
    final favFuture = _remoteDataSource.checkFavorite(wallpaper.id);

    // 3. Fire-and-forget record view
    _remoteDataSource.recordView(wallpaper.id).catchError((_) => 0);

    final results = await Future.wait([similarFuture, favFuture]);
    List<WallpaperModel> related = results[0] as List<WallpaperModel>;
    if (related.isEmpty) {
      related = await _remoteDataSource.getRelatedWallpapers(wallpaper.id).catchError((_) => <WallpaperModel>[]);
    }
    final isFav = results[1] as bool;

    return WallpaperDetailBundle(
      wallpaper: wallpaper,
      relatedWallpapers: related,
      isFavorite: isFav,
    );
  }

  @override
  Future<Map<String, dynamic>> toggleFavorite(String identifier, bool currentStatus) async {
    if (currentStatus) {
      return await _remoteDataSource.removeFavorite(identifier);
    } else {
      return await _remoteDataSource.addFavorite(identifier);
    }
  }

  @override
  Future<String> downloadWallpaper(
    WallpaperModel wallpaper, {
    DownloadProgressCallback? onProgress,
  }) async {
    // Determine download URL (original 8K/4K or optimized fallback)
    final url = wallpaper.originalUrl.isNotEmpty ? wallpaper.originalUrl : wallpaper.imageUrl;
    final filename = 'w8k1_${wallpaper.id}.${wallpaper.fileFormat.isNotEmpty ? wallpaper.fileFormat : 'webp'}';

    final filePath = await _downloadService.downloadFile(
      url: url,
      filename: filename,
      onProgress: onProgress,
    );

    // Record download event on backend
    _remoteDataSource.recordDownload(wallpaper.id).catchError((_) => {});

    return filePath;
  }

  @override
  Future<bool> setWallpaper({
    required WallpaperModel wallpaper,
    required WallpaperDestination destination,
    DownloadProgressCallback? onProgress,
  }) async {
    final filePath = await downloadWallpaper(wallpaper, onProgress: onProgress);
    return await _wallpaperSetterService.setWallpaper(
      filePath: filePath,
      destination: destination,
    );
  }

  @override
  Future<void> shareWallpaper(WallpaperModel wallpaper) async {
    final title = wallpaper.title;
    final shareText = 'Check out this stunning 8K wallpaper "$title" on Wallpapers_8k1!\n${wallpaper.previewUrl}';

    await Share.share(shareText, subject: 'Wallpapers_8k1: $title');
    _remoteDataSource.recordShare(wallpaper.id, platform: 'native_share').catchError((_) => 0);
  }

  @override
  Future<void> reportWallpaper(
    String identifier, {
    required String reason,
    String? description,
  }) async {
    await _remoteDataSource.reportWallpaper(identifier, reason: reason, description: description);
  }
}
