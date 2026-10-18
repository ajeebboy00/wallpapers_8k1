import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/models/wallpaper_model.dart';
import '../../../../shared/widgets/wallpaper_card.dart';
import '../../domain/search_filter.dart';

class SearchResultsGrid extends StatelessWidget {
  final List<WallpaperModel> wallpapers;
  final SearchFilter filter;
  final int totalCount;
  final bool hasReachedMax;
  final bool isLoadingMore;
  final VoidCallback onLoadMore;
  final Function(SearchFilter) onFilterChanged;

  const SearchResultsGrid({
    super.key,
    required this.wallpapers,
    required this.filter,
    required this.totalCount,
    required this.hasReachedMax,
    required this.isLoadingMore,
    required this.onLoadMore,
    required this.onFilterChanged,
  });

  @override
  Widget build(BuildContext context) {
    return NotificationListener<ScrollNotification>(
      onNotification: (ScrollNotification scrollInfo) {
        if (!hasReachedMax &&
            !isLoadingMore &&
            scrollInfo.metrics.pixels >= scrollInfo.metrics.maxScrollExtent - 400) {
          onLoadMore();
        }
        return false;
      },
      child: CustomScrollView(
        slivers: [
          // 1. Active Filters & Count Header
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Active Filter Badges
                  if (filter.hasActiveFilters) ...[
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: [
                          if (filter.resolution != null)
                            Padding(
                              padding: const EdgeInsets.only(right: 8.0),
                              child: Chip(
                                label: Text('Res: ${filter.resolution}'),
                                deleteIcon: const Icon(Icons.close, size: 14),
                                onDeleted: () => onFilterChanged(filter.copyWith(clearResolution: true)),
                                backgroundColor: AppColors.primary.withOpacity(0.15),
                                labelStyle: const TextStyle(color: AppColors.primary, fontSize: 12),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(16),
                                  side: const BorderSide(color: AppColors.primary),
                                ),
                              ),
                            ),
                          if (filter.orientation != null)
                            Padding(
                              padding: const EdgeInsets.only(right: 8.0),
                              child: Chip(
                                label: Text('Orientation: ${filter.orientation}'),
                                deleteIcon: const Icon(Icons.close, size: 14),
                                onDeleted: () => onFilterChanged(filter.copyWith(clearOrientation: true)),
                                backgroundColor: AppColors.primary.withOpacity(0.15),
                                labelStyle: const TextStyle(color: AppColors.primary, fontSize: 12),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(16),
                                  side: const BorderSide(color: AppColors.primary),
                                ),
                              ),
                            ),
                          if (filter.sort != 'relevance')
                            Padding(
                              padding: const EdgeInsets.only(right: 8.0),
                              child: Chip(
                                label: Text('Sort: ${filter.sort}'),
                                deleteIcon: const Icon(Icons.close, size: 14),
                                onDeleted: () => onFilterChanged(filter.copyWith(sort: 'relevance')),
                                backgroundColor: AppColors.surfaceElevated,
                                labelStyle: const TextStyle(color: AppColors.textSecondary, fontSize: 12),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(16),
                                  side: const BorderSide(color: Colors.white24),
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 8),
                  ],

                  // Result Count
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '$totalCount wallpaper${totalCount != 1 ? 's' : ''} found',
                        style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: AppColors.textSecondary,
                        ),
                      ),
                      if (filter.hasActiveFilters)
                        GestureDetector(
                          onTap: () => onFilterChanged(const SearchFilter()),
                          child: const Text(
                            'Clear filters',
                            style: TextStyle(fontSize: 12, color: AppColors.primary),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          // 2. Wallpaper 2-Column Grid
          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
            sliver: SliverGrid(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: 0.5625, // 9:16 vertical standard
              ),
              delegate: SliverChildBuilderDelegate(
                (context, index) {
                  final wp = wallpapers[index];
                  return WallpaperCard(
                    id: wp.id,
                    title: wp.title,
                    thumbnailUrl: wp.thumbnailUrl.isNotEmpty ? wp.thumbnailUrl : wp.imageUrl,
                    resolution: wp.resolution,
                    aspectRatio: 0.5625,
                    onTap: () => context.push('/wallpaper/${wp.id}'),
                  );
                },
                childCount: wallpapers.length,
              ),
            ),
          ),

          // 3. Loading More Footer
          if (isLoadingMore)
            const SliverToBoxAdapter(
              child: Padding(
                padding: EdgeInsets.symmetric(vertical: 24.0),
                child: Center(
                  child: SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(
                      strokeWidth: 2.5,
                      color: AppColors.primary,
                    ),
                  ),
                ),
              ),
            ),

          // 4. Bottom clearance
          const SliverToBoxAdapter(child: SizedBox(height: 40)),
        ],
      ),
    );
  }
}
