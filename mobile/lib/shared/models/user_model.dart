import 'package:equatable/equatable.dart';

class UserModel extends Equatable {
  final String id;
  final String email;
  final String name;
  final String role;
  final bool isActive;
  final bool emailVerified;
  final String? profileImageUrl;
  final int favoritesCount;
  final int downloadsCount;
  final DateTime? createdAt;

  const UserModel({
    required this.id,
    required this.email,
    required this.name,
    this.role = 'user',
    this.isActive = true,
    this.emailVerified = false,
    this.profileImageUrl,
    this.favoritesCount = 0,
    this.downloadsCount = 0,
    this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id']?.toString() ?? '',
      email: json['email']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      role: json['role']?.toString() ?? 'user',
      isActive: (json['is_active'] as bool?) ?? true,
      emailVerified: (json['email_verified'] as bool?) ?? false,
      profileImageUrl: json['profile_image_url']?.toString(),
      favoritesCount: (json['favorites_count'] as num?)?.toInt() ?? 0,
      downloadsCount: (json['downloads_count'] as num?)?.toInt() ?? 0,
      createdAt: json['created_at'] != null ? DateTime.tryParse(json['created_at'].toString()) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'name': name,
      'role': role,
      'is_active': isActive,
      'email_verified': emailVerified,
      'profile_image_url': profileImageUrl,
      'favorites_count': favoritesCount,
      'downloads_count': downloadsCount,
      'created_at': createdAt?.toIso8601String(),
    };
  }

  UserModel copyWith({
    String? name,
    String? profileImageUrl,
    int? favoritesCount,
    int? downloadsCount,
  }) {
    return UserModel(
      id: id,
      email: email,
      name: name ?? this.name,
      role: role,
      isActive: isActive,
      emailVerified: emailVerified,
      profileImageUrl: profileImageUrl ?? this.profileImageUrl,
      favoritesCount: favoritesCount ?? this.favoritesCount,
      downloadsCount: downloadsCount ?? this.downloadsCount,
      createdAt: createdAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        email,
        name,
        role,
        isActive,
        emailVerified,
        profileImageUrl,
        favoritesCount,
        downloadsCount,
        createdAt,
      ];
}

class NotificationPreferenceModel extends Equatable {
  final bool dailyWallpaper;
  final bool newWallpapers;
  final bool newCollections;
  final bool featured;
  final bool promotional;

  const NotificationPreferenceModel({
    this.dailyWallpaper = true,
    this.newWallpapers = true,
    this.newCollections = true,
    this.featured = true,
    this.promotional = false,
  });

  factory NotificationPreferenceModel.fromJson(Map<String, dynamic> json) {
    return NotificationPreferenceModel(
      dailyWallpaper: (json['daily_wallpaper'] as bool?) ?? true,
      newWallpapers: (json['new_wallpapers'] as bool?) ?? true,
      newCollections: (json['new_collections'] as bool?) ?? true,
      featured: (json['featured'] as bool?) ?? true,
      promotional: (json['promotional'] as bool?) ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'daily_wallpaper': dailyWallpaper,
      'new_wallpapers': newWallpapers,
      'new_collections': newCollections,
      'featured': featured,
      'promotional': promotional,
    };
  }

  NotificationPreferenceModel copyWith({
    bool? dailyWallpaper,
    bool? newWallpapers,
    bool? newCollections,
    bool? featured,
    bool? promotional,
  }) {
    return NotificationPreferenceModel(
      dailyWallpaper: dailyWallpaper ?? this.dailyWallpaper,
      newWallpapers: newWallpapers ?? this.newWallpapers,
      newCollections: newCollections ?? this.newCollections,
      featured: featured ?? this.featured,
      promotional: promotional ?? this.promotional,
    );
  }

  @override
  List<Object?> get props => [
        dailyWallpaper,
        newWallpapers,
        newCollections,
        featured,
        promotional,
      ];
}
