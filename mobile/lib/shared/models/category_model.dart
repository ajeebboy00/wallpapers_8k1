import 'package:equatable/equatable.dart';

class CategoryModel extends Equatable {
  final String id;
  final String name;
  final String slug;
  final String? description;
  final String? imageUrl;
  final int sortOrder;
  final bool isActive;
  final int wallpaperCount;

  const CategoryModel({
    required this.id,
    required this.name,
    required this.slug,
    this.description,
    this.imageUrl,
    this.sortOrder = 0,
    this.isActive = true,
    this.wallpaperCount = 0,
  });

  factory CategoryModel.fromJson(Map<String, dynamic> json) {
    return CategoryModel(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      slug: json['slug'] as String? ?? '',
      description: json['description'] as String?,
      imageUrl: json['image_url'] as String?,
      sortOrder: (json['sort_order'] as num?)?.toInt() ?? 0,
      isActive: json['is_active'] as bool? ?? true,
      wallpaperCount: (json['wallpaper_count'] as num?)?.toInt() ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'slug': slug,
      'description': description,
      'image_url': imageUrl,
      'sort_order': sortOrder,
      'is_active': isActive,
      'wallpaper_count': wallpaperCount,
    };
  }

  @override
  List<Object?> get props => [
        id,
        name,
        slug,
        description,
        imageUrl,
        sortOrder,
        isActive,
        wallpaperCount,
      ];
}
