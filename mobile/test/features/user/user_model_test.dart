import 'package:flutter_test/flutter_test.dart';
import 'package:wallpapers_8k1/shared/models/user_model.dart';

void main() {
  group('UserModel and NotificationPreferenceModel Tests', () {
    test('UserModel deserializes from backend JSON with library counters', () {
      final json = {
        'id': 'u-12345',
        'email': 'artisan@example.com',
        'name': 'Artisan Visuals',
        'role': 'user',
        'is_active': true,
        'email_verified': true,
        'profile_image_url': 'https://storage/avatars/artisan.webp',
        'favorites_count': 18,
        'downloads_count': 7,
        'created_at': '2026-09-28T10:00:00Z',
      };

      final user = UserModel.fromJson(json);

      expect(user.id, 'u-12345');
      expect(user.email, 'artisan@example.com');
      expect(user.name, 'Artisan Visuals');
      expect(user.role, 'user');
      expect(user.favoritesCount, 18);
      expect(user.downloadsCount, 7);
      expect(user.isActive, isTrue);
      expect(user.emailVerified, isTrue);
    });

    test('NotificationPreferenceModel handles defaults and copyWith', () {
      const defaultPrefs = NotificationPreferenceModel();
      expect(defaultPrefs.dailyWallpaper, isTrue);
      expect(defaultPrefs.newWallpapers, isTrue);
      expect(defaultPrefs.promotional, isFalse);

      final updated = defaultPrefs.copyWith(dailyWallpaper: false, promotional: true);
      expect(updated.dailyWallpaper, isFalse);
      expect(updated.promotional, isTrue);

      final json = updated.toJson();
      expect(json['daily_wallpaper'], isFalse);
      expect(json['promotional'], isTrue);
    });
  });
}
