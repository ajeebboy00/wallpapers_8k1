import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../constants/app_constants.dart';

class ThemeCubit extends Cubit<ThemeMode> {
  final SharedPreferences? _prefs;

  ThemeCubit([this._prefs]) : super(ThemeMode.dark) {
    _loadSavedTheme();
  }

  void _loadSavedTheme() {
    if (_prefs == null) return;
    final savedMode = _prefs!.getString(AppConstants.themeModeKey);
    if (savedMode == 'light') {
      emit(ThemeMode.light);
    } else if (savedMode == 'system') {
      emit(ThemeMode.system);
    } else {
      emit(ThemeMode.dark);
    }
  }

  Future<void> setTheme(ThemeMode mode) async {
    emit(mode);
    if (_prefs != null) {
      String modeStr = 'dark';
      if (mode == ThemeMode.light) modeStr = 'light';
      if (mode == ThemeMode.system) modeStr = 'system';
      await _prefs!.setString(AppConstants.themeModeKey, modeStr);
    }
  }

  Future<void> toggleTheme() async {
    if (state == ThemeMode.dark) {
      await setTheme(ThemeMode.light);
    } else {
      await setTheme(ThemeMode.dark);
    }
  }
}
