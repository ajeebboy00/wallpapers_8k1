import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_cache_manager/flutter_cache_manager.dart';

import 'package:wallpapers_8k1/core/constants/app_constants.dart';
import 'package:wallpapers_8k1/core/theme/app_colors.dart';
import 'package:wallpapers_8k1/core/theme/theme_cubit.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  String _selectedQuality = '8K';
  bool _isClearingCache = false;

  Future<void> _clearCache() async {
    setState(() => _isClearingCache = true);
    try {
      await DefaultCacheManager().emptyCache();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Image cache cleared successfully'),
            backgroundColor: AppColors.primary,
          ),
        );
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Failed to clear cache'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isClearingCache = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final themeCubit = context.watch<ThemeCubit>();
    final currentThemeMode = themeCubit.state;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Settings & Preferences', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20)),
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
        children: [
          // Section: Appearance
          _buildSectionHeader('Appearance & Display'),
          Container(
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.brightness_auto_rounded, color: AppColors.primary),
                  title: const Text('Theme Mode', style: TextStyle(fontWeight: FontWeight.w600)),
                  subtitle: Text(
                    currentThemeMode == ThemeMode.system
                        ? 'Follow System'
                        : currentThemeMode == ThemeMode.dark
                            ? 'AMOLED Dark'
                            : 'Light Mode',
                    style: const TextStyle(color: AppColors.textSecondary, fontSize: 13),
                  ),
                  trailing: DropdownButton<ThemeMode>(
                    value: currentThemeMode,
                    dropdownColor: AppColors.surfaceElevated,
                    underline: const SizedBox.shrink(),
                    items: const [
                      DropdownMenuItem(value: ThemeMode.system, child: Text('System')),
                      DropdownMenuItem(value: ThemeMode.dark, child: Text('Dark AMOLED')),
                      DropdownMenuItem(value: ThemeMode.light, child: Text('Light')),
                    ],
                    onChanged: (mode) {
                      if (mode != null) themeCubit.setThemeMode(mode);
                    },
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Section: Quality & Downloads
          _buildSectionHeader('Quality & Downloads'),
          Container(
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.high_quality_rounded, color: AppColors.primary),
                  title: const Text('Preferred Resolution', style: TextStyle(fontWeight: FontWeight.w600)),
                  subtitle: Text(
                    'Default image quality for wallpaper previews: $_selectedQuality',
                    style: const TextStyle(color: AppColors.textSecondary, fontSize: 13),
                  ),
                  trailing: DropdownButton<String>(
                    value: _selectedQuality,
                    dropdownColor: AppColors.surfaceElevated,
                    underline: const SizedBox.shrink(),
                    items: const [
                      DropdownMenuItem(value: '8K', child: Text('8K Ultra HD')),
                      DropdownMenuItem(value: '4K', child: Text('4K UHD')),
                      DropdownMenuItem(value: '2K', child: Text('2K QHD')),
                      DropdownMenuItem(value: 'FHD', child: Text('1080p FHD')),
                    ],
                    onChanged: (val) {
                      if (val != null) setState(() => _selectedQuality = val);
                    },
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Section: Storage
          _buildSectionHeader('Storage & Cache'),
          Container(
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
            ),
            child: ListTile(
              leading: const Icon(Icons.cleaning_services_rounded, color: AppColors.primary),
              title: const Text('Clear Image Cache', style: TextStyle(fontWeight: FontWeight.w600)),
              subtitle: const Text('Free up disk space from cached thumbnails', style: TextStyle(color: AppColors.textSecondary, fontSize: 13)),
              trailing: _isClearingCache
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary))
                  : TextButton(
                      onPressed: _clearCache,
                      child: const Text('Clear', style: TextStyle(color: AppColors.error)),
                    ),
            ),
          ),
          const SizedBox(height: 24),

          // Section: About
          _buildSectionHeader('About Platform'),
          Container(
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.info_outline_rounded, color: AppColors.primary),
                  title: const Text('Application Version', style: TextStyle(fontWeight: FontWeight.w600)),
                  trailing: const Text('${AppConstants.appShortBrand} v${AppConstants.appVersion}', style: TextStyle(color: AppColors.textSecondary)),
                ),
                const Divider(color: AppColors.divider, height: 1),
                const ListTile(
                  leading: Icon(Icons.verified_user_outlined, color: AppColors.primary),
                  title: Text('Architecture Grade', style: TextStyle(fontWeight: FontWeight.w600)),
                  trailing: Text('Production-Grade 8K', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold)),
                ),
              ],
            ),
          ),
          const SizedBox(height: 40),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 8.0, bottom: 8.0),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: AppColors.primary,
          letterSpacing: 0.5,
        ),
      ),
    );
  }
}
