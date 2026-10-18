import 'package:flutter/services.dart';

enum WallpaperDestination {
  home(1, 'Home Screen'),
  lock(2, 'Lock Screen'),
  both(3, 'Both Screens');

  final int code;
  final String label;
  const WallpaperDestination(this.code, this.label);
}

abstract class IWallpaperSetterService {
  Future<bool> setWallpaper({
    required String filePath,
    required WallpaperDestination destination,
  });

  Future<bool> isSupported();
}

class WallpaperSetterService implements IWallpaperSetterService {
  static const MethodChannel _channel = MethodChannel('com.wallpapers8k1.app/wallpaper');

  @override
  Future<bool> setWallpaper({
    required String filePath,
    required WallpaperDestination destination,
  }) async {
    try {
      final bool? success = await _channel.invokeMethod<bool>('setWallpaper', {
        'filePath': filePath,
        'destination': destination.code,
      });
      return success ?? false;
    } on PlatformException catch (e) {
      throw Exception('Failed to apply wallpaper: ${e.message}');
    } catch (e) {
      throw Exception('Unexpected error applying wallpaper: $e');
    }
  }

  @override
  Future<bool> isSupported() async {
    try {
      final bool? supported = await _channel.invokeMethod<bool>('isSupported');
      return supported ?? true;
    } catch (_) {
      return true;
    }
  }
}
