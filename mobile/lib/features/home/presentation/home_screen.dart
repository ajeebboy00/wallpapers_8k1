import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import 'package:wallpapers_8k1/core/constants/app_constants.dart';
import 'package:wallpapers_8k1/core/network/api_client.dart';
import 'package:wallpapers_8k1/core/storage/secure_storage_service.dart';
import 'package:wallpapers_8k1/core/theme/app_colors.dart';
import 'package:wallpapers_8k1/shared/widgets/server_config_dialog.dart';
import 'package:wallpapers_8k1/shared/widgets/state_views.dart';
import 'package:wallpapers_8k1/shared/widgets/wallpaper_card.dart';
import 'package:wallpapers_8k1/features/home/data/home_remote_data_source.dart';
import 'package:wallpapers_8k1/features/home/data/home_repository.dart';
import 'bloc/home_cubit.dart';
import 'bloc/home_state.dart';
import 'widgets/category_chips_bar.dart';
import 'widgets/collections_slider.dart';
import 'widgets/daily_wallpaper_banner.dart';
import 'widgets/featured_carousel.dart';
import 'widgets/home_shimmer_view.dart';
import 'widgets/section_header.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Provide HomeCubit with real ApiClient and Repository
    return BlocProvider<HomeCubit>(
      create: (context) {
        final apiClient = ApiClient(storage: SecureStorageService());
        final dataSource = HomeRemoteDataSource(apiClient);
        final repository = HomeRepository(dataSource);
        return HomeCubit(repository)..loadHomeFeed();
      },
      child: const _HomeScreenContent(),
    );
  }
}

class _HomeScreenContent extends StatelessWidget {
  const _HomeScreenContent();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: AppColors.primary,
                borderRadius: BorderRadius.circular(6),
              ),
              child: const Text(
                AppConstants.appShortBrand,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 1,
                  color: Colors.white,
                ),
              ),
            ),
            const SizedBox(width: 10),
            const Text(
              'Wallpapers',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.search_rounded),
            tooltip: 'Search',
            onPressed: () => context.push('/search'),
          ),
          IconButton(
            icon: const Icon(Icons.notifications_none_rounded),
            tooltip: 'Notifications',
            onPressed: () => context.push('/notifications'),
          ),
          IconButton(
            icon: const Icon(Icons.wifi_tethering_rounded),
            tooltip: 'Server IP',
            onPressed: () => showServerConfigDialog(
              context,
              onSaved: () => context.read<HomeCubit>().loadHomeFeed(),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.favorite_outline_rounded),
            tooltip: 'Favorites',
            onPressed: () => context.push('/favorites'),
          ),
        ],
      ),
      body: BlocBuilder<HomeCubit, HomeState>(
        builder: (context, state) {
          if (state is HomeLoading) {
            return const HomeShimmerView();
          }

          if (state is HomeError) {
            return ErrorView(
              message: state.message,
              onRetry: () => context.read<HomeCubit>().loadHomeFeed(),
            );
          }

          if (state is HomeLoaded) {
            final bundle = state.bundle;

            return RefreshIndicator(
              color: AppColors.primary,
              onRefresh: () => context.read<HomeCubit>().refreshHomeFeed(),
              child: CustomScrollView(
                slivers: [
                  // 1. Daily Spotlight Banner
                  if (bundle.dailyWallpaper != null)
                    SliverToBoxAdapter(
                      child: DailyWallpaperBanner(wallpaper: bundle.dailyWallpaper!),
                    ),

                  // 2. Category Quick Filter Chips
                  if (bundle.categories.isNotEmpty) ...[
                    const SliverToBoxAdapter(child: SizedBox(height: 8)),
                    SliverToBoxAdapter(
                      child: CategoryChipsBar(categories: bundle.categories),
                    ),
                  ],

                  // 3. Featured 8K Wallpapers Carousel
                  if (bundle.featuredWallpapers.isNotEmpty) ...[
                    const SliverToBoxAdapter(child: SizedBox(height: 12)),
                    SliverToBoxAdapter(
                      child: SectionHeader(
                        title: 'Featured 8K Ultra',
                        subtitle: 'Curated premium visuals',
                        onSeeAll: () => context.push('/explore'),
                      ),
                    ),
                    SliverToBoxAdapter(
                      child: FeaturedCarousel(wallpapers: bundle.featuredWallpapers),
                    ),
                  ],

                  // 4. Curated Collections
                  if (bundle.featuredCollections.isNotEmpty) ...[
                    const SliverToBoxAdapter(child: SizedBox(height: 16)),
                    SliverToBoxAdapter(
                      child: SectionHeader(
                        title: 'Curated Collections',
                        subtitle: 'Hand-picked aesthetic sets',
                        onSeeAll: () => context.push('/collections'),
                      ),
                    ),
                    SliverToBoxAdapter(
                      child: CollectionsSlider(collections: bundle.featuredCollections),
                    ),
                  ],

                  // 5. Trending Wallpapers Grid
                  if (bundle.trendingWallpapers.isNotEmpty) ...[
                    const SliverToBoxAdapter(child: SizedBox(height: 16)),
                    SliverToBoxAdapter(
                      child: SectionHeader(
                        title: 'Trending This Week',
                        subtitle: 'Most downloaded by the community',
                        onSeeAll: () => context.push('/explore'),
                      ),
                    ),
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
                            final wp = bundle.trendingWallpapers[index];
                            return WallpaperCard(
                              id: wp.id,
                              title: wp.title,
                              thumbnailUrl: wp.thumbnailUrl.isNotEmpty ? wp.thumbnailUrl : wp.imageUrl,
                              resolution: wp.resolution,
                              aspectRatio: 0.5625,
                              onTap: () => context.push('/wallpaper/${wp.id}'),
                            );
                          },
                          childCount: bundle.trendingWallpapers.length,
                        ),
                      ),
                    ),
                  ],

                  // 6. Newest Wallpapers Grid
                  if (bundle.newestWallpapers.isNotEmpty) ...[
                    const SliverToBoxAdapter(child: SizedBox(height: 16)),
                    SliverToBoxAdapter(
                      child: SectionHeader(
                        title: 'Newest Arrivals',
                        subtitle: 'Freshly uploaded 8K & 4K wallpapers',
                        onSeeAll: () => context.push('/explore'),
                      ),
                    ),
                    SliverPadding(
                      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                      sliver: SliverGrid(
                        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 2,
                          crossAxisSpacing: 12,
                          mainAxisSpacing: 12,
                          childAspectRatio: 0.5625,
                        ),
                        delegate: SliverChildBuilderDelegate(
                          (context, index) {
                            final wp = bundle.newestWallpapers[index];
                            return WallpaperCard(
                              id: wp.id,
                              title: wp.title,
                              thumbnailUrl: wp.thumbnailUrl.isNotEmpty ? wp.thumbnailUrl : wp.imageUrl,
                              resolution: wp.resolution,
                              aspectRatio: 0.5625,
                              onTap: () => context.push('/wallpaper/${wp.id}'),
                            );
                          },
                          childCount: bundle.newestWallpapers.length,
                        ),
                      ),
                    ),
                  ],

                  // Bottom padding for scroll clearance
                  const SliverToBoxAdapter(child: SizedBox(height: 40)),
                ],
              ),
            );
          }

          return const SizedBox.shrink();
        },
      ),
    );
  }
}
