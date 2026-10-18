import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/models/wallpaper_model.dart';
import '../../../../shared/widgets/shimmer_loader.dart';

class FeaturedCarousel extends StatelessWidget {
  final List<WallpaperModel> wallpapers;

  const FeaturedCarousel({
    super.key,
    required this.wallpapers,
  });

  @override
  Widget build(BuildContext context) {
    if (wallpapers.isEmpty) return const SizedBox.shrink();

    return SizedBox(
      height: 180,
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 16.0),
        scrollDirection: Axis.horizontal,
        itemCount: wallpapers.length,
        separatorBuilder: (_, __) => const SizedBox(width: 14),
        itemBuilder: (context, index) {
          final wp = wallpapers[index];
          return GestureDetector(
            onTap: () => context.push('/wallpaper/${wp.id}'),
            child: SizedBox(
              width: 270,
              child: ClipRRect(
                borderRadius: AppRadius.roundedLg,
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    // Background Image
                    CachedNetworkImage(
                      imageUrl: wp.previewUrl.isNotEmpty ? wp.previewUrl : wp.imageUrl,
                      fit: BoxFit.cover,
                      placeholder: (context, url) => const ShimmerPlaceholder(),
                      errorWidget: (context, url, error) => Container(color: AppColors.darkSurface),
                    ),

                    // Gradient Overlay
                    Positioned.fill(
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.topCenter,
                            end: Alignment.bottomCenter,
                            colors: [
                              Colors.transparent,
                              Colors.black.withOpacity(0.3),
                              Colors.black.withOpacity(0.8),
                            ],
                          ),
                        ),
                      ),
                    ),

                    // Top Featured Badge
                    Positioned(
                      top: 10,
                      left: 10,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: AppColors.primaryDark.withOpacity(0.9),
                          borderRadius: BorderRadius.circular(4),
                          border: Border.all(color: AppColors.primaryLight, width: 0.5),
                        ),
                        child: Text(
                          wp.resolution,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                    ),

                    // Title & Category at Bottom
                    Positioned(
                      bottom: 12,
                      left: 12,
                      right: 12,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            wp.title,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          if (wp.category != null) ...[
                            const SizedBox(height: 2),
                            Text(
                              wp.category!.name,
                              style: const TextStyle(
                                color: AppColors.textDarkSecondary,
                                fontSize: 11,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
