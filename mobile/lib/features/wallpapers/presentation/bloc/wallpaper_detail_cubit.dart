import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../../core/services/wallpaper_setter_service.dart';
import '../../data/wallpaper_detail_repository.dart';
import 'wallpaper_detail_state.dart';

class WallpaperDetailCubit extends Cubit<WallpaperDetailState> {
  final IWallpaperDetailRepository _repository;

  WallpaperDetailCubit(this._repository) : super(const WallpaperDetailInitial());

  Future<void> loadWallpaper(String identifier) async {
    emit(const WallpaperDetailLoading());

    try {
      final bundle = await _repository.getWallpaperDetail(identifier);
      emit(WallpaperDetailLoaded(
        wallpaper: bundle.wallpaper,
        relatedWallpapers: bundle.relatedWallpapers,
        isFavorite: bundle.isFavorite,
        favoriteCount: bundle.wallpaper.favoriteCount,
      ));
    } catch (e) {
      emit(WallpaperDetailError('Failed to load wallpaper: ${e.toString().replaceAll("Exception: ", "")}'));
    }
  }

  Future<void> toggleFavorite() async {
    final currentState = state;
    if (currentState is! WallpaperDetailLoaded) return;

    final prevFavorite = currentState.isFavorite;
    final prevCount = currentState.favoriteCount;

    // Optimistic UI update
    final nextFavorite = !prevFavorite;
    final nextCount = nextFavorite ? prevCount + 1 : (prevCount > 0 ? prevCount - 1 : 0);

    emit(currentState.copyWith(
      isFavorite: nextFavorite,
      favoriteCount: nextCount,
      clearInfoMessage: true,
      clearErrorMessage: true,
    ));

    try {
      final result = await _repository.toggleFavorite(currentState.wallpaper.id, prevFavorite);
      final confirmedFav = (result['is_favorite'] as bool?) ?? nextFavorite;
      final confirmedCount = (result['favorite_count'] as num?)?.toInt() ?? nextCount;

      emit(currentState.copyWith(
        isFavorite: confirmedFav,
        favoriteCount: confirmedCount,
      ));
    } catch (e) {
      // Revert on failure
      emit(currentState.copyWith(
        isFavorite: prevFavorite,
        favoriteCount: prevCount,
        errorMessage: 'Sign in to sync favorites to your account',
      ));
    }
  }

  Future<void> downloadWallpaper() async {
    final currentState = state;
    if (currentState is! WallpaperDetailLoaded || currentState.isDownloading) return;

    emit(currentState.copyWith(
      isDownloading: true,
      downloadProgress: 0.0,
      downloadSuccess: false,
      clearInfoMessage: true,
      clearErrorMessage: true,
    ));

    try {
      final path = await _repository.downloadWallpaper(
        currentState.wallpaper,
        onProgress: (received, total, percent) {
          if (state is WallpaperDetailLoaded) {
            emit((state as WallpaperDetailLoaded).copyWith(downloadProgress: percent));
          }
        },
      );

      emit((state as WallpaperDetailLoaded).copyWith(
        isDownloading: false,
        downloadProgress: 1.0,
        downloadSuccess: true,
        infoMessage: 'Downloaded 8K wallpaper to cache',
      ));
    } catch (e) {
      emit((state as WallpaperDetailLoaded).copyWith(
        isDownloading: false,
        downloadSuccess: false,
        errorMessage: 'Download failed: ${e.toString().replaceAll("Exception: ", "")}',
      ));
    }
  }

  Future<void> setWallpaper(WallpaperDestination destination) async {
    final currentState = state;
    if (currentState is! WallpaperDetailLoaded || currentState.isSettingWallpaper) return;

    emit(currentState.copyWith(
      isSettingWallpaper: true,
      setWallpaperSuccess: false,
      clearInfoMessage: true,
      clearErrorMessage: true,
    ));

    try {
      final success = await _repository.setWallpaper(
        wallpaper: currentState.wallpaper,
        destination: destination,
        onProgress: (received, total, percent) {
          if (state is WallpaperDetailLoaded) {
            emit((state as WallpaperDetailLoaded).copyWith(downloadProgress: percent));
          }
        },
      );

      if (success) {
        emit((state as WallpaperDetailLoaded).copyWith(
          isSettingWallpaper: false,
          setWallpaperSuccess: true,
          infoMessage: 'Wallpaper applied to ${destination.label}',
        ));
      } else {
        emit((state as WallpaperDetailLoaded).copyWith(
          isSettingWallpaper: false,
          errorMessage: 'Could not apply wallpaper to ${destination.label}',
        ));
      }
    } catch (e) {
      emit((state as WallpaperDetailLoaded).copyWith(
        isSettingWallpaper: false,
        errorMessage: 'Failed to set wallpaper: ${e.toString().replaceAll("Exception: ", "")}',
      ));
    }
  }

  Future<void> shareWallpaper() async {
    final currentState = state;
    if (currentState is! WallpaperDetailLoaded) return;
    try {
      await _repository.shareWallpaper(currentState.wallpaper);
    } catch (_) {}
  }

  Future<void> reportWallpaper(String reason, String? description) async {
    final currentState = state;
    if (currentState is! WallpaperDetailLoaded) return;
    try {
      await _repository.reportWallpaper(currentState.wallpaper.id, reason: reason, description: description);
      emit(currentState.copyWith(infoMessage: 'Thank you. Report submitted for review.'));
    } catch (e) {
      emit(currentState.copyWith(errorMessage: 'Failed to submit report. Please log in first.'));
    }
  }

  void clearNotification() {
    if (state is WallpaperDetailLoaded) {
      emit((state as WallpaperDetailLoaded).copyWith(
        clearInfoMessage: true,
        clearErrorMessage: true,
      ));
    }
  }
}
