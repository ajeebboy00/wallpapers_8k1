import 'package:flutter/material.dart';
import 'package:wallpapers_8k1/core/theme/app_colors.dart';
import '../../domain/search_filter.dart';

class SearchEmptyView extends StatelessWidget {
  final String query;
  final SearchFilter filter;
  final List<String> suggestions;
  final Function(String) onSuggestionSelected;
  final VoidCallback onResetFilters;

  const SearchEmptyView({
    super.key,
    required this.query,
    required this.filter,
    required this.suggestions,
    required this.onSuggestionSelected,
    required this.onResetFilters,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 32.0, vertical: 24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.surface,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.search_off_rounded,
                size: 56,
                color: AppColors.textTertiary,
              ),
            ),
            const SizedBox(height: 20),
            Text(
              query.isNotEmpty ? 'No results for "$query"' : 'No wallpapers found',
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Try checking your spelling, using more general keywords, or resetting active filters.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 14,
                color: AppColors.textSecondary,
                height: 1.4,
              ),
            ),
            const SizedBox(height: 20),

            if (filter.hasActiveFilters) ...[
              OutlinedButton.icon(
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppColors.primary,
                  side: const BorderSide(color: AppColors.primary),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onPressed: onResetFilters,
                icon: const Icon(Icons.refresh_rounded, size: 16),
                label: const Text('Reset All Filters'),
              ),
              const SizedBox(height: 24),
            ],

            if (suggestions.isNotEmpty) ...[
              const Text(
                'Try searching for:',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textTertiary,
                ),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                alignment: WrapAlignment.center,
                children: suggestions.take(6).map((term) {
                  return ActionChip(
                    label: Text(term, style: const TextStyle(fontSize: 12, color: AppColors.textPrimary)),
                    backgroundColor: AppColors.surface,
                    onPressed: () => onSuggestionSelected(term),
                  );
                }).toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
