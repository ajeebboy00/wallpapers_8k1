import '../../shared/models/category_model.dart';
import '../../shared/models/collection_model.dart';
import '../../shared/models/tag_model.dart';
import '../../shared/models/wallpaper_model.dart';
import '../../features/home/data/home_repository.dart';

class MockFeedData {
  static const catAnime = CategoryModel(
    id: 'cat-anime',
    name: 'Anime',
    slug: 'anime',
    description: 'High resolution anime backgrounds and character art',
    imageUrl: 'https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=800&q=80',
    wallpaperCount: 42,
  );

  static const catNature = CategoryModel(
    id: 'cat-nature',
    name: 'Nature',
    slug: 'nature',
    description: 'Breathtaking mountain landscapes, rivers, and forests',
    imageUrl: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80',
    wallpaperCount: 85,
  );

  static const catCyberpunk = CategoryModel(
    id: 'cat-cyberpunk',
    name: 'Cyberpunk',
    slug: 'cyberpunk',
    description: 'Neon futuristic cities, synthwave and tech noir',
    imageUrl: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80',
    wallpaperCount: 64,
  );

  static const catAmoled = CategoryModel(
    id: 'cat-amoled',
    name: 'AMOLED',
    slug: 'amoled',
    description: 'Pure black true-black wallpapers for OLED screens',
    imageUrl: 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80',
    wallpaperCount: 53,
  );

  static const catSpace = CategoryModel(
    id: 'cat-space',
    name: 'Space',
    slug: 'space',
    description: '8K deep cosmos, nebulae, galaxies, and planetary vistas',
    imageUrl: 'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=800&q=80',
    wallpaperCount: 71,
  );

  static const List<CategoryModel> mockCategories = [
    catAnime,
    catNature,
    catCyberpunk,
    catAmoled,
    catSpace,
  ];

  static const List<CollectionModel> mockCollections = [
    CollectionModel(
      id: 'coll-8k-best',
      name: 'Best of 8K Ultra HD',
      slug: 'best-of-8k',
      description: 'Hand-picked wallpapers mastered in native 7680x4320 resolution',
      coverImageUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80',
      isFeatured: true,
      wallpaperCount: 28,
    ),
    CollectionModel(
      id: 'coll-neon-nights',
      name: 'Cyberpunk Neon Nights',
      slug: 'cyberpunk-neon-nights',
      description: 'Luminous neon rain aesthetics from futuristic Tokyo',
      coverImageUrl: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1200&q=80',
      isFeatured: true,
      wallpaperCount: 19,
    ),
    CollectionModel(
      id: 'coll-true-black',
      name: 'True Black Minimal',
      slug: 'true-black-minimal',
      description: 'Optimized for zero battery drain on modern OLED displays',
      coverImageUrl: 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=1200&q=80',
      isFeatured: true,
      wallpaperCount: 22,
    ),
  ];

