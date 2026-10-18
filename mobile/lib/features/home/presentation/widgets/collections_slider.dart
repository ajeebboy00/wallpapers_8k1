import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/models/collection_model.dart';
import '../../../../shared/widgets/shimmer_loader.dart';

class CollectionsSlider extends StatelessWidget {
  final List<CollectionModel> collections;

  const CollectionsSlider({
    super.key,
    required this.collections,
  });

  @override
  Widget build(BuildContext context) {
    if (collections.isEmpty) return const SizedBox.shrink();

    return SizedBox(
      height: 130,
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 16.0),
        scrollDirection: Axis.horizontal,
        itemCount: collections.length,
        separatorBuilder: (_, __) => const SizedBox(width: 12),
        itemBuilder: (context, index) {
          final coll = collections[index];
          return GestureDetector(
            onTap: () => context.push('/collections'),
            child: SizedBox(
              width: 210,
              child: ClipRRect(
                borderRadius: AppRadius.roundedLg,
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    // Background Image / Fallback
                    if (coll.coverImageUrl != null && coll.coverImageUrl!.isNotEmpty)
                      CachedNetworkImage(
                        imageUrl: coll.coverImageUrl!,
                        fit: BoxFit.cover,
                        placeholder: (context, url) => const ShimmerPlaceholder(),
                        errorWidget: (context, url, error) => Container(color: AppColors.darkSurface),
                      )
                    else
                      Container(color: AppColors.darkSurfaceElevated),

                    // Gradient Overlay
                    Positioned.fill(
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.topCenter,
                            end: Alignment.bottomCenter,
                            colors: [
                              Colors.transparent,
                              Colors.black.withOpacity(0.5),
                              Colors.black.withOpacity(0.85),
                            ],
                          ),
                        ),
                      ),
                    ),

                    // Wallpaper count pill
                    Positioned(
                      top: 10,
                      left: 10,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.black.withOpacity(0.6),
                          borderRadius: BorderRadius.circular(4),
                          border: Border.all(color: Colors.white24, width: 0.5),
                        ),
                        child: Text(
                          '${coll.wallpaperCount} ITEMS',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 9,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 0.5,
                          ),
                        ),
                      ),
                    ),

                    // Title
                    Positioned(
                      bottom: 10,
                      left: 10,
                      right: 10,
                      child: Text(
                        coll.name,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                        ),
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
