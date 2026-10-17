import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:wallpapers_8k1/core/network/auth_interceptor.dart';
import 'package:wallpapers_8k1/core/storage/secure_storage_service.dart';

class MockSecureStorageService extends Mock implements ISecureStorageService {}
class MockRequestInterceptorHandler extends Mock implements RequestInterceptorHandler {}

void main() {
  late MockSecureStorageService mockStorage;
  late Dio dio;
  late AuthInterceptor interceptor;
  late MockRequestInterceptorHandler mockHandler;

  setUp(() {
    mockStorage = MockSecureStorageService();
    dio = Dio();
    interceptor = AuthInterceptor(storage: mockStorage, dio: dio);
    mockHandler = MockRequestInterceptorHandler();
  });

  group('AuthInterceptor Tests', () {
    test('attaches Bearer token to outgoing authorized request', () async {
      when(() => mockStorage.getAccessToken()).thenAnswer((_) async => 'valid_access_token_xyz');
      when(() => mockHandler.next(any())).thenReturn(null);

      final options = RequestOptions(path: '/wallpapers');
      interceptor.onRequest(options, mockHandler);

      // Wait a microtask for async storage read
      await Future<void>.delayed(Duration.zero);

      expect(options.headers['Authorization'], 'Bearer valid_access_token_xyz');
      verify(() => mockHandler.next(options)).called(1);
    });

    test('does NOT attach Bearer token to /auth/login request', () async {
      when(() => mockHandler.next(any())).thenReturn(null);

      final options = RequestOptions(path: '/auth/login');
      interceptor.onRequest(options, mockHandler);

      await Future<void>.delayed(Duration.zero);

      expect(options.headers.containsKey('Authorization'), isFalse);
      verifyNever(() => mockStorage.getAccessToken());
      verify(() => mockHandler.next(options)).called(1);
    });

    test('does NOT attach Bearer token to /auth/register request', () async {
      when(() => mockHandler.next(any())).thenReturn(null);

      final options = RequestOptions(path: '/auth/register');
      interceptor.onRequest(options, mockHandler);

      await Future<void>.delayed(Duration.zero);

      expect(options.headers.containsKey('Authorization'), isFalse);
      verifyNever(() => mockStorage.getAccessToken());
      verify(() => mockHandler.next(options)).called(1);
    });
  });
}
