import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:bloc_test/bloc_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:wallpapers_8k1/core/constants/app_constants.dart';
import 'package:wallpapers_8k1/core/theme/theme_cubit.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('ThemeCubit Tests', () {
    test('initial state defaults to ThemeMode.dark when no preference is saved', () {
      SharedPreferences.setMockInitialValues({});
      final cubit = ThemeCubit();
      expect(cubit.state, ThemeMode.dark);
      cubit.close();
    });

    blocTest<ThemeCubit, ThemeMode>(
      'emits [ThemeMode.light] when toggleTheme is called from dark mode',
      build: () => ThemeCubit(),
      act: (cubit) => cubit.toggleTheme(),
      expect: () => [ThemeMode.light],
    );

    blocTest<ThemeCubit, ThemeMode>(
      'emits [ThemeMode.light, ThemeMode.dark] when toggleTheme is called twice',
      build: () => ThemeCubit(),
      act: (cubit) async {
        await cubit.toggleTheme();
        await cubit.toggleTheme();
      },
      expect: () => [ThemeMode.light, ThemeMode.dark],
    );

    blocTest<ThemeCubit, ThemeMode>(
      'emits [ThemeMode.system] when setTheme(ThemeMode.system) is called',
      build: () => ThemeCubit(),
      act: (cubit) => cubit.setTheme(ThemeMode.system),
      expect: () => [ThemeMode.system],
    );
  });
}
