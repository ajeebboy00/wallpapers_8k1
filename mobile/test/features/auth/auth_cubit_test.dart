import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:wallpapers_8k1/features/auth/data/auth_repository.dart';
import 'package:wallpapers_8k1/features/auth/presentation/bloc/auth_cubit.dart';
import 'package:wallpapers_8k1/features/auth/presentation/bloc/auth_state.dart';
import 'package:wallpapers_8k1/shared/models/user_model.dart';

class MockAuthRepository extends Mock implements IAuthRepository {}

void main() {
  late MockAuthRepository mockRepo;

  const testUser = UserModel(
    id: 'user-100',
    email: 'creator@example.com',
    name: '8K Creator',
    role: 'user',
    favoritesCount: 12,
    downloadsCount: 5,
  );

  setUp(() {
    mockRepo = MockAuthRepository();
  });

  group('AuthCubit Unit Tests', () {
    test('initial state is AuthInitial', () {
      final cubit = AuthCubit(mockRepo);
      expect(cubit.state, const AuthInitial());
      cubit.close();
    });

    blocTest<AuthCubit, AuthState>(
      'checkAuthStatus emits Authenticated when active user exists',
      build: () {
        when(() => mockRepo.getCurrentUser()).thenAnswer((_) async => testUser);
        return AuthCubit(mockRepo);
      },
      act: (cubit) => cubit.checkAuthStatus(),
      expect: () => [
        const Authenticated(testUser),
      ],
    );

    blocTest<AuthCubit, AuthState>(
      'checkAuthStatus emits Unauthenticated when no active token',
      build: () {
        when(() => mockRepo.getCurrentUser()).thenAnswer((_) async => null);
        return AuthCubit(mockRepo);
      },
      act: (cubit) => cubit.checkAuthStatus(),
      expect: () => [
        const Unauthenticated(),
      ],
    );

    blocTest<AuthCubit, AuthState>(
      'login emits [AuthLoading, Authenticated] on valid credentials',
      build: () {
        when(() => mockRepo.login(
              email: 'creator@example.com',
              password: 'Password123!',
            )).thenAnswer((_) async => testUser);
        return AuthCubit(mockRepo);
      },
      act: (cubit) => cubit.login('creator@example.com', 'Password123!'),
      expect: () => [
        const AuthLoading(),
        const Authenticated(testUser),
      ],
    );

    blocTest<AuthCubit, AuthState>(
      'login emits [AuthLoading, AuthError] on failed credentials',
      build: () {
        when(() => mockRepo.login(
              email: 'creator@example.com',
              password: 'WrongPassword!',
            )).thenThrow(Exception('Invalid credentials'));
        return AuthCubit(mockRepo);
      },
      act: (cubit) => cubit.login('creator@example.com', 'WrongPassword!'),
      expect: () => [
        const AuthLoading(),
        isA<AuthError>(),
      ],
    );

    blocTest<AuthCubit, AuthState>(
      'logout clears session and emits Unauthenticated',
      build: () {
        when(() => mockRepo.logout()).thenAnswer((_) async {});
        return AuthCubit(mockRepo);
      },
      act: (cubit) => cubit.logout(),
      expect: () => [
        const AuthLoading(),
        const Unauthenticated(),
      ],
    );
  });
}
