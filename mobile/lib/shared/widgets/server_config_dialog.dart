import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/config/app_config.dart';
import '../../core/theme/app_colors.dart';

Future<void> showServerConfigDialog(
  BuildContext context, {
  VoidCallback? onSaved,
}) async {
  final prefs = await SharedPreferences.getInstance();
  final currentUrl = AppConfig.current.apiBaseUrl;

  // Extract host/ip:port from current URL for easy editing
  String initialHost = currentUrl
      .replaceAll('http://', '')
      .replaceAll('https://', '')
      .replaceAll('/api/v1', '');

  final controller = TextEditingController(text: initialHost);

  if (!context.mounted) return;

  await showDialog(
    context: context,
    builder: (dialogContext) {
      return AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.wifi_tethering_rounded, color: AppColors.primary),
            SizedBox(width: 10),
            Text('Server IP Settings', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Enter your PC IP address and port to connect over any Wi-Fi or Hotspot network:',
                style: TextStyle(fontSize: 13, color: AppColors.textDarkMuted),
              ),
              const SizedBox(height: 14),
              TextField(
                controller: controller,
                decoration: InputDecoration(
                  labelText: 'PC IP:Port',
                  hintText: 'e.g. 10.72.10.121:8000',
                  prefixIcon: const Icon(Icons.computer_rounded, size: 20),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                ),
              ),
              const SizedBox(height: 12),
              const Text(
                'Quick Presets:',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.textDarkMuted),
              ),
              const SizedBox(height: 6),
              Wrap(
                spacing: 6,
                runSpacing: 4,
                children: [
                  ActionChip(
                    label: const Text('10.72.10.121:8000', style: TextStyle(fontSize: 11)),
                    onPressed: () => controller.text = '10.72.10.121:8000',
                  ),
                  ActionChip(
                    label: const Text('192.168.1.10:8000', style: TextStyle(fontSize: 11)),
                    onPressed: () => controller.text = '192.168.1.10:8000',
                  ),
                  ActionChip(
                    label: const Text('10.0.2.2:8000', style: TextStyle(fontSize: 11)),
                    onPressed: () => controller.text = '10.0.2.2:8000',
                  ),
                ],
              ),
              const SizedBox(height: 10),
              ValueListenableBuilder<String>(
                valueListenable: AppConfig.baseUrlNotifier,
                builder: (context, activeUrl, _) {
                  return Text(
                    'Active Base URL:\n$activeUrl',
                    style: const TextStyle(fontSize: 11, fontFamily: 'monospace', color: AppColors.primaryLight),
                  );
                },
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              String raw = controller.text.trim();
              if (raw.isEmpty) return;

              String fullUrl;
              if (raw.startsWith('http://') || raw.startsWith('https://')) {
                fullUrl = raw;
              } else {
                fullUrl = 'http://$raw';
              }

              if (!fullUrl.endsWith('/api/v1')) {
                fullUrl = fullUrl.endsWith('/') ? '${fullUrl}api/v1' : '$fullUrl/api/v1';
              }

              await prefs.setString('custom_api_base_url', fullUrl);
              AppConfig.updateApiBaseUrl(fullUrl);

              if (dialogContext.mounted) {
                Navigator.of(dialogContext).pop();
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Server connected to: $fullUrl'),
                    backgroundColor: AppColors.primary,
                    duration: const Duration(seconds: 2),
                  ),
                );
              }

              if (onSaved != null) {
                onSaved();
              }
            },
            child: const Text('Save & Connect'),
          ),
        ],
      );
    },
  );
}
