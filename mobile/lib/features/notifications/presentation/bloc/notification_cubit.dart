import 'package:flutter_bloc/flutter_bloc.dart';
import '../../data/notification_repository.dart';
import 'notification_state.dart';

class NotificationCubit extends Cubit<NotificationState> {
  final INotificationRepository _repository;

  NotificationCubit(this._repository) : super(const NotificationState());

  Future<void> loadNotifications({bool refresh = false}) async {
    if (refresh) {
      emit(state.copyWith(status: NotificationStatus.loading, currentPage: 1));
    } else if (state.status == NotificationStatus.initial) {
      emit(state.copyWith(status: NotificationStatus.loading));
    }

    try {
      final results = await Future.wait([
        _repository.getNotifications(page: 1, limit: 20),
        _repository.getUnreadCount(),
      ]);

      final notifications = results[0] as List<dynamic>;
      final unreadCount = results[1] as int;

      emit(state.copyWith(
        status: NotificationStatus.success,
        notifications: notifications.cast(),
        unreadCount: unreadCount,
        currentPage: 1,
        hasMore: notifications.length >= 20,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: NotificationStatus.failure,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> loadMore() async {
    if (!state.hasMore || state.status == NotificationStatus.loading) return;

    final nextPage = state.currentPage + 1;
    try {
      final more = await _repository.getNotifications(page: nextPage, limit: 20);
      emit(state.copyWith(
        notifications: [...state.notifications, ...more],
        currentPage: nextPage,
        hasMore: more.length >= 20,
      ));
    } catch (e) {
      // Keep existing list on pagination error
    }
  }

  void setFilter(String filter) {
    emit(state.copyWith(selectedFilter: filter));
  }

  Future<void> markAsRead(String id) async {
    final notifIndex = state.notifications.indexWhere((n) => n.id == id);
    if (notifIndex == -1) return;

    final notif = state.notifications[notifIndex];
    if (notif.isRead) return; // already read

    // Optimistic update
    final updatedList = List.of(state.notifications);
    updatedList[notifIndex] = notif.copyWith(isRead: true);
    final newCount = (state.unreadCount > 0) ? state.unreadCount - 1 : 0;
    emit(state.copyWith(notifications: updatedList, unreadCount: newCount));

    try {
      await _repository.markAsRead(id);
    } catch (e) {
      // Revert if failed
      emit(state.copyWith(notifications: state.notifications, unreadCount: state.unreadCount));
    }
  }

  Future<void> markAllAsRead() async {
    if (state.unreadCount == 0) return;

    // Optimistic update
    final updatedList = state.notifications.map((n) => n.copyWith(isRead: true)).toList();
    emit(state.copyWith(notifications: updatedList, unreadCount: 0));

    try {
      await _repository.markAllAsRead();
    } catch (e) {
      // In case of error, reload
      loadNotifications(refresh: true);
    }
  }

  Future<void> deleteNotification(String id) async {
    final notifIndex = state.notifications.indexWhere((n) => n.id == id);
    if (notifIndex == -1) return;

    final notif = state.notifications[notifIndex];
    final wasUnread = !notif.isRead;

    // Optimistic remove
    final updatedList = state.notifications.where((n) => n.id != id).toList();
    final newCount = wasUnread && state.unreadCount > 0 ? state.unreadCount - 1 : state.unreadCount;
    emit(state.copyWith(notifications: updatedList, unreadCount: newCount));

    try {
      await _repository.deleteNotification(id);
    } catch (e) {
      // In case of error, reload
      loadNotifications(refresh: true);
    }
  }

  Future<void> registerDeviceToken({required String token, String? deviceId}) async {
    try {
      await _repository.registerDeviceToken(
        token: token,
        deviceId: deviceId,
        platform: 'android',
        topics: ['daily_wallpaper', 'new_wallpapers', 'featured'],
      );
    } catch (e) {
      // Silently catch registration failure
    }
  }
}
