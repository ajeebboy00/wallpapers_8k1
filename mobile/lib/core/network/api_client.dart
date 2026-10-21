import 'package:dio/dio.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';
import '../config/app_config.dart';
import '../constants/app_constants.dart';
import '../error/exceptions.dart';
import '../storage/secure_storage_service.dart';
import 'auth_interceptor.dart';

class ApiClient {
  final Dio dio;

  ApiClient({Dio? dioClient, ISecureStorageService? storage})
      : dio = dioClient ??
            Dio(
              BaseOptions(
                baseUrl: AppConfig.current.apiBaseUrl,
                connectTimeout: AppConstants.connectTimeout,
                receiveTimeout: AppConstants.receiveTimeout,
                headers: {
                  'Content-Type': 'application/json',
                  'Accept': 'application/json',
                },
              ),
            ) {
    if (storage != null) {
      dio.interceptors.add(AuthInterceptor(storage: storage, dio: dio));
    }

    if (AppConfig.current.enableLogging) {
      dio.interceptors.add(
        PrettyDioLogger(
          requestHeader: false,
          requestBody: true,
          responseBody: true,
          responseHeader: false,
          error: true,
          compact: true,
        ),
      );
    }

    AppConfig.baseUrlNotifier.addListener(() {
      dio.options.baseUrl = AppConfig.baseUrlNotifier.value;
    });
  }

  void updateBaseUrl(String newUrl) {
    AppConfig.updateApiBaseUrl(newUrl);
    dio.options.baseUrl = newUrl;
  }

  AppException _handleDioError(DioException error) {
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.sendTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        error.type == DioExceptionType.connectionError) {
      return const NetworkException();
    }

    final response = error.response;
    if (response != null) {
      final statusCode = response.statusCode;
      final data = response.data;

      String message = 'An unexpected server error occurred';
      String? code;
      dynamic details;

      if (data is Map<String, dynamic>) {
        if (data['error'] is Map<String, dynamic>) {
          message = data['error']['message'] ?? message;
          code = data['error']['code'];
          details = data['error']['details'];
        } else if (data['message'] is String) {
          message = data['message'];
        }
      }

      if (statusCode == 401) {
        return UnauthorizedException(message: message, code: code);
      } else if (statusCode == 404) {
        return NotFoundException(message: message, code: code);
      } else if (statusCode == 422) {
        return ValidationException(message: message, code: code, details: details);
      }

      return ServerException(message: message, code: code, statusCode: statusCode);
    }

    return ServerException(message: error.message ?? 'Unknown connection error');
  }

  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await dio.get<T>(path, queryParameters: queryParameters, options: options);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await dio.post<T>(path, data: data, queryParameters: queryParameters, options: options);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<Response<T>> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await dio.put<T>(path, data: data, queryParameters: queryParameters, options: options);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<Response<T>> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await dio.delete<T>(path, data: data, queryParameters: queryParameters, options: options);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<Response<T>> patch<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await dio.patch<T>(path, data: data, queryParameters: queryParameters, options: options);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<Response> download(
    String urlPath,
    dynamic savePath, {
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      return await dio.download(urlPath, savePath, onReceiveProgress: onReceiveProgress);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }
}
