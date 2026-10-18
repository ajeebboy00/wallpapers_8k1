import 'package:equatable/equatable.dart';
import 'category_model.dart';
import 'tag_model.dart';

class WallpaperModel extends Equatable {
  final String id;
  final String title;
  final String slug;
  final String? description;
  final String originalUrl;
  final String imageUrl;
  final String thumbnailUrl;
  final String previewUrl;
  final int width;
  final int height;
  final double aspectRatio;
  final int fileSize;
  final String fileFormat;
  final String resolution;
  final String categoryId;
  final String? uploaderId;
  final int viewCount;
  final int downloadCount;
  final int favoriteCount;
  final int shareCount;
  final bool isFeatured;
  final bool isTrending;
  final bool isDaily;
  final bool isPublished;
  final double trendingScore;
  final DateTime? createdAt;
  final DateTime? updatedAt;
  final CategoryModel? category;
  final List<TagModel> tags;
  final bool isFavorite;
  final String? dominantColor;
  final List<String> colorPalette;
  final bool isAiGenerated;
  final bool isPremium;
  final List<String> aiTags;
  final String? aiDescription;

  const WallpaperModel({
    required this.id,
    required this.title,
    required this.slug,
    this.description,
    required this.originalUrl,
    required this.imageUrl,
    required this.thumbnailUrl,
    required this.previewUrl,
    required this.width,
    required this.height,
    required this.aspectRatio,
    required this.fileSize,
    required this.fileFormat,
    required this.resolution,
    required this.categoryId,
    this.uploaderId,
    this.viewCount = 0,
    this.downloadCount = 0,
    this.favoriteCount = 0,
    this.shareCount = 0,
    this.isFeatured = false,
    this.isTrending = false,
    this.isDaily = false,
    this.isPublished = true,
    this.trendingScore = 0.0,
    this.createdAt,
    this.updatedAt,
    this.category,
    this.tags = const [],
    this.isFavorite = false,
    this.dominantColor,
    this.colorPalette = const [],
    this.isAiGenerated = false,
    this.isPremium = false,
    this.aiTags = const [],
    this.aiDescription,
  });

  factory WallpaperModel.fromJson(Map<String, dynamic> json) {
    return WallpaperModel(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      slug: json['slug'] as String? ?? '',
      description: json['description'] as String?,
      originalUrl: json['original_url'] as String? ?? '',
      imageUrl: json['image_url'] as String? ?? '',
      thumbnailUrl: json['thumbnail_url'] as String? ?? '',
      previewUrl: json['preview_url'] as String? ?? '',
      width: (json['width'] as num?)?.toInt() ?? 0,
      height: (json['height'] as num?)?.toInt() ?? 0,
      aspectRatio: (json['aspect_ratio'] as num?)?.toDouble() ?? 1.0,
      fileSize: (json['file_size'] as num?)?.toInt() ?? 0,
      fileFormat: json['file_format'] as String? ?? 'webp',
      resolution: json['resolution'] as String? ?? '8K',
      categoryId: json['category_id'] as String? ?? '',
      uploaderId: json['uploader_id'] as String?,
      viewCount: (json['view_count'] as num?)?.toInt() ?? 0,
      downloadCount: (json['download_count'] as num?)?.toInt() ?? 0,
      favoriteCount: (json['favorite_count'] as num?)?.toInt() ?? 0,
      shareCount: (json['share_count'] as num?)?.toInt() ?? 0,
      isFeatured: json['is_featured'] as bool? ?? false,
      isTrending: json['is_trending'] as bool? ?? false,
      isDaily: json['is_daily'] as bool? ?? false,
      isPublished: json['is_published'] as bool? ?? true,
      trendingScore: (json['trending_score'] as num?)?.toDouble() ?? 0.0,
      createdAt: json['created_at'] != null ? DateTime.tryParse(json['created_at'] as String) : null,
      updatedAt: json['updated_at'] != null ? DateTime.tryParse(json['updated_at'] as String) : null,
      category: json['category'] != null ? CategoryModel.fromJson(json['category'] as Map<String, dynamic>) : null,
      tags: json['tags'] != null
          ? (json['tags'] as List).map((t) => TagModel.fromJson(t as Map<String, dynamic>)).toList()
          : const [],
      isFavorite: json['is_favorite'] as bool? ?? false,
      dominantColor: json['dominant_color'] as String?,
      colorPalette: (json['color_palette'] as List<dynamic>?)?.map((c) => c.toString()).toList() ?? const [],
      isAiGenerated: json['is_ai_generated'] as bool? ?? false,
      isPremium: json['is_premium'] as bool? ?? false,
      aiTags: (json['ai_tags'] as List<dynamic>?)?.map((t) => t.toString()).toList() ?? const [],
      aiDescription: json['ai_description'] as String?,
    );
  }

