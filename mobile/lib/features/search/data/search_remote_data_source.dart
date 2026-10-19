import 'package:wallpapers_8k1/core/network/api_client.dart';
import 'package:wallpapers_8k1/shared/models/wallpaper_model.dart';
import '../domain/search_filter.dart';

class SearchResultBundle {
  final List<WallpaperModel> wallpapers;
  final int page;
  final int total;
  final int totalPages;
  final bool hasNext;

  const SearchResultBundle({
    required this.wallpapers,
    required this.page,
    required this.total,
    required this.totalPages,
    required this.hasNext,
  });
}

class SearchSuggestionsBundle {
  final List<String> popularSearches;
  final List<String> suggestedTags;
  final List<String> suggestedCategories;

  const SearchSuggestionsBundle({
    this.popularSearches = const [],
    this.suggestedTags = const [],
    this.suggestedCategories = const [],
  });

  factory SearchSuggestionsBundle.fromJson(Map<String, dynamic> json) {
    return SearchSuggestionsBundle(
      popularSearches: (json['popular_searches'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          const [],
      suggestedTags: (json['suggested_tags'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          const [],
      suggestedCategories: (json['suggested_categories'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          const [],
    );
  }
}

class SearchRemoteDataSource {
  final ApiClient _apiClient;

  SearchRemoteDataSource(this._apiClient);

  Future<SearchResultBundle> searchWallpapers({
    String? query,
    SearchFilter filter = const SearchFilter(),
    int page = 1,
    int limit = 20,
  }) async {
    final queryParams = filter.toQueryParams();
    if (query != null && query.trim().isNotEmpty) {
      queryParams['q'] = query.trim();
    }
    queryParams['page'] = page;
    queryParams['limit'] = limit;

    final response = await _apiClient.get(
      '/search',
      queryParameters: queryParams,
    );

    final rawData = response.data['data'] as List<dynamic>? ?? [];
    final wallpapers = rawData
        .map((item) => WallpaperModel.fromJson(item as Map<String, dynamic>))
        .toList();

    final meta = response.data['meta'] as Map<String, dynamic>? ?? {};
    final total = (meta['total'] as num?)?.toInt() ?? wallpapers.length;
    final totalPages = (meta['total_pages'] as num?)?.toInt() ?? 1;
    final hasNext = (meta['has_next'] as bool?) ?? (page < totalPages);

    return SearchResultBundle(
      wallpapers: wallpapers,
      page: page,
      total: total,
      totalPages: totalPages,
      hasNext: hasNext,
    );
  }

  Future<SearchSuggestionsBundle> getSuggestions({String? query, int limit = 10}) async {
    final Map<String, dynamic> queryParams = {'limit': limit};
    if (query != null && query.trim().isNotEmpty) {
      queryParams['q'] = query.trim();
    }

    final response = await _apiClient.get(
      '/search/suggestions',
      queryParameters: queryParams,
    );

    final rawData = response.data['data'] as Map<String, dynamic>? ?? {};
    return SearchSuggestionsBundle.fromJson(rawData);
  }
}
