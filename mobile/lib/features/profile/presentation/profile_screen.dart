import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/network/api_client.dart';
import '../../../../core/storage/secure_storage_service.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/models/user_model.dart';
import '../../auth/data/auth_remote_data_source.dart';
import '../../auth/data/auth_repository.dart';
import '../../auth/presentation/bloc/auth_cubit.dart';
import '../../auth/presentation/bloc/auth_state.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider<AuthCubit>(
      create: (context) {
        final storage = SecureStorageService();
        final apiClient = ApiClient(storage: storage);
        final dataSource = AuthRemoteDataSource(apiClient);
        final repository = AuthRepository(dataSource, storage);
        return AuthCubit(repository)..checkAuthStatus();
      },
      child: const _ProfileScreenContent(),
    );
  }
}

class _ProfileScreenContent extends StatelessWidget {
  const _ProfileScreenContent();

  void _showEditProfileSheet(BuildContext context, UserModel user, AuthCubit authCubit) {
    final nameController = TextEditingController(text: user.name);
    final storage = SecureStorageService();
    final apiClient = ApiClient(storage: storage);

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.surface,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(
          left: 20,
          right: 20,
          top: 16,
          bottom: MediaQuery.of(ctx).viewInsets.bottom + 24,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(width: 40, height: 4, decoration: BoxDecoration(color: Colors.white24, borderRadius: BorderRadius.circular(2))),
            ),
            const SizedBox(height: 16),
            const Text('Edit Profile', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
            const SizedBox(height: 16),
            TextField(
              controller: nameController,
              style: const TextStyle(color: AppColors.textPrimary),
              decoration: const InputDecoration(labelText: 'Display Name', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, foregroundColor: Colors.white),
                onPressed: () async {
                  final newName = nameController.text.trim();
                  if (newName.isNotEmpty) {
                    try {
                      final resp = await apiClient.put('/users/me', data: {'name': newName});
                      final updated = UserModel.fromJson(resp.data['data'] as Map<String, dynamic>);
                      authCubit.updateUser(updated);
                      if (ctx.mounted) Navigator.of(ctx).pop();
                    } catch (_) {}
                  }
                },
                child: const Text('Save Changes', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showNotificationPreferences(BuildContext context) async {
    final storage = SecureStorageService();
    final apiClient = ApiClient(storage: storage);

    try {
      final resp = await apiClient.get('/users/me/notification-preferences');
      var prefs = NotificationPreferenceModel.fromJson(resp.data['data'] as Map<String, dynamic>);

      if (!context.mounted) return;

      showModalBottomSheet(
        context: context,
        backgroundColor: AppColors.surface,
        shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
        builder: (ctx) => StatefulBuilder(
          builder: (ctx, setSheetState) => SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Container(width: 40, height: 4, decoration: BoxDecoration(color: Colors.white24, borderRadius: BorderRadius.circular(2))),
                  ),
                  const SizedBox(height: 16),
                  const Text('Notification Preferences', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                  const SizedBox(height: 16),
                  SwitchListTile(
                    title: const Text('Daily Wallpaper Spotlight'),
                    value: prefs.dailyWallpaper,
                    activeColor: AppColors.primary,
                    onChanged: (val) async {
                      setSheetState(() => prefs = prefs.copyWith(dailyWallpaper: val));
                      await apiClient.put('/users/me/notification-preferences', data: {'daily_wallpaper': val});
                    },
                  ),
                  SwitchListTile(
                    title: const Text('New 8K Arrivals'),
                    value: prefs.newWallpapers,
                    activeColor: AppColors.primary,
                    onChanged: (val) async {
                      setSheetState(() => prefs = prefs.copyWith(newWallpapers: val));
                      await apiClient.put('/users/me/notification-preferences', data: {'new_wallpapers': val});
                    },
                  ),
                  SwitchListTile(
                    title: const Text('Curated Collections'),
                    value: prefs.newCollections,
                    activeColor: AppColors.primary,
                    onChanged: (val) async {
                      setSheetState(() => prefs = prefs.copyWith(newCollections: val));
                      await apiClient.put('/users/me/notification-preferences', data: {'new_collections': val});
                    },
                  ),
                ],
              ),
            ),
          ),
        ),
      );
    } catch (_) {}
  }

