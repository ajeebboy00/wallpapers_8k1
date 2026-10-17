import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:wallpapers_8k1/features/home/data/home_repository.dart';
import 'package:wallpapers_8k1/features/home/presentation/bloc/home_cubit.dart';
import 'package:wallpapers_8k1/features/home/presentation/bloc/home_state.dart';
import 'package:wallpapers_8k1/shared/models/category_model.dart';
import 'package:wallpapers_8k1/shared/models/collection_model.dart';
import 'package:wallpapers_8k1/shared/models/wallpaper_model.dart';

class MockHomeRepository extends Mock implements HomeRepository {}

void main() {
  late MockHomeRepository mockRepository;
  late HomeBundle sampleBundle;

  setUp(() {
    mockRepository = MockHomeRepository();
    sampleBundle = const HomeBundle(
      dailyWallpaper: WallpaperModel(
        id: 'daily-1',
        title: 'Daily Nebula',
        slug: 'daily-nebula',
        originalUrl: 'url',
        imageUrl: 'url',
        thumbnailUrl: 'url',
        previewUrl: 'url',
        width: 7680,
        height: 4320,
        aspectRatio: 1.7778,
        fileSize: 1000,
        fileFormat: 'webp',
        resolution: '8K',
        categoryId: 'cat-1',
        isDaily: true,
      ),
      featuredWallpapers: [],
      trendingWallpapers: [],
      categories: [
        CategoryModel(id: 'cat-1', name: 'Space', slug: 'space'),
      ],
      featuredCollections: [
        CollectionModel(id: 'coll-1', name: 'Cyberpunk', slug: 'cyberpunk'),
      ],
      newestWallpapers: [],
    );
  });

  group('HomeCubit Tests', () {
    test('initial state is HomeInitial', () {
      final cubit = HomeCubit(mockRepository);
      expect(cubit.state, const HomeInitial());
      cubit.close();
    });

    blocTest<HomeCubit, HomeState>(
      'emits [HomeLoading, HomeLoaded] when loadHomeFeed succeeds',
      build: () {
        when(() => mockRepository.getHomeFeed()).thenAnswer((_) async => sampleBundle);
        return HomeCubit(mockRepository);
      },
      act: (cubit) => cubit.loadHomeFeed(),
      expect: () => [
        const HomeLoading(),
        HomeLoaded(sampleBundle),
      ],
      verify: (_) {
        verify(() => mockRepository.getHomeFeed()).called(1);
      },
    );

    blocTest<HomeCubit, HomeState>(
      'emits [HomeLoading, HomeError] when loadHomeFeed fails',
      build: () {
        when(() => mockRepository.getHomeFeed()).thenThrow(Exception('Network error'));
        return HomeCubit(mockRepository);
      },
      act: (cubit) => cubit.loadHomeFeed(),
      expect: () => [
        const HomeLoading(),
        isA<HomeError>(),
      ],
      verify: (_) {
        verify(() => mockRepository.getHomeFeed()).called(1);
      },
    );

    blocTest<HomeCubit, HomeState>(
      'emits [HomeLoaded] when refreshHomeFeed succeeds',
      build: () {
        when(() => mockRepository.getHomeFeed()).thenAnswer((_) async => sampleBundle);
        return HomeCubit(mockRepository);
      },
      act: (cubit) => cubit.refreshHomeFeed(),
      expect: () => [
        HomeLoaded(sampleBundle),
      ],
      verify: (_) {
        verify(() => mockRepository.getHomeFeed()).called(1);
      },
    );
  });
}
