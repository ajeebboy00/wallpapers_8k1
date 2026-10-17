import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:wallpapers_8k1/core/constants/app_constants.dart';
import 'package:wallpapers_8k1/core/storage/secure_storage_service.dart';

class MockFlutterSecureStorage extends Mock implements FlutterSecureStorage {}

void main() {
  late MockFlutterSecureStorage mockStorage;
  late SecureStorageService service;

  setUp(() {
    mockStorage = MockFlutterSecureStorage();
    service = SecureStorageService(mockStorage);
  });

  group('SecureStorageService Tests', () {
    test('saveTokens writes accessToken and refreshToken to secure storage', () async {
      when(() => mockStorage.write(key: AppConstants.accessTokenKey, value: 'test_access_token'))
          .thenAnswer((_) async {});
      when(() => mockStorage.write(key: AppConstants.refreshTokenKey, value: 'test_refresh_token'))
          .thenAnswer((_) async {});

      await service.saveTokens(
        accessToken: 'test_access_token',
        refreshToken: 'test_refresh_token',
      );

      verify(() => mockStorage.write(key: AppConstants.accessTokenKey, value: 'test_access_token'))
          .called(1);
      verify(() => mockStorage.write(key: AppConstants.refreshTokenKey, value: 'test_refresh_token'))
          .called(1);
    });

    test('getAccessToken retrieves token from storage', () async {
      when(() => mockStorage.read(key: AppConstants.accessTokenKey))
          .thenAnswer((_) async => 'stored_jwt_token');

      final token = await service.getAccessToken();

      expect(token, 'stored_jwt_token');
      verify(() => mockStorage.read(key: AppConstants.accessTokenKey)).called(1);
    });

    test('hasAccessToken returns true when token is present and non-empty', () async {
      when(() => mockStorage.read(key: AppConstants.accessTokenKey))
          .thenAnswer((_) async => 'valid_token');

      final hasToken = await service.hasAccessToken();

      expect(hasToken, isTrue);
    });

    test('hasAccessToken returns false when token is null', () async {
      when(() => mockStorage.read(key: AppConstants.accessTokenKey))
          .thenAnswer((_) async => null);

      final hasToken = await service.hasAccessToken();

      expect(hasToken, isFalse);
    });

    test('clearAll delegates to deleteAll on underlying secure storage', () async {
      when(() => mockStorage.deleteAll()).thenAnswer((_) async {});

      await service.clearAll();

      verify(() => mockStorage.deleteAll()).called(1);
    });
  });
}
