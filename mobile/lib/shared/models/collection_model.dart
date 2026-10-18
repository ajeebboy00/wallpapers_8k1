import 'package:equatable/equatable.dart';

class CollectionModel extends Equatable {
  final String id;
  final String name;
  final String slug;
  final String? description;
  final String? coverImageUrl;
  final bool isFeatured;
  final bool isPublished;
  final int wallpaperCount;

  const CollectionModel({
    required this.id,
    required this.name,
    required this.slug,
    this.description,
    this.coverImageUrl,
    this.isFeatured = false,
    this.isPublished = true,
    this.wallpaperCount = 0,
  });

  factory CollectionModel.fromJson(Map<String, dynamic> json) {
    return CollectionModel(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      slug: json['slug'] as String? ?? '',
      description: json['description'] as String?,
      coverImageUrl: json['cover_image_url'] as String?,
      isFeatured: json['is_featured'] as bool? ?? false,
      isPublished: json['is_published'] as bool? ?? true,
      wallpaperCount: (json['wallpaper_count'] as num?)?.toInt() ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'slug': slug,
      'description': description,
      'cover_image_url': coverImageUrl,
      'is_featured': isFeatured,
      'is_published': isPublished,
      'wallpaper_count': wallpaperCount,
    };
  }

  @override
  List<Object?> get props => [
        id,
        name,
        slug,
        description,
        coverImageUrl,
        isFeatured,
        isPublished,
        wallpaperCount,
      ];
}
