import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:wallpapers_8k1/core/services/wallpaper_setter_service.dart';
import 'package:wallpapers_8k1/features/wallpapers/data/wallpaper_detail_repository.dart';
import 'package:wallpapers_8k1/features/wallpapers/presentation/bloc/wallpaper_detail_cubit.dart';
import 'package:wallpapers_8k1/features/wallpapers/presentation/bloc/wallpaper_detail_state.dart';
import 'package:wallpapers_8k1/shared/models/wallpaper_model.dart';

class MockWallpaperDetailRepository extends Mock implements IWallpaperDetailRepository {}

void main() {
  late MockWallpaperDetailRepository mockRepo;

  const testWallpaper = WallpaperModel(
    id: 'wp-detail-1',
    title: 'Cyberpunk Skyline 8K',
    slug: 'cyberpunk-skyline-8k',
    originalUrl: 'https://storage/orig.png',
    imageUrl: 'https://storage/opt.webp',
    thumbnailUrl: 'https://storage/thumb.webp',
    previewUrl: 'https://storage/prev.webp',
    width: 7680,
    height: 4320,
    aspectRatio: 1.7778,
    fileSize: 25000000,
    fileFormat: 'webp',
    resolution: '8K',
    categoryId: 'cat-1',
    favoriteCount: 5,
  );

  const testBundle = WallpaperDetailBundle(
    wallpaper: testWallpaper,
    relatedWallpapers: [],
    isFavorite: false,
  );

  setUp(() {
    mockRepo = MockWallpaperDetailRepository();
  });

  group('WallpaperDetailCubit Unit Tests', () {
    test('initial state is WallpaperDetailInitial', () {
      final cubit = WallpaperDetailCubit(mockRepo);
      expect(cubit.state, const WallpaperDetailInitial());
      cubit.close();
    });

    blocTest<WallpaperDetailCubit, WallpaperDetailState>(
      'loadWallpaper emits [WallpaperDetailLoading, WallpaperDetailLoaded] on success',
      build: () {
        when(() => mockRepo.getWallpaperDetail('wp-detail-1'))
            .thenAnswer((_) async => testBundle);
        return WallpaperDetailCubit(mockRepo);
      },
      act: (cubit) => cubit.loadWallpaper('wp-detail-1'),
      expect: () => [
        const WallpaperDetailLoading(),
        const WallpaperDetailLoaded(
          wallpaper: testWallpaper,
          relatedWallpapers: [],
          isFavorite: false,
          favoriteCount: 5,
        ),
      ],
      verify: (_) {
        verify(() => mockRepo.getWallpaperDetail('wp-detail-1')).called(1);
      },
    );

    blocTest<WallpaperDetailCubit, WallpaperDetailState>(
      'toggleFavorite optimistically increments and verifies with repository',
      build: () {
        when(() => mockRepo.getWallpaperDetail('wp-detail-1'))
            .thenAnswer((_) async => testBundle);
        when(() => mockRepo.toggleFavorite(any(), any()))
            .thenAnswer((_) async => {'is_favorite': true, 'favorite_count': 6});
        return WallpaperDetailCubit(mockRepo);
      },
      act: (cubit) async {
        await cubit.loadWallpaper('wp-detail-1');
        await cubit.toggleFavorite();
      },
      skip: 2, // Skip initial loading & loaded
      expect: () => [
        // 1. Optimistic emission
        const WallpaperDetailLoaded(
          wallpaper: testWallpaper,
          isFavorite: true,
          favoriteCount: 6,
        ),
      ],
    );

    blocTest<WallpaperDetailCubit, WallpaperDetailState>(
      'setWallpaper calls setter service and emits success message',
      build: () {
        when(() => mockRepo.getWallpaperDetail('wp-detail-1'))
            .thenAnswer((_) async => testBundle);
        when(() => mockRepo.setWallpaper(
              wallpaper: any(named: 'wallpaper'),
              destination: WallpaperDestination.home,
              onProgress: any(named: 'onProgress'),
            )).thenAnswer((_) async => true);
        return WallpaperDetailCubit(mockRepo);
      },
      act: (cubit) async {
        await cubit.loadWallpaper('wp-detail-1');
        await cubit.setWallpaper(WallpaperDestination.home);
      },
      skip: 2, // Skip load
      expect: () => [
        const WallpaperDetailLoaded(
          wallpaper: testWallpaper,
          favoriteCount: 5,
          isSettingWallpaper: true,
          setWallpaperSuccess: false,
        ),
        const WallpaperDetailLoaded(
          wallpaper: testWallpaper,
          favoriteCount: 5,
          isSettingWallpaper: false,
          setWallpaperSuccess: true,
          infoMessage: 'Wallpaper applied to Home Screen',
        ),
      ],
    );
  });
}
