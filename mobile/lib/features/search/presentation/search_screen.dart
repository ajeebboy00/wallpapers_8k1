import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/network/api_client.dart';
import '../../../../core/storage/secure_storage_service.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/widgets/state_views.dart';
import '../../data/search_remote_data_source.dart';
import '../../data/search_repository.dart';
import '../../domain/search_filter.dart';
import 'bloc/search_cubit.dart';
import 'bloc/search_state.dart';
import 'widgets/search_empty_view.dart';
import 'widgets/search_filter_modal.dart';
import 'widgets/search_history_view.dart';
import 'widgets/search_results_grid.dart';
import 'widgets/search_shimmer_view.dart';

class SearchScreen extends StatelessWidget {
  final String? initialQuery;
  final String? initialCategory;

  const SearchScreen({
    super.key,
    this.initialQuery,
    this.initialCategory,
  });

  @override
  Widget build(BuildContext context) {
    return BlocProvider<SearchCubit>(
      create: (context) {
        final storage = SecureStorageService();
        final apiClient = ApiClient(storage: storage);
        final dataSource = SearchRemoteDataSource(apiClient);
        final repository = SearchRepository(dataSource, storage);
        final cubit = SearchCubit(repository);

        if ((initialQuery != null && initialQuery!.isNotEmpty) ||
            (initialCategory != null && initialCategory!.isNotEmpty)) {
          final filter = SearchFilter(categorySlug: initialCategory);
          cubit.search(initialQuery ?? '', filter: filter);
        } else {
          cubit.loadInitialData();
        }

        return cubit;
      },
      child: _SearchScreenContent(
        initialQuery: initialQuery,
      ),
    );
  }
}

class _SearchScreenContent extends StatefulWidget {
  final String? initialQuery;

  const _SearchScreenContent({this.initialQuery});

  @override
  State<_SearchScreenContent> createState() => _SearchScreenContentState();
}

class _SearchScreenContentState extends State<_SearchScreenContent> {
  late final TextEditingController _searchController;
  Timer? _debounceTimer;

  @override
  void initState() {
    super.initState();
    _searchController = TextEditingController(text: widget.initialQuery ?? '');
  }

  @override
  void dispose() {
    _debounceTimer?.cancel();
    _searchController.dispose();
    super.dispose();
  }

  void _onQueryChanged(String query) {
    _debounceTimer?.cancel();
    _debounceTimer = Timer(const Duration(milliseconds: 400), () {
      if (mounted) {
        context.read<SearchCubit>().search(query);
      }
    });
    setState(() {}); // Updates clear button visibility
  }

  void _onSearchSubmitted(String query) {
    _debounceTimer?.cancel();
    context.read<SearchCubit>().search(query);
  }

  void _clearSearch() {
    _searchController.clear();
    _debounceTimer?.cancel();
    context.read<SearchCubit>().search('');
    setState(() {});
  }

  void _openFilterModal(BuildContext context, SearchFilter currentFilter) {
    SearchFilterModal.show(
      context,
      initialFilter: currentFilter,
      onApply: (newFilter) {
        context.read<SearchCubit>().applyFilter(newFilter);
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
          onPressed: () {
            if (context.canPop()) {
              context.pop();
            } else {
              context.go('/');
            }
          },
        ),
        titleSpacing: 0,
        title: Container(
          height: 44,
          margin: const EdgeInsets.only(right: 8),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(22),
            border: Border.all(color: Colors.white12),
          ),
          child: TextField(
            controller: _searchController,
            autofocus: widget.initialQuery == null,
            textInputAction: TextInputAction.search,
            onChanged: _onQueryChanged,
            onSubmitted: _onSearchSubmitted,
            style: const TextStyle(color: AppColors.textPrimary, fontSize: 14),
            decoration: InputDecoration(
              hintText: 'Search 8K wallpapers, tags, styles...',
              hintStyle: const TextStyle(color: AppColors.textTertiary, fontSize: 13),
              prefixIcon: const Icon(Icons.search_rounded, size: 20, color: AppColors.textTertiary),
              suffixIcon: _searchController.text.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.close_rounded, size: 18, color: AppColors.textSecondary),
                      onPressed: _clearSearch,
                    )
                  : null,
              contentPadding: const EdgeInsets.symmetric(vertical: 10),
              border: InputBorder.none,
              enabledBorder: InputBorder.none,
              focusedBorder: InputBorder.none,
            ),
          ),
        ),
        actions: [
          BlocBuilder<SearchCubit, SearchState>(
            builder: (context, state) {
              final activeCount = context.read<SearchCubit>().currentFilter.activeFilterCount;
              return Stack(
                alignment: Alignment.center,
                children: [
                  IconButton(
                    icon: Icon(
                      Icons.tune_rounded,
                      color: activeCount > 0 ? AppColors.primary : AppColors.textSecondary,
                    ),
                    tooltip: 'Filters',
                    onPressed: () => _openFilterModal(
                      context,
                      context.read<SearchCubit>().currentFilter,
                    ),
                  ),
                  if (activeCount > 0)
                    Positioned(
                      top: 8,
                      right: 8,
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: const BoxDecoration(
                          color: AppColors.primary,
                          shape: BoxShape.circle,
                        ),
                        child: Text(
                          '$activeCount',
                          style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.white),
                        ),
                      ),
                    ),
                ],
              );
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: BlocBuilder<SearchCubit, SearchState>(
        builder: (context, state) {
          if (state is SearchLoading) {
            return const SearchShimmerView();
          }

          if (state is SearchError) {
            return ErrorView(
              message: state.message,
              onRetry: () => context.read<SearchCubit>().search(_searchController.text),
            );
          }

          if (state is SearchEmpty) {
            return SearchEmptyView(
              query: state.query,
              filter: state.filter,
              suggestions: state.suggestions,
              onSuggestionSelected: (term) {
                _searchController.text = term;
                context.read<SearchCubit>().search(term);
              },
              onResetFilters: () {
                context.read<SearchCubit>().clearFilter();
              },
            );
          }

          if (state is SearchLoaded) {
            return SearchResultsGrid(
              wallpapers: state.wallpapers,
              filter: state.filter,
              totalCount: state.totalCount,
              hasReachedMax: state.hasReachedMax,
              isLoadingMore: state.isLoadingMore,
              onLoadMore: () => context.read<SearchCubit>().loadMore(),
              onFilterChanged: (filter) => context.read<SearchCubit>().applyFilter(filter),
            );
          }

          if (state is SearchInitial) {
            return SearchHistoryView(
              recentSearches: state.recentSearches,
              popularSearches: state.popularSearches,
              suggestedTags: state.suggestedTags,
              suggestedCategories: state.suggestedCategories,
              onTermSelected: (term) {
                _searchController.text = term;
                context.read<SearchCubit>().search(term);
              },
              onDeleteRecent: (term) => context.read<SearchCubit>().removeRecentSearch(term),
              onClearAllRecent: () => context.read<SearchCubit>().clearRecentSearches(),
            );
          }

          return const SizedBox.shrink();
        },
      ),
    );
  }
}
