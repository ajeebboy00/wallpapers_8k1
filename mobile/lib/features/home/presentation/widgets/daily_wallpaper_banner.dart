import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/models/wallpaper_model.dart';
import '../../../../shared/widgets/shimmer_loader.dart';

class DailyWallpaperBanner extends StatelessWidget {
  final WallpaperModel wallpaper;

  const DailyWallpaperBanner({
    super.key,
    required this.wallpaper,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      child: GestureDetector(
        onTap: () => context.push('/wallpaper/${wallpaper.id}'),
        child: Container(
          height: 220,
          decoration: BoxDecoration(
            borderRadius: AppRadius.roundedLg,
            border: Border.all(color: AppColors.primary.withOpacity(0.3), width: 1.5),
            boxShadow: [
              BoxShadow(
                color: AppColors.primary.withOpacity(0.15),
                blurRadius: 20,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: AppRadius.roundedLg,
            child: Stack(
              fit: StackFit.expand,
              children: [
                // 1. Background Cached Image
                CachedNetworkImage(
                  imageUrl: wallpaper.previewUrl.isNotEmpty ? wallpaper.previewUrl : wallpaper.imageUrl,
                  fit: BoxFit.cover,
                  placeholder: (context, url) => const ShimmerPlaceholder(),
                  errorWidget: (context, url, error) => Container(color: AppColors.darkSurface),
                ),

                // 2. Cinematic Gradient Overlay
                Positioned.fill(
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Colors.black.withOpacity(0.2),
                          Colors.black.withOpacity(0.4),
                          Colors.black.withOpacity(0.85),
                        ],
                      ),
                    ),
                  ),
                ),

                // 3. Top Banner Badges
                Positioned(
                  top: 14,
                  left: 14,
                  right: 14,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.primary,
                          borderRadius: BorderRadius.circular(6),
                          boxShadow: [
                            BoxShadow(
                              color: AppColors.primary.withOpacity(0.4),
                              blurRadius: 8,
                            ),
                          ],
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.auto_awesome_rounded, size: 13, color: Colors.white),
                            SizedBox(width: 5),
                            Text(
                              "DAILY SPOTLIGHT",
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 10,
                                fontWeight: FontWeight.w800,
                                letterSpacing: 0.8,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.black.withOpacity(0.6),
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(color: Colors.white24, width: 0.5),
                        ),
                        child: Text(
                          wallpaper.resolution,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                // 4. Bottom Info & CTA
                Positioned(
                  bottom: 14,
                  left: 14,
                  right: 14,
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              wallpaper.title,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 18,
                                fontWeight: FontWeight.w800,
                                shadows: [Shadow(blurRadius: 6, color: Colors.black)],
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              wallpaper.category != null ? wallpaper.category!.name : 'Ultra HD Collection',
                              style: const TextStyle(
                                color: AppColors.textDarkSecondary,
                                fontSize: 12,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.white30, width: 1),
                        ),
                        child: const Row(
                          children: [
                            Text(
                              'View 8K',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            SizedBox(width: 4),
                            Icon(Icons.arrow_forward_rounded, size: 14, color: Colors.white),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
