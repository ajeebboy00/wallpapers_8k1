import 'package:equatable/equatable.dart';
import 'package:wallpapers_8k1/shared/models/wallpaper_model.dart';
import '../../domain/search_filter.dart';

abstract class SearchState extends Equatable {
  const SearchState();

  @override
  List<Object?> get props => [];
}

class SearchInitial extends SearchState {
  final List<String> recentSearches;
  final List<String> popularSearches;
  final List<String> suggestedTags;
  final List<String> suggestedCategories;

  const SearchInitial({
    this.recentSearches = const [],
    this.popularSearches = const [],
    this.suggestedTags = const [],
    this.suggestedCategories = const [],
  });

  @override
  List<Object?> get props => [
        recentSearches,
        popularSearches,
        suggestedTags,
        suggestedCategories,
      ];
}

class SearchLoading extends SearchState {
  final String query;
  final SearchFilter filter;
  final List<WallpaperModel> previousWallpapers;

  const SearchLoading({
    this.query = '',
    this.filter = const SearchFilter(),
    this.previousWallpapers = const [],
  });

  @override
  List<Object?> get props => [query, filter, previousWallpapers];
}

class SearchLoaded extends SearchState {
  final String query;
  final List<WallpaperModel> wallpapers;
  final SearchFilter filter;
  final int page;
  final int totalCount;
  final bool hasReachedMax;
  final bool isLoadingMore;

  const SearchLoaded({
    required this.query,
    required this.wallpapers,
    this.filter = const SearchFilter(),
    this.page = 1,
    required this.totalCount,
    this.hasReachedMax = false,
    this.isLoadingMore = false,
  });

  SearchLoaded copyWith({
    String? query,
    List<WallpaperModel>? wallpapers,
    SearchFilter? filter,
    int? page,
    int? totalCount,
    bool? hasReachedMax,
    bool? isLoadingMore,
  }) {
    return SearchLoaded(
      query: query ?? this.query,
      wallpapers: wallpapers ?? this.wallpapers,
      filter: filter ?? this.filter,
      page: page ?? this.page,
      totalCount: totalCount ?? this.totalCount,
      hasReachedMax: hasReachedMax ?? this.hasReachedMax,
      isLoadingMore: isLoadingMore ?? this.isLoadingMore,
    );
  }

  @override
  List<Object?> get props => [
        query,
        wallpapers,
        filter,
        page,
        totalCount,
        hasReachedMax,
        isLoadingMore,
      ];
}

class SearchEmpty extends SearchState {
  final String query;
  final SearchFilter filter;
  final List<String> suggestions;

  const SearchEmpty({
    this.query = '',
    this.filter = const SearchFilter(),
    this.suggestions = const [],
  });

  @override
  List<Object?> get props => [query, filter, suggestions];
}

class SearchError extends SearchState {
  final String message;
  final String query;
  final SearchFilter filter;

  const SearchError({
    required this.message,
    this.query = '',
    this.filter = const SearchFilter(),
  });

  @override
  List<Object?> get props => [message, query, filter];
}
