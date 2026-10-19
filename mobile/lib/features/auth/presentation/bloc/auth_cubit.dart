import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:wallpapers_8k1/shared/models/user_model.dart';
import '../../data/auth_repository.dart';
import 'auth_state.dart';

class AuthCubit extends Cubit<AuthState> {
  final IAuthRepository _repository;

  AuthCubit(this._repository) : super(const AuthInitial());

  Future<void> checkAuthStatus() async {
    try {
      final user = await _repository.getCurrentUser();
      if (user != null) {
        emit(Authenticated(user));
      } else {
        emit(const Unauthenticated());
      }
    } catch (_) {
      emit(const Unauthenticated());
    }
  }

  Future<void> login(String email, String password) async {
    emit(const AuthLoading());

    try {
      final user = await _repository.login(
        email: email.trim(),
        password: password,
      );
      emit(Authenticated(user));
    } catch (e) {
      emit(AuthError(e.toString().replaceAll("Exception: ", "")));
    }
  }

  Future<void> register(String name, String email, String password) async {
    emit(const AuthLoading());

    try {
      final user = await _repository.register(
        name: name.trim(),
        email: email.trim(),
        password: password,
      );
      emit(Authenticated(user));
    } catch (e) {
      emit(AuthError(e.toString().replaceAll("Exception: ", "")));
    }
  }

  Future<void> logout() async {
    emit(const AuthLoading());
    await _repository.logout();
    emit(const Unauthenticated());
  }

  void updateUser(UserModel updatedUser) {
    if (state is Authenticated) {
      emit(Authenticated(updatedUser));
    }
  }
}
