import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:wallpapers_8k1/core/theme/app_colors.dart';
import 'package:wallpapers_8k1/shared/models/notification_model.dart';

class NotificationItemCard extends StatelessWidget {
  final NotificationModel notification;
  final VoidCallback onTap;
  final VoidCallback onDismissed;

  const NotificationItemCard({
    super.key,
    required this.notification,
    required this.onTap,
    required this.onDismissed,
  });

  @override
  Widget build(BuildContext context) {
    return Dismissible(
      key: Key(notification.id),
      direction: DismissDirection.endToStart,
      onDismissed: (_) => onDismissed(),
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.symmetric(horizontal: 20),
        decoration: BoxDecoration(
          color: Colors.red.shade900.withOpacity(0.4),
          borderRadius: BorderRadius.circular(16),
        ),
        child: const Icon(Icons.delete_outline_rounded, color: Colors.redAccent),
      ),
      child: InkWell(
        onTap: () {
          onTap();
          _handleNavigation(context);
        },
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: notification.isRead
                ? AppColors.surface.withOpacity(0.6)
                : AppColors.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: notification.isRead
                  ? AppColors.border.withOpacity(0.4)
                  : AppColors.primary.withOpacity(0.4),
              width: notification.isRead ? 1 : 1.5,
            ),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Icon Badge
              _buildTypeIcon(),
              const SizedBox(width: 12),

              // Content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          child: Text(
                            notification.title,
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: notification.isRead
                                  ? FontWeight.w600
                                  : FontWeight.bold,
                              color: notification.isRead
                                  ? Colors.white.withOpacity(0.9)
                                  : Colors.white,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          notification.timeAgo,
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.white.withOpacity(0.4),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      notification.message,
                      style: TextStyle(
                        fontSize: 12,
                        height: 1.35,
                        color: Colors.white.withOpacity(0.7),
                      ),
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),

              // Optional Thumbnail or Unread Dot
              if (notification.imageUrl != null) ...[
                const SizedBox(width: 10),
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.network(
                    notification.imageUrl!,
                    width: 44,
                    height: 60,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => const SizedBox.shrink(),
                  ),
                ),
              ] else if (!notification.isRead) ...[
                const SizedBox(width: 8),
                Container(
                  width: 8,
                  height: 8,
                  margin: const EdgeInsets.only(top: 4),
                  decoration: const BoxDecoration(
                    color: AppColors.primary,
                    shape: BoxShape.circle,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTypeIcon() {
    IconData icon;
    Color iconColor;
    Color bgColor;

    switch (notification.type) {
      case 'DAILY_WALLPAPER':
        icon = Icons.auto_awesome_rounded;
        iconColor = Colors.amber;
        bgColor = Colors.amber.withOpacity(0.15);
        break;
      case 'FEATURED':
        icon = Icons.star_rounded;
        iconColor = Colors.orangeAccent;
        bgColor = Colors.orangeAccent.withOpacity(0.15);
        break;
      case 'NEW_WALLPAPER':
        icon = Icons.image_rounded;
        iconColor = AppColors.primary;
        bgColor = AppColors.primary.withOpacity(0.15);
        break;
      case 'NEW_COLLECTION':
        icon = Icons.collections_bookmark_rounded;
        iconColor = Colors.cyanAccent;
        bgColor = Colors.cyanAccent.withOpacity(0.15);
        break;
      case 'PROMOTIONAL':
        icon = Icons.local_fire_department_rounded;
        iconColor = Colors.pinkAccent;
        bgColor = Colors.pinkAccent.withOpacity(0.15);
        break;
      case 'SYSTEM':
      default:
        icon = Icons.info_outline_rounded;
        iconColor = Colors.blueAccent;
        bgColor = Colors.blueAccent.withOpacity(0.15);
    }

    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Icon(icon, color: iconColor, size: 20),
    );
  }

  void _handleNavigation(BuildContext context) {
    if (notification.wallpaperId != null) {
      context.push('/wallpaper/${notification.wallpaperId}');
    } else if (notification.collectionId != null) {
      context.push('/collections');
    }
  }
}
