import 'package:flutter_test/flutter_test.dart';
import 'package:wallpapers_8k1/shared/models/category_model.dart';
import 'package:wallpapers_8k1/shared/models/collection_model.dart';
import 'package:wallpapers_8k1/shared/models/wallpaper_model.dart';

void main() {
  group('Home Models Serialization Tests', () {
    test('CategoryModel deserializes from JSON correctly', () {
      final json = {
        'id': 'cat-123',
        'name': 'Nature',
        'slug': 'nature',
        'description': 'Stunning wilderness in 8K',
        'image_url': 'https://storage.wallpapers8k1.com/nature.webp',
        'sort_order': 2,
        'is_active': true,
        'wallpaper_count': 14,
      };

      final category = CategoryModel.fromJson(json);

      expect(category.id, 'cat-123');
      expect(category.name, 'Nature');
      expect(category.slug, 'nature');
      expect(category.wallpaperCount, 14);
      expect(category.isActive, isTrue);
    });

    test('CollectionModel deserializes from JSON correctly', () {
      final json = {
        'id': 'coll-456',
        'name': 'Cyberpunk Aesthetics',
        'slug': 'cyberpunk-aesthetics',
        'description': 'High tech cityscapes',
        'cover_image_url': 'https://storage.wallpapers8k1.com/cover.webp',
        'is_featured': true,
        'is_published': true,
        'wallpaper_count': 9,
      };

      final collection = CollectionModel.fromJson(json);

      expect(collection.id, 'coll-456');
      expect(collection.name, 'Cyberpunk Aesthetics');
      expect(collection.slug, 'cyberpunk-aesthetics');
      expect(collection.isFeatured, isTrue);
      expect(collection.wallpaperCount, 9);
    });

    test('WallpaperModel deserializes from JSON with nested category and tags', () {
      final json = {
        'id': 'wp-789',
        'title': 'Supernova 8K',
        'slug': 'supernova-8k',
        'description': 'Deep space cosmic blast',
        'original_url': 'https://storage.wallpapers8k1.com/raw.png',
        'image_url': 'https://storage.wallpapers8k1.com/opt.webp',
        'thumbnail_url': 'https://storage.wallpapers8k1.com/thumb.webp',
        'preview_url': 'https://storage.wallpapers8k1.com/prev.webp',
        'width': 7680,
        'height': 4320,
        'aspect_ratio': 1.7778,
        'file_size': 25000000,
        'file_format': 'webp',
        'resolution': '8K',
        'category_id': 'cat-123',
        'view_count': 120,
        'download_count': 45,
        'favorite_count': 30,
        'share_count': 10,
        'is_featured': true,
        'is_trending': false,
        'is_daily': true,
        'is_published': true,
        'trending_score': 8.5,
        'category': {
          'id': 'cat-123',
          'name': 'Space',
          'slug': 'space',
        },
        'tags': [
          {'id': 'tag-1', 'name': 'cosmos', 'slug': 'cosmos'},
          {'id': 'tag-2', 'name': 'stars', 'slug': 'stars'},
        ],
      };

      final wallpaper = WallpaperModel.fromJson(json);

      expect(wallpaper.id, 'wp-789');
      expect(wallpaper.title, 'Supernova 8K');
      expect(wallpaper.resolution, '8K');
      expect(wallpaper.width, 7680);
      expect(wallpaper.height, 4320);
      expect(wallpaper.aspectRatio, 1.7778);
      expect(wallpaper.isDaily, isTrue);
      expect(wallpaper.category?.name, 'Space');
      expect(wallpaper.tags.length, 2);
      expect(wallpaper.tags[0].name, 'cosmos');
    });

    test('WallpaperModel copyWith toggles isFavorite', () {
      const wallpaper = WallpaperModel(
        id: 'wp-1',
        title: 'Mountain Lake',
        slug: 'mountain-lake',
        originalUrl: 'url',
        imageUrl: 'url',
        thumbnailUrl: 'url',
        previewUrl: 'url',
        width: 3840,
        height: 2160,
        aspectRatio: 1.7778,
        fileSize: 10000,
        fileFormat: 'webp',
        resolution: '4K',
        categoryId: 'cat-1',
        isFavorite: false,
      );

      final updated = wallpaper.copyWith(isFavorite: true);

      expect(updated.isFavorite, isTrue);
      expect(wallpaper.isFavorite, isFalse);
    });
  });
}
