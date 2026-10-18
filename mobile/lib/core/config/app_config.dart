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
  }
}
