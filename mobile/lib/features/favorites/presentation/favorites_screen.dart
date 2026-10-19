import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:wallpapers_8k1/core/network/api_client.dart';
import 'package:wallpapers_8k1/core/storage/secure_storage_service.dart';
import 'package:wallpapers_8k1/core/theme/app_colors.dart';
import 'package:wallpapers_8k1/shared/models/wallpaper_model.dart';
import 'package:wallpapers_8k1/shared/widgets/state_views.dart';
import 'package:wallpapers_8k1/shared/widgets/wallpaper_card.dart';

class FavoritesScreen extends StatefulWidget {
  const FavoritesScreen({super.key});

  @override
  State<FavoritesScreen> createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends State<FavoritesScreen> {
  final SecureStorageService _storage = SecureStorageService();
  late final ApiClient _apiClient;

  bool _isLoading = true;
  bool _isAuthenticated = false;
  String? _errorMessage;
  List<WallpaperModel> _wallpapers = [];

  @override
  void initState() {
    super.initState();
    _apiClient = ApiClient(storage: _storage);
    _loadFavorites();
  }

  Future<void> _loadFavorites() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final hasToken = await _storage.hasAccessToken();
    if (!hasToken) {
      if (mounted) {
        setState(() {
          _isAuthenticated = false;
          _isLoading = false;
        });
      }
      return;
    }

    try {
      final response = await _apiClient.get('/users/me/favorites');
      final list = (response.data['data'] as List<dynamic>? ?? [])
          .map((e) => WallpaperModel.fromJson(e as Map<String, dynamic>))
          .toList();

      if (mounted) {
        setState(() {
          _isAuthenticated = true;
          _wallpapers = list;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isAuthenticated = true;
          _errorMessage = e.toString().replaceAll("Exception: ", "");
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Saved Favorites', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20)),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator(color: AppColors.primary));
    }

    if (!_isAuthenticated) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: const BoxDecoration(
                  color: AppColors.surface,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.favorite_border_rounded, size: 56, color: AppColors.primary),
              ),
              const SizedBox(height: 20),
              const Text(
                'Sign In to Sync Favorites',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
              ),
              const SizedBox(height: 8),
              const Text(
                'Save your favorite 8K wallpapers and access them across all your devices.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 14, color: AppColors.textSecondary, height: 1.4),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                onPressed: () async {
                  await context.push('/login');
                  _loadFavorites();
                },
                child: const Text('Sign In', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
        ),
      );
    }

    if (_errorMessage != null) {
      return ErrorView(
        message: _errorMessage!,
        onRetry: _loadFavorites,
      );
    }

    if (_wallpapers.isEmpty) {
      return EmptyView(
        message: 'No favorites yet.\nTap the heart icon on any 8K wallpaper to save it here.',
        icon: Icons.favorite_outline_rounded,
        onAction: () => context.go('/explore'),
        actionLabel: 'Discover Wallpapers',
      );
    }

    return RefreshIndicator(
      color: AppColors.primary,
      onRefresh: _loadFavorites,
      child: GridView.builder(
        padding: const EdgeInsets.all(16.0),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 0.5625,
        ),
        itemCount: _wallpapers.length,
        itemBuilder: (context, index) {
          final wp = _wallpapers[index];
          return WallpaperCard(
            id: wp.id,
            title: wp.title,
            thumbnailUrl: wp.thumbnailUrl.isNotEmpty ? wp.thumbnailUrl : wp.imageUrl,
            resolution: wp.resolution,
            aspectRatio: 0.5625,
            onTap: () async {
              await context.push('/wallpaper/${wp.id}');
              _loadFavorites();
            },
          );
        },
      ),
    );
  }
}
