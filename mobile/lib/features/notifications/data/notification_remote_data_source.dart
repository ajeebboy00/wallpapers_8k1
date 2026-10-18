import '../../../../core/network/api_client.dart';
import '../../../../shared/models/notification_model.dart';

abstract class INotificationRemoteDataSource {
  Future<void> registerDeviceToken({
    required String token,
    String? deviceId,
    String platform = 'android',
    String? appVersion,
    List<String>? topics,
  });

  Future<void> unregisterDeviceToken(String token);

  Future<List<NotificationModel>> getNotifications({int page = 1, int limit = 20});

  Future<int> getUnreadCount();

  Future<NotificationModel> markAsRead(String notificationId);

  Future<int> markAllAsRead();

  Future<bool> deleteNotification(String notificationId);
}

class NotificationRemoteDataSource implements INotificationRemoteDataSource {
  final ApiClient _apiClient;

  NotificationRemoteDataSource(this._apiClient);

  @override
  Future<void> registerDeviceToken({
    required String token,
    String? deviceId,
    String platform = 'android',
    String? appVersion,
    List<String>? topics,
  }) async {
    await _apiClient.post(
      '/api/v1/notifications/devices',
      data: {
        'token': token,
        if (deviceId != null) 'device_id': deviceId,
        'platform': platform,
        if (appVersion != null) 'app_version': appVersion,
        if (topics != null) 'topics': topics,
      },
    );
  }

  @override
  Future<void> unregisterDeviceToken(String token) async {
    await _apiClient.delete('/api/v1/notifications/devices/$token');
  }

  @override
  Future<List<NotificationModel>> getNotifications({int page = 1, int limit = 20}) async {
    final response = await _apiClient.get(
      '/api/v1/notifications',
      queryParameters: {
        'page': page,
        'limit': limit,
      },
    );

    final data = response.data;
    if (data is Map<String, dynamic> && data['data'] is List) {
      return (data['data'] as List)
          .map((item) => NotificationModel.fromJson(item as Map<String, dynamic>))
          .toList();
    }
    return [];
  }

  @override
  Future<int> getUnreadCount() async {
    final response = await _apiClient.get('/api/v1/notifications/unread-count');
    final data = response.data;
    if (data is Map<String, dynamic> && data['data'] is Map<String, dynamic>) {
      return (data['data']['unread_count'] as num?)?.toInt() ?? 0;
    }
    return 0;
  }

  @override
  Future<NotificationModel> markAsRead(String notificationId) async {
    final response = await _apiClient.patch('/api/v1/notifications/$notificationId/read');
    final data = response.data;
    if (data is Map<String, dynamic> && data['data'] is Map<String, dynamic>) {
      return NotificationModel.fromJson(data['data'] as Map<String, dynamic>);
    }
    throw Exception('Failed to parse updated notification');
  }

  @override
  Future<int> markAllAsRead() async {
    final response = await _apiClient.patch('/api/v1/notifications/read-all');
    final data = response.data;
    if (data is Map<String, dynamic> && data['data'] is Map<String, dynamic>) {
      return (data['data']['updated_count'] as num?)?.toInt() ?? 0;
    }
    return 0;
  }

  @override
  Future<bool> deleteNotification(String notificationId) async {
    final response = await _apiClient.delete('/api/v1/notifications/$notificationId');
    final data = response.data;
    if (data is Map<String, dynamic> && data['data'] is Map<String, dynamic>) {
      return (data['data']['deleted'] as bool?) ?? true;
    }
    return true;
  }
}
