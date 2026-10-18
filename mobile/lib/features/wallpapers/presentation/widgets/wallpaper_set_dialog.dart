import 'package:flutter/material.dart';
import '../../../../core/services/wallpaper_setter_service.dart';
import '../../../../core/theme/app_colors.dart';

class WallpaperSetDialog extends StatelessWidget {
  const WallpaperSetDialog({super.key});

  static Future<WallpaperDestination?> show(BuildContext context) {
    return showModalBottomSheet<WallpaperDestination>(
      context: context,
      backgroundColor: AppColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) => const WallpaperSetDialog(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Handle bar
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.white24,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),

            const Text(
              'Set as Wallpaper',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 6),
            const Text(
              'Choose which screen you want to apply this wallpaper to:',
              style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
            ),
            const SizedBox(height: 16),

            _buildOptionTile(
              context: context,
              destination: WallpaperDestination.home,
              icon: Icons.home_rounded,
              title: 'Home Screen',
              subtitle: 'Apply to device home screen only',
            ),
            const Divider(color: AppColors.divider, height: 1),

            _buildOptionTile(
              context: context,
              destination: WallpaperDestination.lock,
              icon: Icons.lock_outline_rounded,
              title: 'Lock Screen',
              subtitle: 'Apply to device lock screen only',
            ),
            const Divider(color: AppColors.divider, height: 1),

            _buildOptionTile(
              context: context,
              destination: WallpaperDestination.both,
              icon: Icons.smartphone_rounded,
              title: 'Both Screens',
              subtitle: 'Apply to both home and lock screens',
              isHighlight: true,
            ),
            const SizedBox(height: 12),
          ],
        ),
      ),
    );
  }

  Widget _buildOptionTile({
    required BuildContext context,
    required WallpaperDestination destination,
    required IconData icon,
    required String title,
    required String subtitle,
    bool isHighlight = false,
  }) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      leading: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: isHighlight ? AppColors.primary.withOpacity(0.15) : AppColors.surfaceElevated,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Icon(
          icon,
          color: isHighlight ? AppColors.primary : AppColors.textPrimary,
          size: 22,
        ),
      ),
      title: Text(
        title,
        style: TextStyle(
          fontSize: 15,
          fontWeight: FontWeight.w600,
          color: isHighlight ? AppColors.primary : AppColors.textPrimary,
        ),
      ),
      subtitle: Text(
        subtitle,
        style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
      ),
      trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: AppColors.textTertiary),
      onTap: () => Navigator.of(context).pop(destination),
    );
  }
}
