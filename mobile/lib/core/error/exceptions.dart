/// Base application exception
class AppException implements Exception {
  final String message;
  final String? code;
  final int? statusCode;

  const AppException({
    required this.message,
    this.code,
    this.statusCode,
  });

  @override
  String toString() => 'AppException(message: $message, code: $code, statusCode: $statusCode)';
}

class ServerException extends AppException {
  const ServerException({
    required super.message,
    super.code,
    super.statusCode,
  });
}

class NetworkException extends AppException {
  const NetworkException({
    super.message = 'No internet connection. Please verify network status.',
  }) : super(code: 'NETWORK_ERROR', statusCode: 0);
}

class UnauthorizedException extends AppException {
  const UnauthorizedException({
    super.message = 'Authentication required or session expired.',
    super.code = 'UNAUTHORIZED',
  }) : super(statusCode: 401);
}

class NotFoundException extends AppException {
  const NotFoundException({
    super.message = 'Requested resource was not found.',
    super.code = 'NOT_FOUND',
  }) : super(statusCode: 404);
}

class ValidationException extends AppException {
  final dynamic details;

  const ValidationException({
    super.message = 'Request validation failed.',
    super.code = 'VALIDATION_ERROR',
    this.details,
  }) : super(statusCode: 422);
}
