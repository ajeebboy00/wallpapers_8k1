import 'package:flutter/material.dart';
import 'package:wallpapers_8k1/core/theme/app_colors.dart';
import '../../domain/search_filter.dart';

class SearchFilterModal extends StatefulWidget {
  final SearchFilter initialFilter;
  final Function(SearchFilter) onApply;

  const SearchFilterModal({
    super.key,
    required this.initialFilter,
    required this.onApply,
  });

  static Future<void> show(
    BuildContext context, {
    required SearchFilter initialFilter,
    required Function(SearchFilter) onApply,
  }) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.darkSurface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => SearchFilterModal(
        initialFilter: initialFilter,
        onApply: onApply,
      ),
    );
  }

  @override
  State<SearchFilterModal> createState() => _SearchFilterModalState();
}

class _SearchFilterModalState extends State<SearchFilterModal> {
  late String? _selectedResolution;
  late String? _selectedOrientation;
  late String? _selectedColor;
  late bool? _selectedPremium;
  late String _selectedSort;

  final List<String> _resolutions = ['8K', '4K', '2K', 'FHD'];
  final Map<String, String> _orientations = {
    'portrait': 'Portrait',
    'landscape': 'Landscape',
    'square': 'Square',
  };

  final List<Map<String, dynamic>> _colorPalette = [
    {'name': 'Purple', 'hex': '#8B5CF6', 'color': Color(0xFF8B5CF6)},
    {'name': 'Cyan', 'hex': '#06B6D4', 'color': Color(0xFF06B6D4)},
    {'name': 'Green', 'hex': '#10B981', 'color': Color(0xFF10B981)},
    {'name': 'Red', 'hex': '#EF4444', 'color': Color(0xFFEF4444)},
    {'name': 'Orange', 'hex': '#F97316', 'color': Color(0xFFF97316)},
    {'name': 'Gold', 'hex': '#F59E0B', 'color': Color(0xFFF59E0B)},
    {'name': 'AMOLED', 'hex': '#0A0A0C', 'color': Color(0xFF18181B)},
  ];

  final Map<String, String> _sortOptions = {
    'relevance': 'Relevance',
    'newest': 'Newest',
    'downloads': 'Downloads',
    'trending': 'Trending',
    'views': 'Views',
  };

  @override
  void initState() {
    super.initState();
    _selectedResolution = widget.initialFilter.resolution;
    _selectedOrientation = widget.initialFilter.orientation;
    _selectedColor = widget.initialFilter.color;
    _selectedPremium = widget.initialFilter.isPremium;
    _selectedSort = widget.initialFilter.sort;
  }

  void _apply() {
    final updated = widget.initialFilter.copyWith(
      resolution: _selectedResolution,
      clearResolution: _selectedResolution == null,
      orientation: _selectedOrientation,
      clearOrientation: _selectedOrientation == null,
      color: _selectedColor,
      clearColor: _selectedColor == null,
      isPremium: _selectedPremium,
      clearPremium: _selectedPremium == null,
      sort: _selectedSort,
    );
    widget.onApply(updated);
    Navigator.of(context).pop();
  }

  void _reset() {
    setState(() {
      _selectedResolution = null;
      _selectedOrientation = null;
      _selectedColor = null;
      _selectedPremium = null;
      _selectedSort = 'relevance';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.85,
      ),
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 16,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Drag handle
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.white24,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Advanced Search Filters',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                TextButton(
                  onPressed: _reset,
                  child: const Text(
                    'Reset',
                    style: TextStyle(color: AppColors.textDarkSecondary),
                  ),
                ),
              ],
            ),
            const Divider(color: AppColors.darkBorder),
            const SizedBox(height: 12),

            // Dominant Color Filter
            const Text(
              'Dominant Color Tone',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.white),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                ChoiceChip(
                  label: const Text('Any Color'),
                  selected: _selectedColor == null,
                  onSelected: (_) => setState(() => _selectedColor = null),
                ),
                ..._colorPalette.map((cp) {
                  final isSelected = _selectedColor == cp['hex'];
                  final Color c = cp['color'] as Color;
                  return ChoiceChip(
                    avatar: CircleAvatar(backgroundColor: c, radius: 6),
                    label: Text(cp['name'] as String),
                    selected: isSelected,
                    selectedColor: AppColors.primary,
                    onSelected: (val) => setState(() => _selectedColor = val ? (cp['hex'] as String) : null),
                  );
                }),
              ],
            ),
            const SizedBox(height: 16),

            // Resolution
            const Text(
              'Resolution Tier',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.white),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: [
                ChoiceChip(
                  label: const Text('All'),
                  selected: _selectedResolution == null,
                  onSelected: (_) => setState(() => _selectedResolution = null),
                ),
                ..._resolutions.map((res) {
                  final isSelected = _selectedResolution == res;
                  return ChoiceChip(
                    label: Text(res),
                    selected: isSelected,
                    selectedColor: AppColors.primary,
                    onSelected: (val) => setState(() => _selectedResolution = val ? res : null),
                  );
                }),
              ],
            ),
            const SizedBox(height: 16),

            // Orientation
            const Text(
              'Orientation',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.white),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: [
                ChoiceChip(
                  label: const Text('All'),
                  selected: _selectedOrientation == null,
                  onSelected: (_) => setState(() => _selectedOrientation = null),
                ),
                ..._orientations.entries.map((entry) {
                  final isSelected = _selectedOrientation == entry.key;
                  return ChoiceChip(
                    label: Text(entry.value),
                    selected: isSelected,
                    selectedColor: AppColors.primary,
                    onSelected: (val) => setState(() => _selectedOrientation = val ? entry.key : null),
                  );
                }),
              ],
            ),
            const SizedBox(height: 16),

            // VIP Pro Tier Filter
            const Text(
              'Access Tier',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.white),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: [
                ChoiceChip(
                  label: const Text('All Access'),
                  selected: _selectedPremium == null,
                  onSelected: (_) => setState(() => _selectedPremium = null),
                ),
                ChoiceChip(
                  avatar: const Icon(Icons.workspace_premium, size: 14, color: Colors.amberAccent),
                  label: const Text('Pro VIP Only'),
                  selected: _selectedPremium == true,
                  selectedColor: AppColors.primary,
                  onSelected: (val) => setState(() => _selectedPremium = val ? true : null),
                ),
                ChoiceChip(
                  label: const Text('Free Only'),
                  selected: _selectedPremium == false,
                  selectedColor: AppColors.primary,
                  onSelected: (val) => setState(() => _selectedPremium = val ? false : null),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Sort by
            const Text(
              'Sort By',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.white),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: _sortOptions.entries.map((entry) {
                final isSelected = _selectedSort == entry.key;
                return ChoiceChip(
                  label: Text(entry.value),
                  selected: isSelected,
                  selectedColor: AppColors.primary,
                  onSelected: (val) {
                    if (val) setState(() => _selectedSort = entry.key);
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 24),

            // Action Buttons
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                onPressed: _apply,
                child: const Text('Apply Filters', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
