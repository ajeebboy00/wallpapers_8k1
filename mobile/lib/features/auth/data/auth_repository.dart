import 'package:wallpapers_8k1/core/storage/secure_storage_service.dart';
import 'package:wallpapers_8k1/shared/models/user_model.dart';
import 'auth_remote_data_source.dart';

abstract class IAuthRepository {
  Future<UserModel> login({required String email, required String password});
  Future<UserModel> register({required String name, required String email, required String password});
  Future<UserModel?> getCurrentUser();
  Future<void> logout();
}

class AuthRepository implements IAuthRepository {
  final AuthRemoteDataSource _remoteDataSource;
  final ISecureStorageService _storage;

  AuthRepository(this._remoteDataSource, this._storage);

  @override
  Future<UserModel> login({required String email, required String password}) async {
    final session = await _remoteDataSource.login(email: email, password: password);
    await _storage.saveTokens(
      accessToken: session.accessToken,
      refreshToken: session.refreshToken,
    );
    await _storage.saveUserId(session.user.id);
    return session.user;
  }

  @override
  Future<UserModel> register({
    required String name,
    required String email,
    required String password,
  }) async {
    final session = await _remoteDataSource.register(
      name: name,
      email: email,
      password: password,
    );
    await _storage.saveTokens(
      accessToken: session.accessToken,
      refreshToken: session.refreshToken,
    );
    await _storage.saveUserId(session.user.id);
    return session.user;
  }

  @override
  Future<UserModel?> getCurrentUser() async {
    final hasToken = await _storage.hasAccessToken();
    if (!hasToken) return null;

    try {
      return await _remoteDataSource.getProfile();
    } catch (_) {
      return null;
    }
  }

  @override
  Future<void> logout() async {
    final refresh = await _storage.getRefreshToken();
    if (refresh != null) {
      await _remoteDataSource.logout(refresh);
    }
    await _storage.clearAll();
  }
}