  void _confirmLogout(BuildContext context, AuthCubit authCubit) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.surface,
        title: const Text('Log Out', style: TextStyle(color: AppColors.textPrimary)),
        content: const Text('Are you sure you want to sign out?', style: TextStyle(color: AppColors.textSecondary)),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Cancel', style: TextStyle(color: AppColors.textTertiary)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.error),
            onPressed: () {
              Navigator.of(ctx).pop();
              authCubit.logout();
            },
            child: const Text('Log Out', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('My Profile', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20)),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            tooltip: 'Settings',
            onPressed: () => context.push('/settings'),
          ),
        ],
      ),
      body: BlocBuilder<AuthCubit, AuthState>(
        builder: (context, state) {
          final authCubit = context.read<AuthCubit>();

          if (state is AuthLoading) {
            return const Center(child: CircularProgressIndicator(color: AppColors.primary));
          }

          if (state is Authenticated) {
            final user = state.user;
            final initial = user.name.isNotEmpty ? user.name[0].toUpperCase() : 'U';

            return ListView(
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 16.0),
              children: [
                // User Card
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppColors.surface,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: Colors.white10),
                  ),
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 34,
                        backgroundColor: AppColors.primary,
                        child: Text(
                          initial,
                          style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              user.name,
                              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              user.email,
                              style: const TextStyle(fontSize: 13, color: AppColors.textSecondary),
                            ),
                            const SizedBox(height: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: AppColors.primary.withOpacity(0.2),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                user.role.toUpperCase(),
                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.primary),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // W8K Pro Upgrade Banner
                GestureDetector(
                  onTap: () => context.push('/paywall'),
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF6D28D9), Color(0xFF4C1D95)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFF8B5CF6).withOpacity(0.5)),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFF6D28D9).withOpacity(0.3),
                          blurRadius: 10,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.15),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(Icons.workspace_premium_rounded, color: Colors.amberAccent, size: 28),
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: const [
                              Text(
                                'W8K Pro VIP Access',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                ),
                              ),
                              SizedBox(height: 2),
                              Text(
                                'Unlimited 8K UHD downloads & 100% ad-free',
                                style: TextStyle(
                                  color: Colors.white70,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const Icon(Icons.arrow_forward_ios_rounded, color: Colors.white, size: 14),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Library Counters Row
                Row(
                  children: [
                    Expanded(
                      child: GestureDetector(
                        onTap: () => context.push('/favorites'),
                        child: Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: AppColors.surface,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: Colors.white10),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Icon(Icons.favorite_rounded, color: AppColors.error, size: 24),
                              const SizedBox(height: 12),
                              Text(
                                '${user.favoritesCount}',
                                style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                              ),
                              const SizedBox(height: 4),
                              const Text('Saved Favorites', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                            ],
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: GestureDetector(
                        onTap: () => context.push('/downloads'),
                        child: Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: AppColors.surface,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: Colors.white10),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Icon(Icons.download_done_rounded, color: AppColors.primary, size: 24),
                              const SizedBox(height: 12),
                              Text(
                                '${user.downloadsCount}',
                                style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                              ),
                              const SizedBox(height: 4),
                              const Text('Download History', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // Options List
                Container(
                  decoration: BoxDecoration(
                    color: AppColors.surface,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Column(
                    children: [
                      ListTile(
                        leading: const Icon(Icons.edit_outlined, color: AppColors.primary),
                        title: const Text('Edit Profile'),
                        trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: AppColors.textTertiary),
                        onTap: () => _showEditProfileSheet(context, user, authCubit),
                      ),
                      const Divider(color: AppColors.divider, height: 1),
                      ListTile(
                        leading: const Icon(Icons.notifications_outlined, color: AppColors.primary),
                        title: const Text('Notification Preferences'),
                        trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: AppColors.textTertiary),
                        onTap: () => _showNotificationPreferences(context),
                      ),
                      const Divider(color: AppColors.divider, height: 1),
                      ListTile(
                        leading: const Icon(Icons.workspace_premium_outlined, color: AppColors.accent),
                        title: const Text('Subscription & VIP Plan'),
                        trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: AppColors.textTertiary),
                        onTap: () => context.push('/paywall'),
                      ),
                      const Divider(color: AppColors.divider, height: 1),
                      ListTile(
                        leading: const Icon(Icons.palette_outlined, color: AppColors.primary),
                        title: const Text('Settings & Preferences'),
                        trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: AppColors.textTertiary),
                        onTap: () => context.push('/settings'),
                      ),
                      const Divider(color: AppColors.divider, height: 1),
                      ListTile(
                        leading: const Icon(Icons.logout_rounded, color: AppColors.error),
                        title: const Text('Log Out', style: TextStyle(color: AppColors.error)),
                        onTap: () => _confirmLogout(context, authCubit),
                      ),
                    ],
                  ),
                ),
              ],
            );
          }

          // Unauthenticated State View
          return Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 32.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: const BoxDecoration(
                      color: AppColors.surface,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.person_outline_rounded, size: 64, color: AppColors.primary),
                  ),
                  const SizedBox(height: 24),
                  const Text(
                    'Welcome to Wallpapers_8k1',
                    style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Sign in to synchronize your favorite 8K wallpapers, download history, and preferences across devices.',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 14, color: AppColors.textSecondary, height: 1.4),
                  ),
                  const SizedBox(height: 32),
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      onPressed: () async {
                        await context.push('/login');
                        authCubit.checkAuthStatus();
                      },
                      child: const Text('Sign In', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    ),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: OutlinedButton(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppColors.primary,
                        side: const BorderSide(color: AppColors.primary),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      onPressed: () async {
                        await context.push('/register');
                        authCubit.checkAuthStatus();
                      },
                      child: const Text('Create Account', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    ),
                  ),
                  const SizedBox(height: 32),
                  Container(
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: ListTile(
                      leading: const Icon(Icons.settings_outlined, color: AppColors.primary),
                      title: const Text('Theme & Display Settings'),
                      trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: AppColors.textTertiary),
                      onTap: () => context.push('/settings'),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
