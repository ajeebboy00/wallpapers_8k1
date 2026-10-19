import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:wallpapers_8k1/core/network/api_client.dart';
import 'package:wallpapers_8k1/core/storage/secure_storage_service.dart';
import 'package:wallpapers_8k1/core/theme/app_colors.dart';
import '../../data/monetization_repository.dart';

class AdRewardDialog extends StatefulWidget {
  final String wallpaperId;
  final String wallpaperTitle;
  final VoidCallback onUnlocked;

  const AdRewardDialog({
    super.key,
    required this.wallpaperId,
    required this.wallpaperTitle,
    required this.onUnlocked,
  });

  static Future<void> show(
    BuildContext context, {
    required String wallpaperId,
    required String wallpaperTitle,
    required VoidCallback onUnlocked,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: true,
      builder: (context) => AdRewardDialog(
        wallpaperId: wallpaperId,
        wallpaperTitle: wallpaperTitle,
        onUnlocked: onUnlocked,
      ),
    );
  }

  @override
  State<AdRewardDialog> createState() => _AdRewardDialogState();
}

class _AdRewardDialogState extends State<AdRewardDialog> {
  bool _isWatchingAd = false;
  String? _errorMessage;

  Future<void> _watchAdAndUnlock() async {
    setState(() {
      _isWatchingAd = true;
      _errorMessage = null;
    });

    try {
      final storage = SecureStorageService();
      final apiClient = ApiClient(storage: storage);
      final repo = MonetizationRepository(apiClient);

      final txId = 'admob_tx_${DateTime.now().millisecondsSinceEpoch}';
      final res = await repo.claimAdReward(
        wallpaperId: widget.wallpaperId,
        transactionId: txId,
      );

      if (mounted) {
        setState(() {
          _isWatchingAd = false;
        });

        if (res['unlocked'] == true) {
          Navigator.of(context).pop();
          widget.onUnlocked();
        } else {
          setState(() {
            _errorMessage = 'Could not verify ad completion. Please try again.';
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isWatchingAd = false;
          _errorMessage = 'Failed to claim reward unlock. Check your connection.';
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: AppColors.darkSurface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: AppColors.darkBorder),
      ),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Icon
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.15),
                shape: BoxShape.circle,
                border: Border.all(color: AppColors.primary.withOpacity(0.3)),
              ),
              child: const Icon(
                Icons.ondemand_video_rounded,
                color: AppColors.primaryLight,
                size: 28,
              ),
            ),
            const SizedBox(height: 16),

            // Title
            const Text(
              '8K UHD Master Asset',
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),

            // Description
            Text(
              'Watch a short sponsored video to unlock full 8K uncompressed download for "${widget.wallpaperTitle}" for 24 hours, or upgrade to W8K Pro for zero ads forever.',
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: AppColors.textDarkSecondary,
                fontSize: 13,
                height: 1.4,
              ),
            ),
            const SizedBox(height: 20),

            if (_errorMessage != null) ...[
              Text(
                _errorMessage!,
                style: const TextStyle(color: AppColors.error, fontSize: 12),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),
            ],

            // Watch Ad Button
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton.icon(
                onPressed: _isWatchingAd ? null : _watchAdAndUnlock,
                icon: _isWatchingAd
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                      )
                    : const Icon(Icons.play_circle_outline, size: 20),
                label: Text(
                  _isWatchingAd ? 'Processing Reward...' : 'Watch Short Video (Free 8K)',
                  style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
            const SizedBox(height: 10),

            // Upgrade to Pro Button
            SizedBox(
              width: double.infinity,
              height: 48,
              child: OutlinedButton.icon(
                onPressed: () {
                  Navigator.of(context).pop();
                  context.push('/paywall');
                },
                icon: const Icon(Icons.workspace_premium, size: 20, color: AppColors.accent),
                label: const Text(
                  'Get 8K Pro (Zero Ads)',
                  style: TextStyle(
                    color: AppColors.accent,
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                  ),
                ),
                style: OutlinedButton.styleFrom(
                  side: BorderSide(color: AppColors.accent.withOpacity(0.5)),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
            const SizedBox(height: 6),

            // Cancel
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text(
                'Maybe Later',
                style: TextStyle(color: AppColors.textDarkMuted, fontSize: 13),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
