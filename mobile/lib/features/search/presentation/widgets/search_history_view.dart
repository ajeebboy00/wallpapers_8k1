import 'package:flutter/material.dart';
import 'package:wallpapers_8k1/core/theme/app_colors.dart';

class SearchHistoryView extends StatelessWidget {
  final List<String> recentSearches;
  final List<String> popularSearches;
  final List<String> suggestedTags;
  final List<String> suggestedCategories;
  final Function(String) onTermSelected;
  final Function(String) onDeleteRecent;
  final VoidCallback onClearAllRecent;

  const SearchHistoryView({
    super.key,
    required this.recentSearches,
    required this.popularSearches,
    required this.suggestedTags,
    required this.suggestedCategories,
    required this.onTermSelected,
    required this.onDeleteRecent,
    required this.onClearAllRecent,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Recent Searches
          if (recentSearches.isNotEmpty) ...[
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Row(
                  children: [
                    Icon(Icons.history_rounded, size: 20, color: AppColors.primary),
                    SizedBox(width: 8),
                    Text(
                      'Recent Searches',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ],
                ),
                TextButton(
                  onPressed: onClearAllRecent,
                  style: TextButton.styleFrom(
                    visualDensity: VisualDensity.compact,
                    foregroundColor: AppColors.textTertiary,
                  ),
                  child: const Text('Clear all', style: TextStyle(fontSize: 13)),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: recentSearches.map((term) {
                return InputChip(
                  label: Text(term, style: const TextStyle(fontSize: 13)),
                  backgroundColor: AppColors.surface,
                  deleteIcon: const Icon(Icons.close, size: 16, color: AppColors.textTertiary),
                  onDeleted: () => onDeleteRecent(term),
                  onPressed: () => onTermSelected(term),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(20),
                    side: const BorderSide(color: Colors.white12),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 24),
          ],

          // 2. Popular Searches
          if (popularSearches.isNotEmpty) ...[
            const Row(
              children: [
                Icon(Icons.local_fire_department_rounded, size: 20, color: Colors.orangeAccent),
                SizedBox(width: 8),
                Text(
                  'Popular Searches',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: popularSearches.map((term) {
                return ActionChip(
                  avatar: const Icon(Icons.search, size: 14, color: AppColors.primary),
                  label: Text(term, style: const TextStyle(fontSize: 13, color: AppColors.textPrimary)),
                  backgroundColor: AppColors.surface,
                  onPressed: () => onTermSelected(term),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(20),
                    side: const BorderSide(color: Colors.white10),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 24),
          ],

          // 3. Trending Tags
          if (suggestedTags.isNotEmpty) ...[
            const Row(
              children: [
                Icon(Icons.tag_rounded, size: 20, color: AppColors.accent),
                SizedBox(width: 8),
                Text(
                  'Trending Tags',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: suggestedTags.map((tag) {
                return ActionChip(
                  label: Text('#$tag', style: const TextStyle(fontSize: 13, color: AppColors.textPrimary)),
                  backgroundColor: AppColors.surfaceElevated,
                  onPressed: () => onTermSelected(tag),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(20),
                    side: const BorderSide(color: Colors.white10),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 24),
          ],

          // 4. Categories Quick Access
          if (suggestedCategories.isNotEmpty) ...[
            const Row(
              children: [
                Icon(Icons.category_outlined, size: 20, color: Colors.cyanAccent),
                SizedBox(width: 8),
                Text(
                  'Explore Categories',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: suggestedCategories.map((cat) {
                return ActionChip(
                  label: Text(cat, style: const TextStyle(fontSize: 13, color: AppColors.textPrimary)),
                  backgroundColor: AppColors.surface,
                  onPressed: () => onTermSelected(cat),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(20),
                    side: const BorderSide(color: Colors.white12),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 32),
          ],
        ],
      ),
    );
  }
}
