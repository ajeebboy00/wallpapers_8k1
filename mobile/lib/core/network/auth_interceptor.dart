import 'package:dio/dio.dart';
import '../config/app_config.dart';
import '../storage/secure_storage_service.dart';

/// QueuedInterceptor handles automatic Bearer token injection and seamless token rotation on 401
class AuthInterceptor extends QueuedInterceptor {
  final ISecureStorageService _storage;
  final Dio _dio;

  AuthInterceptor({
    required ISecureStorageService storage,
    required Dio dio,
  })  : _storage = storage,
        _dio = dio;

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    // Exclude auth credentials for public registration/login endpoints
    final path = options.path;
    final isAuthRoute = path.contains('/auth/login') ||
        path.contains('/auth/register') ||
        path.contains('/auth/refresh') ||
        path.contains('/auth/forgot-password');

    if (!isAuthRoute) {
      final token = await _storage.getAccessToken();
      if (token != null && token.isNotEmpty) {
        options.headers['Authorization'] = 'Bearer $token';
      }
    }

    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      final path = err.requestOptions.path;
      // Do not attempt refresh on auth endpoints to avoid infinite recursion
      if (path.contains('/auth/login') ||
          path.contains('/auth/register') ||
          path.contains('/auth/refresh')) {
        handler.next(err);
        return;
      }

      final refreshToken = await _storage.getRefreshToken();
      if (refreshToken != null && refreshToken.isNotEmpty) {
        try {
          // Use isolated Dio instance for token rotation
          final refreshDio = Dio(BaseOptions(
            baseUrl: AppConfig.current.apiBaseUrl,
            headers: {'Content-Type': 'application/json'},
          ));

          final refreshResponse = await refreshDio.post(
            '/auth/refresh',
            data: {'refresh_token': refreshToken},
          );

          if (refreshResponse.statusCode == 200 && refreshResponse.data['success'] == true) {
            final tokenData = refreshResponse.data['data'];
            final newAccessToken = tokenData['access_token'] as String;
            final newRefreshToken = tokenData['refresh_token'] as String;

            // Persist rotated tokens
            await _storage.saveTokens(
              accessToken: newAccessToken,
              refreshToken: newRefreshToken,
            );

            // Retry original request with newly rotated token
            final originalOptions = err.requestOptions;
            originalOptions.headers['Authorization'] = 'Bearer $newAccessToken';

            final retryResponse = await _dio.fetch(originalOptions);
            handler.resolve(retryResponse);
            return;
          }
        } catch (_) {
          // Token rotation failed or token was revoked: clear session
          await _storage.clearAll();
        }
      }
    }

    handler.next(err);
  }
}
