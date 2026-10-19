import 'dart:convert';
import 'package:wallpapers_8k1/core/constants/app_constants.dart';
import 'package:wallpapers_8k1/core/storage/secure_storage_service.dart';
import '../domain/search_filter.dart';
import 'search_remote_data_source.dart';

abstract class ISearchRepository {
  Future<SearchResultBundle> searchWallpapers({
    String? query,
    SearchFilter filter = const SearchFilter(),
    int page = 1,
    int limit = 20,
  });

  Future<SearchSuggestionsBundle> getSuggestions({String? query, int limit = 10});

  Future<List<String>> getRecentSearches();

  Future<void> saveRecentSearch(String query);

  Future<void> removeRecentSearch(String query);

  Future<void> clearRecentSearches();
}

class SearchRepository implements ISearchRepository {
  final SearchRemoteDataSource _remoteDataSource;
  final ISecureStorageService _storage;

  static const int _maxRecentSearches = 10;

  SearchRepository(this._remoteDataSource, this._storage);

  @override
  Future<SearchResultBundle> searchWallpapers({
    String? query,
    SearchFilter filter = const SearchFilter(),
    int page = 1,
    int limit = 20,
  }) async {
    return await _remoteDataSource.searchWallpapers(
      query: query,
      filter: filter,
      page: page,
      limit: limit,
    );
  }

  @override
  Future<SearchSuggestionsBundle> getSuggestions({String? query, int limit = 10}) async {
    return await _remoteDataSource.getSuggestions(query: query, limit: limit);
  }

  @override
  Future<List<String>> getRecentSearches() async {
    try {
      final raw = await _storage.getString(AppConstants.recentSearchesKey);
      if (raw == null || raw.isEmpty) return [];
      final List<dynamic> decoded = jsonDecode(raw) as List<dynamic>;
      return decoded.map((e) => e.toString()).toList();
    } catch (_) {
      return [];
    }
  }

  @override
  Future<void> saveRecentSearch(String query) async {
    final clean = query.trim();
    if (clean.isEmpty) return;

    try {
      final current = await getRecentSearches();
      // Remove existing occurrence to place it at the front
      final updated = [clean, ...current.where((e) => e.toLowerCase() != clean.toLowerCase())];
      if (updated.length > _maxRecentSearches) {
        updated.removeRange(_maxRecentSearches, updated.length);
      }
      await _storage.setString(AppConstants.recentSearchesKey, jsonEncode(updated));
    } catch (_) {}
  }

  @override
  Future<void> removeRecentSearch(String query) async {
    try {
      final current = await getRecentSearches();
      final updated = current.where((e) => e.toLowerCase() != query.trim().toLowerCase()).toList();
      await _storage.setString(AppConstants.recentSearchesKey, jsonEncode(updated));
    } catch (_) {}
  }

  @override
  Future<void> clearRecentSearches() async {
    try {
      await _storage.delete(AppConstants.recentSearchesKey);
    } catch (_) {}
  }
}
