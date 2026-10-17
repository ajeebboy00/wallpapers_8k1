import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:wallpapers_8k1/features/search/data/search_remote_data_source.dart';
import 'package:wallpapers_8k1/features/search/data/search_repository.dart';
import 'package:wallpapers_8k1/features/search/domain/search_filter.dart';
import 'package:wallpapers_8k1/features/search/presentation/bloc/search_cubit.dart';
import 'package:wallpapers_8k1/features/search/presentation/bloc/search_state.dart';
import 'package:wallpapers_8k1/shared/models/wallpaper_model.dart';

class MockSearchRepository extends Mock implements ISearchRepository {}

void main() {
  late MockSearchRepository mockRepository;

  const sampleWallpaper = WallpaperModel(
    id: 'wp-100',
    title: 'Neon Cyberpunk 8K',
    slug: 'neon-cyberpunk-8k',
    originalUrl: 'https://storage/orig.png',
    imageUrl: 'https://storage/img.webp',
    thumbnailUrl: 'https://storage/thumb.webp',
    previewUrl: 'https://storage/prev.webp',
    width: 7680,
    height: 4320,
    aspectRatio: 1.7778,
    fileSize: 20000000,
    fileFormat: 'webp',
    resolution: '8K',
    categoryId: 'cat-1',
  );

  const sampleBundle = SearchResultBundle(
    wallpapers: [sampleWallpaper],
    page: 1,
    total: 1,
    totalPages: 1,
    hasNext: false,
  );

  const sampleSuggestions = SearchSuggestionsBundle(
    popularSearches: ['8K Ultra', 'Cyberpunk'],
    suggestedTags: ['space', 'nature'],
    suggestedCategories: ['Sci-Fi', 'Nature'],
  );

  setUp(() {
    mockRepository = MockSearchRepository();
  });

  group('SearchCubit Tests', () {
    test('initial state is SearchInitial', () {
      final cubit = SearchCubit(mockRepository);
      expect(cubit.state, const SearchInitial());
      cubit.close();
    });

    blocTest<SearchCubit, SearchState>(
      'loadInitialData emits SearchInitial with history and suggestions',
      build: () {
        when(() => mockRepository.getRecentSearches())
            .thenAnswer((_) async => ['Space', 'Nebula']);
        when(() => mockRepository.getSuggestions())
            .thenAnswer((_) async => sampleSuggestions);
        return SearchCubit(mockRepository);
      },
      act: (cubit) => cubit.loadInitialData(),
      expect: () => [
        const SearchInitial(
          recentSearches: ['Space', 'Nebula'],
          popularSearches: ['8K Ultra', 'Cyberpunk'],
          suggestedTags: ['space', 'nature'],
          suggestedCategories: ['Sci-Fi', 'Nature'],
        ),
      ],
    );

    blocTest<SearchCubit, SearchState>(
      'search with results emits [SearchLoading, SearchLoaded] and saves search',
      build: () {
        when(() => mockRepository.searchWallpapers(
              query: any(named: 'query'),
              filter: any(named: 'filter'),
              page: any(named: 'page'),
              limit: any(named: 'limit'),
            )).thenAnswer((_) async => sampleBundle);
        when(() => mockRepository.saveRecentSearch(any())).thenAnswer((_) async {});
        return SearchCubit(mockRepository);
      },
      act: (cubit) => cubit.search('Neon'),
      expect: () => [
        const SearchLoading(query: 'Neon'),
        const SearchLoaded(
          query: 'Neon',
          wallpapers: [sampleWallpaper],
          page: 1,
          totalCount: 1,
          hasReachedMax: true,
        ),
      ],
      verify: (_) {
        verify(() => mockRepository.saveRecentSearch('Neon')).called(1);
      },
    );

    blocTest<SearchCubit, SearchState>(
      'search with empty results emits [SearchLoading, SearchEmpty]',
      build: () {
        when(() => mockRepository.searchWallpapers(
              query: any(named: 'query'),
              filter: any(named: 'filter'),
              page: any(named: 'page'),
              limit: any(named: 'limit'),
            )).thenAnswer((_) async => const SearchResultBundle(
              wallpapers: [],
              page: 1,
              total: 0,
              totalPages: 1,
              hasNext: false,
            ));
        when(() => mockRepository.getSuggestions())
            .thenAnswer((_) async => sampleSuggestions);
        when(() => mockRepository.saveRecentSearch(any())).thenAnswer((_) async {});
        return SearchCubit(mockRepository);
      },
      act: (cubit) => cubit.search('NonExistentTerm'),
      expect: () => [
        const SearchLoading(query: 'NonExistentTerm'),
        const SearchEmpty(
          query: 'NonExistentTerm',
          suggestions: ['8K Ultra', 'Cyberpunk'],
        ),
      ],
    );

    blocTest<SearchCubit, SearchState>(
      'search failure emits [SearchLoading, SearchError]',
      build: () {
        when(() => mockRepository.searchWallpapers(
              query: any(named: 'query'),
              filter: any(named: 'filter'),
              page: any(named: 'page'),
              limit: any(named: 'limit'),
            )).thenThrow(Exception('Network timeout'));
        return SearchCubit(mockRepository);
      },
      act: (cubit) => cubit.search('Space'),
      expect: () => [
        const SearchLoading(query: 'Space'),
        isA<SearchError>(),
      ],
    );
  });
}
