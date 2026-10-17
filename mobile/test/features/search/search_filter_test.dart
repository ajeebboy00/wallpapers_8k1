import 'package:flutter_test/flutter_test.dart';
import 'package:wallpapers_8k1/features/search/domain/search_filter.dart';

void main() {
  group('SearchFilter Unit Tests', () {
    test('default SearchFilter has no active filters', () {
      const filter = SearchFilter();
      expect(filter.hasActiveFilters, isFalse);
      expect(filter.activeFilterCount, 0);
      expect(filter.sort, 'relevance');
      expect(filter.order, 'desc');
      expect(filter.toQueryParams(), {
        'sort': 'relevance',
        'order': 'desc',
      });
    });

    test('SearchFilter detects active resolution and orientation filters', () {
      final filter = const SearchFilter().copyWith(
        resolution: '8K',
        orientation: 'portrait',
      );

      expect(filter.hasActiveFilters, isTrue);
      expect(filter.activeFilterCount, 2);
      expect(filter.resolution, '8K');
      expect(filter.orientation, 'portrait');

      final params = filter.toQueryParams();
      expect(params['resolution'], '8K');
      expect(params['orientation'], 'portrait');
      expect(params['sort'], 'relevance');
    });

    test('SearchFilter clearing single filter via copyWith', () {
      final filter = const SearchFilter().copyWith(
        resolution: '4K',
        sort: 'downloads',
      );
      expect(filter.activeFilterCount, 2);

      final cleared = filter.copyWith(clearResolution: true);
      expect(cleared.resolution, isNull);
      expect(cleared.sort, 'downloads');
      expect(cleared.activeFilterCount, 1);
    });

    test('SearchFilter full clear returns pristine default', () {
      final filter = const SearchFilter(
        resolution: '8K',
        orientation: 'landscape',
        categorySlug: 'space',
        sort: 'trending',
      );
      expect(filter.hasActiveFilters, isTrue);

      final reset = filter.clear();
      expect(reset.hasActiveFilters, isFalse);
      expect(reset.resolution, isNull);
      expect(reset.orientation, isNull);
      expect(reset.categorySlug, isNull);
      expect(reset.sort, 'relevance');
    });
  });
}
