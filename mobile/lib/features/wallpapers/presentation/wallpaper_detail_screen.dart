import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/network/api_client.dart';
import '../../../../core/services/download_service.dart';
import '../../../../core/services/wallpaper_setter_service.dart';
import '../../../../core/storage/secure_storage_service.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/widgets/state_views.dart';
import '../data/wallpaper_detail_remote_data_source.dart';
import '../data/wallpaper_detail_repository.dart';
import 'bloc/wallpaper_detail_cubit.dart';
import 'bloc/wallpaper_detail_state.dart';
import 'widgets/fullscreen_image_viewer.dart';
import 'widgets/wallpaper_action_bar.dart';
import 'widgets/wallpaper_info_sheet.dart';
import 'widgets/wallpaper_set_dialog.dart';

class WallpaperDetailScreen extends StatelessWidget {
  final String wallpaperId;

  const WallpaperDetailScreen({
    super.key,
    required this.wallpaperId,
  });

  @override
  Widget build(BuildContext context) {
    return BlocProvider<WallpaperDetailCubit>(
      create: (context) {
        final storage = SecureStorageService();
        final apiClient = ApiClient(storage: storage);
        final dataSource = WallpaperDetailRemoteDataSource(apiClient);
        final downloadService = DownloadService();
        final setterService = WallpaperSetterService();
        final repository = WallpaperDetailRepository(
          remoteDataSource: dataSource,
          downloadService: downloadService,
          wallpaperSetterService: setterService,
        );

        return WallpaperDetailCubit(repository)..loadWallpaper(wallpaperId);
      },
      child: const _WallpaperDetailContent(),
    );
  }
}

class _WallpaperDetailContent extends StatefulWidget {
  const _WallpaperDetailContent();

  @override
  State<_WallpaperDetailContent> createState() => _WallpaperDetailContentState();
}

class _WallpaperDetailContentState extends State<_WallpaperDetailContent> {
  bool _showChrome = true;

  void _toggleChrome() {
    setState(() {
      _showChrome = !_showChrome;
    });
  }

  void _onSetWallpaper(BuildContext context, WallpaperDetailCubit cubit) async {
    final destination = await WallpaperSetDialog.show(context);
    if (destination != null && mounted) {
      cubit.setWallpaper(destination);
    }
  }

  void _onOpenInfo(BuildContext context, WallpaperDetailLoaded state, WallpaperDetailCubit cubit) {
    WallpaperInfoSheet.show(
      context,
      wallpaper: state.wallpaper,
      relatedWallpapers: state.relatedWallpapers,
      onReport: (reason, desc) => cubit.reportWallpaper(reason, desc),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: BlocConsumer<WallpaperDetailCubit, WallpaperDetailState>(
        listener: (context, state) {
          if (state is WallpaperDetailLoaded) {
            if (state.infoMessage != null) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(state.infoMessage!),
                  backgroundColor: AppColors.primary,
                  behavior: SnackBarBehavior.floating,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
              );
              context.read<WallpaperDetailCubit>().clearNotification();
            } else if (state.errorMessage != null) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(state.errorMessage!),
                  backgroundColor: AppColors.error,
                  behavior: SnackBarBehavior.floating,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
              );
              context.read<WallpaperDetailCubit>().clearNotification();
            }
          }
        },
        builder: (context, state) {
          if (state is WallpaperDetailLoading) {
            return const Center(
              child: CircularProgressIndicator(color: AppColors.primary),
            );
          }

          if (state is WallpaperDetailError) {
            return ErrorView(
              message: state.message,
              onRetry: () {
                final id = GoRouterState.of(context).pathParameters['id'] ?? '';
                context.read<WallpaperDetailCubit>().loadWallpaper(id);
              },
            );
          }

          if (state is WallpaperDetailLoaded) {
            final cubit = context.read<WallpaperDetailCubit>();

            return Stack(
              children: [
                // 1. Fullscreen Interactive Image Viewer
                FullscreenImageViewer(
                  wallpaper: state.wallpaper,
                  onToggleChrome: _toggleChrome,
                ),

                // 2. Glassmorphic Top Bar
                AnimatedPositioned(
                  duration: const Duration(milliseconds: 250),
                  curve: Curves.easeInOut,
                  top: _showChrome ? MediaQuery.of(context).padding.top + 8 : -80,
                  left: 16,
                  right: 16,
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(24),
                    child: BackdropFilter(
                      filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: Colors.black.withOpacity(0.5),
                          borderRadius: BorderRadius.circular(24),
                          border: Border.all(color: Colors.white10),
                        ),
                        child: Row(
                          children: [
                            IconButton(
                              icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20, color: Colors.white),
                              onPressed: () {
                                if (context.canPop()) {
                                  context.pop();
                                } else {
                                  context.go('/');
                                }
                              },
                            ),
                            const Spacer(),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: AppColors.primary.withOpacity(0.2),
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(color: AppColors.primary, width: 0.8),
                              ),
                              child: Text(
                                state.wallpaper.resolution,
                                style: const TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                  color: AppColors.primary,
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            IconButton(
                              icon: const Icon(Icons.share_outlined, color: Colors.white, size: 22),
                              tooltip: 'Share Wallpaper',
                              onPressed: () => cubit.shareWallpaper(),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),

                // 3. Floating Bottom Action Bar
                AnimatedPositioned(
                  duration: const Duration(milliseconds: 250),
                  curve: Curves.easeInOut,
                  bottom: _showChrome ? MediaQuery.of(context).padding.bottom + 20 : -100,
                  left: 20,
                  right: 20,
                  child: Center(
                    child: WallpaperActionBar(
                      isFavorite: state.isFavorite,
                      favoriteCount: state.favoriteCount,
                      isDownloading: state.isDownloading,
                      downloadProgress: state.downloadProgress,
                      isSettingWallpaper: state.isSettingWallpaper,
                      onToggleFavorite: () => cubit.toggleFavorite(),
                      onDownload: () => cubit.downloadWallpaper(),
                      onSetWallpaper: () => _onSetWallpaper(context, cubit),
                      onOpenInfo: () => _onOpenInfo(context, state, cubit),
                    ),
                  ),
                ),
              ],
            );
          }

          return const SizedBox.shrink();
        },
      ),
    );
  }
}
