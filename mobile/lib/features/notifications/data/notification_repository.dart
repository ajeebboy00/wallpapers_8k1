import 'package:wallpapers_8k1/shared/models/notification_model.dart';
import 'notification_remote_data_source.dart';

abstract class INotificationRepository {
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

class NotificationRepository implements INotificationRepository {
  final INotificationRemoteDataSource _remoteDataSource;

  NotificationRepository(this._remoteDataSource);

  @override
  Future<void> registerDeviceToken({
    required String token,
    String? deviceId,
    String platform = 'android',
    String? appVersion,
    List<String>? topics,
  }) {
    return _remoteDataSource.registerDeviceToken(
      token: token,
      deviceId: deviceId,
      platform: platform,
      appVersion: appVersion,
      topics: topics,
    );
  }

  @override
  Future<void> unregisterDeviceToken(String token) {
    return _remoteDataSource.unregisterDeviceToken(token);
  }

  @override
  Future<List<NotificationModel>> getNotifications({int page = 1, int limit = 20}) {
    return _remoteDataSource.getNotifications(page: page, limit: limit);
  }

  @override
  Future<int> getUnreadCount() {
    return _remoteDataSource.getUnreadCount();
  }

  @override
  Future<NotificationModel> markAsRead(String notificationId) {
    return _remoteDataSource.markAsRead(notificationId);
  }

  @override
  Future<int> markAllAsRead() {
    return _remoteDataSource.markAllAsRead();
  }

  @override
  Future<bool> deleteNotification(String notificationId) {
    return _remoteDataSource.deleteNotification(notificationId);
  }
}
