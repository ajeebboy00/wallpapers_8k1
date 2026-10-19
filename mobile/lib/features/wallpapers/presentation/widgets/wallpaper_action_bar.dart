import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:wallpapers_8k1/core/theme/app_colors.dart';

class WallpaperActionBar extends StatelessWidget {
  final bool isFavorite;
  final int favoriteCount;
  final bool isDownloading;
  final double downloadProgress;
  final bool isSettingWallpaper;
  final VoidCallback onToggleFavorite;
  final VoidCallback onDownload;
  final VoidCallback onSetWallpaper;
  final VoidCallback onOpenInfo;

  const WallpaperActionBar({
    super.key,
    required this.isFavorite,
    required this.favoriteCount,
    required this.isDownloading,
    required this.downloadProgress,
    required this.isSettingWallpaper,
    required this.onToggleFavorite,
    required this.onDownload,
    required this.onSetWallpaper,
    required this.onOpenInfo,
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(30),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 16, sigmaY: 16),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.65),
            borderRadius: BorderRadius.circular(30),
            border: Border.all(color: Colors.white12),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              // 1. Favorite Button
              IconButton(
                icon: AnimatedSwitcher(
                  duration: const Duration(milliseconds: 200),
                  transitionBuilder: (child, anim) => ScaleTransition(scale: anim, child: child),
                  child: Icon(
                    isFavorite ? Icons.favorite_rounded : Icons.favorite_outline_rounded,
                    key: ValueKey<bool>(isFavorite),
                    color: isFavorite ? AppColors.error : Colors.white,
                    size: 26,
                  ),
                ),
                tooltip: 'Favorite',
                onPressed: onToggleFavorite,
              ),

              // 2. Download Button with circular progress
              Stack(
                alignment: Alignment.center,
                children: [
                  if (isDownloading)
                    SizedBox(
                      width: 36,
                      height: 36,
                      child: CircularProgressIndicator(
                        value: downloadProgress > 0 ? downloadProgress : null,
                        strokeWidth: 2.5,
                        color: AppColors.primary,
                      ),
                    ),
                  IconButton(
                    icon: Icon(
                      Icons.download_rounded,
                      color: isDownloading ? AppColors.primary : Colors.white,
                      size: 26,
                    ),
                    tooltip: 'Download',
                    onPressed: isDownloading ? null : onDownload,
                  ),
                ],
              ),
              const SizedBox(width: 6),

              // 3. Set Wallpaper Prominent Action
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                  elevation: 4,
                ),
                icon: isSettingWallpaper
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.wallpaper_rounded, size: 20),
                label: Text(
                  isSettingWallpaper ? 'Applying...' : 'Set Wallpaper',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                ),
                onPressed: isSettingWallpaper ? null : onSetWallpaper,
              ),
              const SizedBox(width: 6),

              // 4. Info Details Action
              IconButton(
                icon: const Icon(Icons.info_outline_rounded, color: Colors.white, size: 24),
                tooltip: 'Wallpaper Info',
                onPressed: onOpenInfo,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
