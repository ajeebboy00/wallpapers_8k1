import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../constants/app_constants.dart';

abstract class ISecureStorageService {
  Future<void> saveTokens({required String accessToken, required String refreshToken});
  Future<String?> getAccessToken();
  Future<String?> getRefreshToken();
  Future<void> saveUserId(String userId);
  Future<String?> getUserId();
  Future<void> clearAll();
  Future<bool> hasAccessToken();
  Future<String?> getString(String key);
  Future<void> setString(String key, String value);
  Future<void> delete(String key);
}

class SecureStorageService implements ISecureStorageService {
  final FlutterSecureStorage _storage;

  SecureStorageService([FlutterSecureStorage? storage])
      : _storage = storage ??
            const FlutterSecureStorage(
              aOptions: AndroidOptions(encryptedSharedPreferences: true),
            );

  @override
  Future<void> saveTokens({required String accessToken, required String refreshToken}) async {
    await _storage.write(key: AppConstants.accessTokenKey, value: accessToken);
    await _storage.write(key: AppConstants.refreshTokenKey, value: refreshToken);
  }

  @override
  Future<String?> getAccessToken() async {
    return await _storage.read(key: AppConstants.accessTokenKey);
  }

  @override
  Future<String?> getRefreshToken() async {
    return await _storage.read(key: AppConstants.refreshTokenKey);
  }

  @override
  Future<void> saveUserId(String userId) async {
    await _storage.write(key: AppConstants.userProfileKey, value: userId);
  }

  @override
  Future<String?> getUserId() async {
    return await _storage.read(key: AppConstants.userProfileKey);
  }

  @override
  Future<void> clearAll() async {
    await _storage.deleteAll();
  }

  @override
  Future<bool> hasAccessToken() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }

  @override
  Future<String?> getString(String key) async {
    return await _storage.read(key: key);
  }

  @override
  Future<void> setString(String key, String value) async {
    await _storage.write(key: key, value: value);
  }

  @override
  Future<void> delete(String key) async {
    await _storage.delete(key: key);
  }
}
