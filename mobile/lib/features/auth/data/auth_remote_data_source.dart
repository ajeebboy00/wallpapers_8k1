import '../../../../core/network/api_client.dart';
import '../../../../shared/models/user_model.dart';

class AuthSessionBundle {
  final String accessToken;
  final String refreshToken;
  final UserModel user;

  const AuthSessionBundle({
    required this.accessToken,
    required this.refreshToken,
    required this.user,
  });
}

class AuthRemoteDataSource {
  final ApiClient _apiClient;

  AuthRemoteDataSource(this._apiClient);

  Future<AuthSessionBundle> login({
    required String email,
    required String password,
  }) async {
    final response = await _apiClient.post(
      '/auth/login',
      data: {
        'email': email,
        'password': password,
      },
    );

    final data = response.data['data'] as Map<String, dynamic>;
    final user = UserModel.fromJson(data['user'] as Map<String, dynamic>);

    return AuthSessionBundle(
      accessToken: data['access_token'].toString(),
      refreshToken: data['refresh_token'].toString(),
      user: user,
    );
  }

  Future<AuthSessionBundle> register({
    required String name,
    required String email,
    required String password,
  }) async {
    final response = await _apiClient.post(
      '/auth/register',
      data: {
        'name': name,
        'email': email,
        'password': password,
      },
    );

    final data = response.data['data'] as Map<String, dynamic>;
    final user = UserModel.fromJson(data['user'] as Map<String, dynamic>);

    return AuthSessionBundle(
      accessToken: data['access_token'].toString(),
      refreshToken: data['refresh_token'].toString(),
      user: user,
    );
  }

  Future<UserModel> getProfile() async {
    final response = await _apiClient.get('/users/me');
    return UserModel.fromJson(response.data['data'] as Map<String, dynamic>);
  }

  Future<void> logout(String refreshToken) async {
    try {
      await _apiClient.post(
        '/auth/logout',
        data: {'refresh_token': refreshToken},
      );
    } catch (_) {}
  }
}
