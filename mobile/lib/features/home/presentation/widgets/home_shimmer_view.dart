import 'package:flutter/material.dart';
import 'package:wallpapers_8k1/core/theme/app_spacing.dart';
import 'package:wallpapers_8k1/shared/widgets/shimmer_loader.dart';

class HomeShimmerView extends StatelessWidget {
  const HomeShimmerView({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      physics: const NeverScrollableScrollPhysics(),
      padding: const EdgeInsets.symmetric(vertical: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Daily Banner Skeleton
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: ShimmerPlaceholder(
              height: 220,
              borderRadius: AppRadius.roundedLg,
            ),
          ),
          const SizedBox(height: 20),

          // 2. Category Chips Skeleton
          SizedBox(
            height: 38,
            child: ListView.separated(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              scrollDirection: Axis.horizontal,
              itemCount: 6,
              separatorBuilder: (_, __) => const SizedBox(width: 8),
              itemBuilder: (_, __) => ShimmerPlaceholder(
                width: 90,
                height: 38,
                borderRadius: AppRadius.roundedFull,
              ),
            ),
          ),
          const SizedBox(height: 24),

          // 3. Featured Header & Carousel Skeleton
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: ShimmerPlaceholder(width: 160, height: 22, borderRadius: AppRadius.roundedSm),
          ),
          const SizedBox(height: 12),
          SizedBox(
            height: 180,
            child: ListView.separated(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              scrollDirection: Axis.horizontal,
              itemCount: 3,
              separatorBuilder: (_, __) => const SizedBox(width: 14),
              itemBuilder: (_, __) => ShimmerPlaceholder(
                width: 270,
                height: 180,
                borderRadius: AppRadius.roundedLg,
              ),
            ),
          ),
          const SizedBox(height: 24),

          // 4. Trending Grid Skeleton
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: ShimmerPlaceholder(width: 180, height: 22, borderRadius: AppRadius.roundedSm),
          ),
          const SizedBox(height: 12),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: 4,
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: 0.5625,
              ),
              itemBuilder: (_, __) => ShimmerPlaceholder(
                borderRadius: AppRadius.roundedMd,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
