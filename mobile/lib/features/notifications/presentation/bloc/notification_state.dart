import 'package:equatable/equatable.dart';
import '../../../../shared/models/notification_model.dart';

enum NotificationStatus { initial, loading, success, failure }

class NotificationState extends Equatable {
  final NotificationStatus status;
  final List<NotificationModel> notifications;
  final int unreadCount;
  final bool hasMore;
  final int currentPage;
  final String? errorMessage;
  final String selectedFilter; // 'all' or 'unread'

  const NotificationState({
    this.status = NotificationStatus.initial,
    this.notifications = const [],
    this.unreadCount = 0,
    this.hasMore = true,
    this.currentPage = 1,
    this.errorMessage,
    this.selectedFilter = 'all',
  });

  List<NotificationModel> get displayedNotifications {
    if (selectedFilter == 'unread') {
      return notifications.where((n) => !n.isRead).toList();
    }
    return notifications;
  }

  NotificationState copyWith({
    NotificationStatus? status,
    List<NotificationModel>? notifications,
    int? unreadCount,
    bool? hasMore,
    int? currentPage,
    String? errorMessage,
    String? selectedFilter,
  }) {
    return NotificationState(
      status: status ?? this.status,
      notifications: notifications ?? this.notifications,
      unreadCount: unreadCount ?? this.unreadCount,
      hasMore: hasMore ?? this.hasMore,
      currentPage: currentPage ?? this.currentPage,
      errorMessage: errorMessage ?? this.errorMessage,
      selectedFilter: selectedFilter ?? this.selectedFilter,
    );
  }

  @override
  List<Object?> get props => [
        status,
        notifications,
        unreadCount,
        hasMore,
        currentPage,
        errorMessage,
        selectedFilter,
      ];
}
