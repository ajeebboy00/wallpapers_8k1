import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';
import 'shimmer_loader.dart';

class WallpaperCard extends StatelessWidget {
  final String id;
  final String title;
  final String thumbnailUrl;
  final String resolution;
  final double aspectRatio;
  final bool isFavorite;
  final VoidCallback? onTap;
  final VoidCallback? onFavoriteTap;

  const WallpaperCard({
    super.key,
    required this.id,
    required this.title,
    required this.thumbnailUrl,
    required this.resolution,
    this.aspectRatio = 0.5625, // 9:16 vertical standard
    this.isFavorite = false,
    this.onTap,
    this.onFavoriteTap,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final is8k = resolution.toUpperCase().contains('8K');

    return GestureDetector(
      onTap: onTap,
      child: ClipRRect(
        borderRadius: AppRadius.roundedMd,
        child: AspectRatio(
          aspectRatio: aspectRatio,
          child: Stack(
            fit: StackFit.expand,
            children: [
              // 1. Cached Network Image with Placeholder
              CachedNetworkImage(
                imageUrl: thumbnailUrl,
                fit: BoxFit.cover,
                placeholder: (context, url) => const ShimmerPlaceholder(),
                errorWidget: (context, url, error) => Container(
                  color: isDark ? AppColors.darkSurface : AppColors.lightSurface,
                  child: const Center(
                    child: Icon(Icons.broken_image_rounded, color: AppColors.textDarkMuted),
                  ),
                ),
              ),

              // 2. Subtle gradient overlay at bottom
              Positioned.fill(
                child: DecoratedBox(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Colors.transparent,
                        Colors.transparent,
                        Colors.black.withOpacity(0.7),
                      ],
                    ),
                  ),
                ),
              ),

              // 3. Resolution Badge at Top-Left
              Positioned(
                top: 8,
                left: 8,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: is8k
                        ? AppColors.primary.withOpacity(0.9)
                        : Colors.black.withOpacity(0.6),
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(
                      color: is8k ? AppColors.primaryLight : Colors.white24,
                      width: 0.5,
                    ),
                  ),
                  child: Text(
                    resolution,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ),

              // 4. Favorite Icon at Top-Right
              if (onFavoriteTap != null)
                Positioned(
                  top: 4,
                  right: 4,
                  child: IconButton(
                    iconSize: 20,
                    icon: Icon(
                      isFavorite ? Icons.favorite_rounded : Icons.favorite_border_rounded,
                      color: isFavorite ? AppColors.favorite : Colors.white,
                    ),
                    onPressed: onFavoriteTap,
                  ),
                ),

              // 5. Title at Bottom
              Positioned(
                left: 10,
                right: 10,
                bottom: 10,
                child: Text(
                  title,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    shadows: [
                      Shadow(blurRadius: 4, color: Colors.black54),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
