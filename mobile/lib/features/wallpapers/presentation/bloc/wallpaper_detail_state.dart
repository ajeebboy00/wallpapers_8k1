import 'package:equatable/equatable.dart';
import '../../../../shared/models/wallpaper_model.dart';

abstract class WallpaperDetailState extends Equatable {
  const WallpaperDetailState();

  @override
  List<Object?> get props => [];
}

class WallpaperDetailInitial extends WallpaperDetailState {
  const WallpaperDetailInitial();
}

class WallpaperDetailLoading extends WallpaperDetailState {
  const WallpaperDetailLoading();
}

class WallpaperDetailLoaded extends WallpaperDetailState {
  final WallpaperModel wallpaper;
  final List<WallpaperModel> relatedWallpapers;
  final bool isFavorite;
  final int favoriteCount;
  final bool isDownloading;
  final double downloadProgress;
  final bool downloadSuccess;
  final bool isSettingWallpaper;
  final bool setWallpaperSuccess;
  final String? infoMessage;
  final String? errorMessage;

  const WallpaperDetailLoaded({
    required this.wallpaper,
    this.relatedWallpapers = const [],
    this.isFavorite = false,
    required this.favoriteCount,
    this.isDownloading = false,
    this.downloadProgress = 0.0,
    this.downloadSuccess = false,
    this.isSettingWallpaper = false,
    this.setWallpaperSuccess = false,
    this.infoMessage,
    this.errorMessage,
  });

  WallpaperDetailLoaded copyWith({
    WallpaperModel? wallpaper,
    List<WallpaperModel>? relatedWallpapers,
    bool? isFavorite,
    int? favoriteCount,
    bool? isDownloading,
    double? downloadProgress,
    bool? downloadSuccess,
    bool? isSettingWallpaper,
    bool? setWallpaperSuccess,
    String? infoMessage,
    bool clearInfoMessage = false,
    String? errorMessage,
    bool clearErrorMessage = false,
  }) {
    return WallpaperDetailLoaded(
      wallpaper: wallpaper ?? this.wallpaper,
      relatedWallpapers: relatedWallpapers ?? this.relatedWallpapers,
      isFavorite: isFavorite ?? this.isFavorite,
      favoriteCount: favoriteCount ?? this.favoriteCount,
      isDownloading: isDownloading ?? this.isDownloading,
      downloadProgress: downloadProgress ?? this.downloadProgress,
      downloadSuccess: downloadSuccess ?? this.downloadSuccess,
      isSettingWallpaper: isSettingWallpaper ?? this.isSettingWallpaper,
      setWallpaperSuccess: setWallpaperSuccess ?? this.setWallpaperSuccess,
      infoMessage: clearInfoMessage ? null : (infoMessage ?? this.infoMessage),
      errorMessage: clearErrorMessage ? null : (errorMessage ?? this.errorMessage),
    );
  }

  @override
  List<Object?> get props => [
        wallpaper,
        relatedWallpapers,
        isFavorite,
        favoriteCount,
        isDownloading,
        downloadProgress,
        downloadSuccess,
        isSettingWallpaper,
        setWallpaperSuccess,
        infoMessage,
        errorMessage,
      ];
}

class WallpaperDetailError extends WallpaperDetailState {
  final String message;

  const WallpaperDetailError(this.message);

  @override
  List<Object?> get props => [message];
}
