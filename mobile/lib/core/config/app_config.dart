import 'package:flutter/foundation.dart';

enum Environment { development, staging, production }

class AppConfig {
  final Environment environment;
  final String apiBaseUrl;
  final bool enableLogging;

  const AppConfig({
    required this.environment,
    required this.apiBaseUrl,
    this.enableLogging = true,
  });

  static late AppConfig current;
  static final ValueNotifier<String> baseUrlNotifier = ValueNotifier<String>('');

  static void initialize({
    required Environment environment,
    required String apiBaseUrl,
    bool enableLogging = true,
  }) {
    current = AppConfig(
      environment: environment,
      apiBaseUrl: apiBaseUrl,
      enableLogging: enableLogging,
    );
    baseUrlNotifier.value = apiBaseUrl;
  }

  static void updateApiBaseUrl(String newUrl) {
    current = AppConfig(
      environment: current.environment,
      apiBaseUrl: newUrl,
      enableLogging: current.enableLogging,
    );
    baseUrlNotifier.value = newUrl;
  }
}
