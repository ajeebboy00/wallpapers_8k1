import 'package:equatable/equatable.dart';

class SearchFilter extends Equatable {
  final String? resolution;
  final String? orientation;
  final String? categorySlug;
  final String? tagSlug;
  final String? color;
  final bool? isPremium;
  final bool? isAiGenerated;
  final String sort;
  final String order;

  const SearchFilter({
    this.resolution,
    this.orientation,
    this.categorySlug,
    this.tagSlug,
    this.color,
    this.isPremium,
    this.isAiGenerated,
    this.sort = 'relevance',
    this.order = 'desc',
  });

  bool get hasActiveFilters =>
      resolution != null ||
      orientation != null ||
      categorySlug != null ||
      tagSlug != null ||
      color != null ||
      isPremium != null ||
      isAiGenerated != null ||
      sort != 'relevance';

  int get activeFilterCount {
    int count = 0;
    if (resolution != null) count++;
    if (orientation != null) count++;
    if (categorySlug != null) count++;
    if (tagSlug != null) count++;
    if (color != null) count++;
    if (isPremium != null) count++;
    if (isAiGenerated != null) count++;
    if (sort != 'relevance') count++;
    return count;
  }

  SearchFilter copyWith({
    String? resolution,
    bool clearResolution = false,
    String? orientation,
    bool clearOrientation = false,
    String? categorySlug,
    bool clearCategory = false,
    String? tagSlug,
    bool clearTag = false,
    String? color,
    bool clearColor = false,
    bool? isPremium,
    bool clearPremium = false,
    bool? isAiGenerated,
    bool clearAiGenerated = false,
    String? sort,
    String? order,
  }) {
    return SearchFilter(
      resolution: clearResolution ? null : (resolution ?? this.resolution),
      orientation: clearOrientation ? null : (orientation ?? this.orientation),
      categorySlug: clearCategory ? null : (categorySlug ?? this.categorySlug),
      tagSlug: clearTag ? null : (tagSlug ?? this.tagSlug),
      color: clearColor ? null : (color ?? this.color),
      isPremium: clearPremium ? null : (isPremium ?? this.isPremium),
      isAiGenerated: clearAiGenerated ? null : (isAiGenerated ?? this.isAiGenerated),
      sort: sort ?? this.sort,
      order: order ?? this.order,
    );
  }

  SearchFilter clear() {
    return const SearchFilter();
  }

  Map<String, dynamic> toQueryParams() {
    final Map<String, dynamic> params = {};
    if (resolution != null && resolution!.isNotEmpty) {
      params['resolution'] = resolution;
    }
    if (orientation != null && orientation!.isNotEmpty) {
      params['orientation'] = orientation;
    }
    if (categorySlug != null && categorySlug!.isNotEmpty) {
      params['category'] = categorySlug;
    }
    if (tagSlug != null && tagSlug!.isNotEmpty) {
      params['tag'] = tagSlug;
    }
    if (color != null && color!.isNotEmpty) {
      params['color'] = color;
    }
    if (isPremium != null) {
      params['is_premium'] = isPremium;
    }
    if (isAiGenerated != null) {
      params['is_ai_generated'] = isAiGenerated;
    }
    if (sort.isNotEmpty) {
      params['sort'] = sort;
    }
    if (order.isNotEmpty) {
      params['order'] = order;
    }
    return params;
  }

  @override
  List<Object?> get props => [
        resolution,
        orientation,
        categorySlug,
        tagSlug,
        color,
        isPremium,
        isAiGenerated,
        sort,
        order,
      ];
}