  static final List<WallpaperModel> mockWallpapers = [
    const WallpaperModel(
      id: 'w1-celestial-nebula',
      title: 'Celestial Nebula 8K',
      slug: 'celestial-nebula-8k',
      description: 'Breathtaking deep cosmos explosion of vibrant purple and teal dust clouds.',
      originalUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=3840&q=85',
      imageUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1920&q=80',
      thumbnailUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=600&q=70',
      previewUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1080&q=75',
      width: 7680,
      height: 4320,
      aspectRatio: 1.777,
      fileSize: 18450120,
      fileFormat: 'WEBP',
      resolution: '8K UHD',
      categoryId: 'cat-space',
      viewCount: 14200,
      downloadCount: 9820,
      favoriteCount: 3450,
      shareCount: 820,
      isFeatured: true,
      isTrending: true,
      isDaily: true,
      dominantColor: '#6C5CE7',
      colorPalette: ['#6C5CE7', '#00CEC9', '#0984E3'],
      tags: [
        TagModel(id: 't-space', name: 'Space', slug: 'space'),
        TagModel(id: 't-nebula', name: 'Nebula', slug: 'nebula'),
        TagModel(id: 't-8k', name: '8K UHD', slug: '8k-uhd'),
      ],
    ),
    const WallpaperModel(
      id: 'w2-neo-tokyo',
      title: 'Neo Tokyo Rain',
      slug: 'neo-tokyo-rain',
      description: 'Cyberpunk street illuminated by holographic signs and neon reflections.',
      originalUrl: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=3840&q=85',
      imageUrl: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1920&q=80',
      thumbnailUrl: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=70',
      previewUrl: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1080&q=75',
      width: 7680,
      height: 4320,
      aspectRatio: 1.777,
      fileSize: 19200400,
      fileFormat: 'WEBP',
      resolution: '8K UHD',
      categoryId: 'cat-cyberpunk',
      viewCount: 21400,
      downloadCount: 12300,
      favoriteCount: 5210,
      shareCount: 1140,
      isFeatured: true,
      isTrending: true,
      isDaily: false,
      dominantColor: '#E84393',
      colorPalette: ['#E84393', '#2D3436', '#FD79A8'],
      tags: [
        TagModel(id: 't-cyberpunk', name: 'Cyberpunk', slug: 'cyberpunk'),
        TagModel(id: 't-neon', name: 'Neon', slug: 'neon'),
      ],
    ),
    const WallpaperModel(
      id: 'w3-yosemite-dawn',
      title: 'Yosemite Mirror Lake',
      slug: 'yosemite-mirror-lake',
      description: 'Crystal clear water reflection of sheer granite cliffs under dawn light.',
      originalUrl: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=3840&q=85',
      imageUrl: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1920&q=80',
      thumbnailUrl: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=70',
      previewUrl: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1080&q=75',
      width: 7680,
      height: 4320,
      aspectRatio: 1.777,
      fileSize: 16540100,
      fileFormat: 'JPEG',
      resolution: '8K UHD',
      categoryId: 'cat-nature',
      viewCount: 16800,
      downloadCount: 10100,
      favoriteCount: 4100,
      shareCount: 650,
      isFeatured: true,
      isTrending: false,
      isDaily: false,
      dominantColor: '#00B894',
      colorPalette: ['#00B894', '#55EFC4', '#2D3436'],
      tags: [
        TagModel(id: 't-nature', name: 'Nature', slug: 'nature'),
        TagModel(id: 't-mountains', name: 'Mountains', slug: 'mountains'),
      ],
    ),
    const WallpaperModel(
      id: 'w4-dark-poly',
      title: 'Dark Minimalist Poly',
      slug: 'dark-minimalist-poly',
      description: 'Deep dark AMOLED polygon geometric relief with subtle edge highlights.',
      originalUrl: 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=3840&q=85',
      imageUrl: 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=1920&q=80',
      thumbnailUrl: 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=600&q=70',
      previewUrl: 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=1080&q=75',
      width: 7680,
      height: 4320,
      aspectRatio: 1.777,
      fileSize: 11200300,
      fileFormat: 'WEBP',
      resolution: '8K UHD',
      categoryId: 'cat-amoled',
      viewCount: 28900,
      downloadCount: 19400,
      favoriteCount: 7300,
      shareCount: 1450,
      isFeatured: true,
      isTrending: true,
      isDaily: false,
      dominantColor: '#1E272E',
      colorPalette: ['#000000', '#1E272E', '#485460'],
      tags: [
        TagModel(id: 't-amoled', name: 'AMOLED', slug: 'amoled'),
        TagModel(id: 't-dark', name: 'Dark', slug: 'dark'),
      ],
    ),
    const WallpaperModel(
      id: 'w5-sunset-horizon',
      title: 'Anime Sunset Horizon',
      slug: 'anime-sunset-horizon',
      description: 'Serene golden hour clouds over a distant anime coastal skyline.',
      originalUrl: 'https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=3840&q=85',
      imageUrl: 'https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=1920&q=80',
      thumbnailUrl: 'https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=600&q=70',
      previewUrl: 'https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=1080&q=75',
      width: 7680,
      height: 4320,
      aspectRatio: 1.777,
      fileSize: 15400200,
      fileFormat: 'JPEG',
      resolution: '8K UHD',
      categoryId: 'cat-anime',
      viewCount: 19800,
      downloadCount: 14100,
      favoriteCount: 6200,
      shareCount: 930,
      isFeatured: true,
      isTrending: true,
      isDaily: false,
      dominantColor: '#FFA502',
      colorPalette: ['#FFA502', '#FF6348', '#2F3542'],
      tags: [
        TagModel(id: 't-anime', name: 'Anime', slug: 'anime'),
        TagModel(id: 't-sunset', name: 'Sunset', slug: 'sunset'),
      ],
    ),
  ];

  static HomeBundle getHomeBundle() {
    return HomeBundle(
      dailyWallpaper: mockWallpapers[0],
      featuredWallpapers: mockWallpapers,
      trendingWallpapers: mockWallpapers.reversed.toList(),
      categories: mockCategories,
      featuredCollections: mockCollections,
      newestWallpapers: mockWallpapers,
    );
  }

  static WallpaperModel getWallpaperById(String identifier) {
    for (final w in mockWallpapers) {
      if (w.id == identifier || w.slug == identifier) {
        return w;
      }
    }
    return mockWallpapers[0];
  }
}
