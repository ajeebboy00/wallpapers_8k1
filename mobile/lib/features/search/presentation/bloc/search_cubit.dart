import 'package:flutter_bloc/flutter_bloc.dart';
import '../../data/search_remote_data_source.dart';
import '../../data/search_repository.dart';
import '../../domain/search_filter.dart';
import 'search_state.dart';

class SearchCubit extends Cubit<SearchState> {
  final ISearchRepository _repository;

  SearchCubit(this._repository) : super(const SearchInitial());

  String _currentQuery = '';
  SearchFilter _currentFilter = const SearchFilter();

  String get currentQuery => _currentQuery;
  SearchFilter get currentFilter => _currentFilter;

  Future<void> loadInitialData() async {
    try {
      final recents = await _repository.getRecentSearches();
      final suggestions = await _repository.getSuggestions();

      emit(SearchInitial(
        recentSearches: recents,
        popularSearches: suggestions.popularSearches,
        suggestedTags: suggestions.suggestedTags,
        suggestedCategories: suggestions.suggestedCategories,
      ));
    } catch (_) {
      emit(const SearchInitial());
    }
  }

  Future<void> search(
    String query, {
    SearchFilter? filter,
  }) async {
    _currentQuery = query.trim();
    if (filter != null) {
      _currentFilter = filter;
    }

    if (_currentQuery.isEmpty && !_currentFilter.hasActiveFilters) {
      await loadInitialData();
      return;
    }

    emit(SearchLoading(
      query: _currentQuery,
      filter: _currentFilter,
      previousWallpapers: state is SearchLoaded ? (state as SearchLoaded).wallpapers : const [],
    ));

    try {
      final result = await _repository.searchWallpapers(
        query: _currentQuery.isNotEmpty ? _currentQuery : null,
        filter: _currentFilter,
        page: 1,
        limit: 20,
      );

      if (_currentQuery.isNotEmpty) {
        await _repository.saveRecentSearch(_currentQuery);
      }

      if (result.wallpapers.isEmpty) {
        final suggestions = await _repository.getSuggestions();
        emit(SearchEmpty(
          query: _currentQuery,
          filter: _currentFilter,
          suggestions: suggestions.popularSearches,
        ));
      } else {
        emit(SearchLoaded(
          query: _currentQuery,
          wallpapers: result.wallpapers,
          filter: _currentFilter,
          page: 1,
          totalCount: result.total,
          hasReachedMax: !result.hasNext,
        ));
      }
    } catch (e) {
      emit(SearchError(
        message: 'Failed to search wallpapers: ${e.toString().replaceAll("Exception: ", "")}',
        query: _currentQuery,
        filter: _currentFilter,
      ));
    }
  }

  Future<void> loadMore() async {
    final currentState = state;
    if (currentState is! SearchLoaded) return;
    if (currentState.hasReachedMax || currentState.isLoadingMore) return;

    emit(currentState.copyWith(isLoadingMore: true));

    try {
      final nextPage = currentState.page + 1;
      final result = await _repository.searchWallpapers(
        query: _currentQuery.isNotEmpty ? _currentQuery : null,
        filter: _currentFilter,
        page: nextPage,
        limit: 20,
      );

      final combined = [...currentState.wallpapers, ...result.wallpapers];

      emit(currentState.copyWith(
        wallpapers: combined,
        page: nextPage,
        hasReachedMax: !result.hasNext || result.wallpapers.isEmpty,
        isLoadingMore: false,
      ));
    } catch (e) {
      emit(currentState.copyWith(isLoadingMore: false));
    }
  }

  void applyFilter(SearchFilter filter) {
    _currentFilter = filter;
    search(_currentQuery, filter: _currentFilter);
  }

  void clearFilter() {
    _currentFilter = const SearchFilter();
    search(_currentQuery, filter: _currentFilter);
  }

  Future<void> removeRecentSearch(String term) async {
    await _repository.removeRecentSearch(term);
    if (state is SearchInitial) {
      final current = (state as SearchInitial);
      final updated = current.recentSearches.where((e) => e != term).toList();
      emit(SearchInitial(
        recentSearches: updated,
        popularSearches: current.popularSearches,
        suggestedTags: current.suggestedTags,
        suggestedCategories: current.suggestedCategories,
      ));
    }
  }

  Future<void> clearRecentSearches() async {
    await _repository.clearRecentSearches();
    if (state is SearchInitial) {
      final current = (state as SearchInitial);
      emit(SearchInitial(
        recentSearches: const [],
        popularSearches: current.popularSearches,
        suggestedTags: current.suggestedTags,
        suggestedCategories: current.suggestedCategories,
      ));
    }
  }
}
