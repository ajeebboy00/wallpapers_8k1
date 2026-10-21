import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'core/config/app_config.dart';
import 'core/constants/app_constants.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';
import 'core/theme/theme_cubit.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 1. Initialize environment settings with --dart-define support
  const envString = String.fromEnvironment('APP_ENV', defaultValue: 'development');
  const customBaseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: '');
  final isProd = envString.toLowerCase() == 'production';
  final env = isProd ? Environment.production : Environment.development;
  final baseUrl = customBaseUrl.isNotEmpty
      ? customBaseUrl
      : (isProd ? 'https://api.wallpapers8k1.com/api/v1' : AppConstants.defaultBaseUrl);

  AppConfig.initialize(
    environment: env,
    apiBaseUrl: baseUrl,
    enableLogging: !isProd,
  );

  // 2. Initialize local preferences safely
  SharedPreferences? prefs;
  try {
    prefs = await SharedPreferences.getInstance();
  } catch (e) {
    debugPrint('Could not initialize SharedPreferences: $e');
  }

  runApp(
    MultiBlocProvider(
      providers: [
        BlocProvider<ThemeCubit>(
          create: (_) => ThemeCubit(prefs),
        ),
      ],
      child: const Wallpapers8k1App(),
    ),
  );
}

class Wallpapers8k1App extends StatelessWidget {
  const Wallpapers8k1App({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<ThemeCubit, ThemeMode>(
      builder: (context, themeMode) {
        return MaterialApp.router(
          title: AppConstants.appName,
          debugShowCheckedModeBanner: false,
          theme: AppTheme.lightTheme,
          darkTheme: AppTheme.darkTheme,
          themeMode: themeMode,
          routerConfig: AppRouter.router,
        );
      },
    );
  }
}