  WallpaperModel copyWith({
    String? id,
    String? title,
    String? slug,
    String? description,
    String? originalUrl,
    String? imageUrl,
    String? thumbnailUrl,
    String? previewUrl,
    int? width,
    int? height,
    double? aspectRatio,
    int? fileSize,
    String? fileFormat,
    String? resolution,
    String? categoryId,
    String? uploaderId,
    int? viewCount,
    int? downloadCount,
    int? favoriteCount,
    int? shareCount,
    bool? isFeatured,
    bool? isTrending,
    bool? isDaily,
    bool? isPublished,
    double? trendingScore,
    DateTime? createdAt,
    DateTime? updatedAt,
    CategoryModel? category,
    List<TagModel>? tags,
    bool? isFavorite,
    String? dominantColor,
    List<String>? colorPalette,
    bool? isAiGenerated,
    bool? isPremium,
    List<String>? aiTags,
    String? aiDescription,
  }) {
    return WallpaperModel(
      id: id ?? this.id,
      title: title ?? this.title,
      slug: slug ?? this.slug,
      description: description ?? this.description,
      originalUrl: originalUrl ?? this.originalUrl,
      imageUrl: imageUrl ?? this.imageUrl,
      thumbnailUrl: thumbnailUrl ?? this.thumbnailUrl,
      previewUrl: previewUrl ?? this.previewUrl,
      width: width ?? this.width,
      height: height ?? this.height,
      aspectRatio: aspectRatio ?? this.aspectRatio,
      fileSize: fileSize ?? this.fileSize,
      fileFormat: fileFormat ?? this.fileFormat,
      resolution: resolution ?? this.resolution,
      categoryId: categoryId ?? this.categoryId,
      uploaderId: uploaderId ?? this.uploaderId,
      viewCount: viewCount ?? this.viewCount,
      downloadCount: downloadCount ?? this.downloadCount,
      favoriteCount: favoriteCount ?? this.favoriteCount,
      shareCount: shareCount ?? this.shareCount,
      isFeatured: isFeatured ?? this.isFeatured,
      isTrending: isTrending ?? this.isTrending,
      isDaily: isDaily ?? this.isDaily,
      isPublished: isPublished ?? this.isPublished,
      trendingScore: trendingScore ?? this.trendingScore,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      category: category ?? this.category,
      tags: tags ?? this.tags,
      isFavorite: isFavorite ?? this.isFavorite,
      dominantColor: dominantColor ?? this.dominantColor,
      colorPalette: colorPalette ?? this.colorPalette,
      isAiGenerated: isAiGenerated ?? this.isAiGenerated,
      isPremium: isPremium ?? this.isPremium,
      aiTags: aiTags ?? this.aiTags,
      aiDescription: aiDescription ?? this.aiDescription,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'slug': slug,
      'description': description,
      'original_url': originalUrl,
      'image_url': imageUrl,
      'thumbnail_url': thumbnailUrl,
      'preview_url': previewUrl,
      'width': width,
      'height': height,
      'aspect_ratio': aspectRatio,
      'file_size': fileSize,
      'file_format': fileFormat,
      'resolution': resolution,
      'category_id': categoryId,
      'uploader_id': uploaderId,
      'view_count': viewCount,
      'download_count': downloadCount,
      'favorite_count': favoriteCount,
      'share_count': shareCount,
      'is_featured': isFeatured,
      'is_trending': isTrending,
      'is_daily': isDaily,
      'is_published': isPublished,
      'trending_score': trendingScore,
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'category': category?.toJson(),
      'tags': tags.map((t) => t.toJson()).toList(),
      'is_favorite': isFavorite,
      'dominant_color': dominantColor,
      'color_palette': colorPalette,
      'is_ai_generated': isAiGenerated,
      'is_premium': isPremium,
      'ai_tags': aiTags,
      'ai_description': aiDescription,
    };
  }

  @override
  List<Object?> get props => [
        id,
        title,
        slug,
        description,
        originalUrl,
        imageUrl,
        thumbnailUrl,
        previewUrl,
        width,
        height,
        aspectRatio,
        fileSize,
        fileFormat,
        resolution,
        categoryId,
        uploaderId,
        viewCount,
        downloadCount,
        favoriteCount,
        shareCount,
        isFeatured,
        isTrending,
        isDaily,
        isPublished,
        trendingScore,
        createdAt,
        updatedAt,
        category,
        tags,
        isFavorite,
        dominantColor,
        colorPalette,
        isAiGenerated,
        isPremium,
        aiTags,
        aiDescription,
      ];
}
