import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/storage/secure_storage_service.dart';
import '../../../../core/theme/app_colors.dart';
import '../data/notification_remote_data_source.dart';
import '../data/notification_repository.dart';
import 'bloc/notification_cubit.dart';
import 'bloc/notification_state.dart';
import 'widgets/notification_item_card.dart';

class NotificationScreen extends StatelessWidget {
  const NotificationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider<NotificationCubit>(
      create: (context) {
        final apiClient = ApiClient(storage: SecureStorageService());
        final dataSource = NotificationRemoteDataSource(apiClient);
        final repository = NotificationRepository(dataSource);
        return NotificationCubit(repository)..loadNotifications();
      },
      child: const _NotificationScreenContent(),
    );
  }
}

class _NotificationScreenContent extends StatefulWidget {
  const _NotificationScreenContent();

  @override
  State<_NotificationScreenContent> createState() => _NotificationScreenContentState();
}

class _NotificationScreenContentState extends State<_NotificationScreenContent> {
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.removeListener(_onScroll);
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >= _scrollController.position.maxScrollExtent - 200) {
      context.read<NotificationCubit>().loadMore();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text(
          'Notifications',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 19),
        ),
        actions: [
          BlocBuilder<NotificationCubit, NotificationState>(
            builder: (context, state) {
              if (state.unreadCount > 0) {
                return TextButton.icon(
                  onPressed: () {
                    context.read<NotificationCubit>().markAllAsRead();
                  },
                  icon: const Icon(Icons.done_all_rounded, size: 18, color: AppColors.primary),
                  label: const Text(
                    'Mark all read',
                    style: TextStyle(fontSize: 12, color: AppColors.primary, fontWeight: FontWeight.bold),
                  ),
                );
              }
              return const SizedBox.shrink();
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: BlocBuilder<NotificationCubit, NotificationState>(
        builder: (context, state) {
          return Column(
            children: [
              // Filter Chips Bar
              _buildFilterChips(context, state),

              // Content Body
              Expanded(
                child: _buildBody(context, state),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildFilterChips(BuildContext context, NotificationState state) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.background,
        border: Border(bottom: BorderSide(color: AppColors.border.withOpacity(0.4))),
      ),
      child: Row(
        children: [
          _buildChip(
            context,
            label: 'All',
            isSelected: state.selectedFilter == 'all',
            count: state.notifications.length,
            onTap: () => context.read<NotificationCubit>().setFilter('all'),
          ),
          const SizedBox(width: 8),
          _buildChip(
            context,
            label: 'Unread',
            isSelected: state.selectedFilter == 'unread',
            count: state.unreadCount,
            onTap: () => context.read<NotificationCubit>().setFilter('unread'),
          ),
        ],
      ),
    );
  }

  Widget _buildChip(
    BuildContext context, {
    required String label,
    required bool isSelected,
    required int count,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primary : AppColors.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? AppColors.primary : AppColors.border,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                color: isSelected ? Colors.white : Colors.white.withOpacity(0.7),
              ),
            ),
            if (count > 0) ...[
              const SizedBox(width: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: isSelected ? Colors.white.withOpacity(0.2) : AppColors.primary.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  count.toString(),
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: isSelected ? Colors.white : AppColors.primary,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildBody(BuildContext context, NotificationState state) {
    if (state.status == NotificationStatus.loading && state.notifications.isEmpty) {
      return const Center(
        child: CircularProgressIndicator(color: AppColors.primary),
      );
    }

    if (state.status == NotificationStatus.failure && state.notifications.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error_outline_rounded, size: 48, color: Colors.red.shade400),
            const SizedBox(height: 12),
            const Text(
              'Failed to load notifications',
              style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              state.errorMessage ?? 'Please check your connection',
              style: TextStyle(color: Colors.white.withOpacity(0.6), fontSize: 12),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => context.read<NotificationCubit>().loadNotifications(refresh: true),
              style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
              child: const Text('Retry', style: TextStyle(color: Colors.white)),
            ),
          ],
        ),
      );
    }

    final items = state.displayedNotifications;

    if (items.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.surface,
                shape: BoxShape.circle,
                border: Border.all(color: AppColors.border),
              ),
              child: Icon(
                state.selectedFilter == 'unread'
                    ? Icons.mark_email_read_rounded
                    : Icons.notifications_none_rounded,
                size: 44,
                color: Colors.white.withOpacity(0.4),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              state.selectedFilter == 'unread'
                  ? 'All Caught Up!'
                  : 'No Notifications Yet',
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              state.selectedFilter == 'unread'
                  ? 'You have read all received updates.'
                  : 'Daily spotlight wallpapers and news will appear here.',
              style: TextStyle(
                fontSize: 12,
                color: Colors.white.withOpacity(0.5),
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      color: AppColors.primary,
      backgroundColor: AppColors.surface,
      onRefresh: () => context.read<NotificationCubit>().loadNotifications(refresh: true),
      child: ListView.separated(
        controller: _scrollController,
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        itemCount: items.length + (state.hasMore ? 1 : 0),
        separatorBuilder: (_, __) => const SizedBox(height: 10),
        itemBuilder: (context, index) {
          if (index >= items.length) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.symmetric(vertical: 16),
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary),
                ),
              ),
            );
          }

          final item = items[index];
          return NotificationItemCard(
            notification: item,
            onTap: () => context.read<NotificationCubit>().markAsRead(item.id),
            onDismissed: () => context.read<NotificationCubit>().deleteNotification(item.id),
          );
        },
      ),
    );
  }
}
