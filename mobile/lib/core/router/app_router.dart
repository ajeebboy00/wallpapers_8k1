import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/presentation/login_screen.dart';
import '../../features/auth/presentation/register_screen.dart';
import '../../features/categories/presentation/categories_screen.dart';
import '../../features/collections/presentation/collections_screen.dart';
import '../../features/downloads/presentation/downloads_screen.dart';
import '../../features/favorites/presentation/favorites_screen.dart';
import '../../features/home/presentation/home_screen.dart';
import '../../features/monetization/presentation/paywall_screen.dart';
import '../../features/notifications/presentation/notification_screen.dart';
import '../../features/profile/presentation/profile_screen.dart';
import '../../features/search/presentation/search_screen.dart';
import '../../features/settings/presentation/settings_screen.dart';
import '../../features/wallpapers/presentation/explore_screen.dart';
import '../../features/wallpapers/presentation/wallpaper_detail_screen.dart';
import '../../shared/widgets/main_shell.dart';

final GlobalKey<NavigatorState> _rootNavigatorKey = GlobalKey<NavigatorState>(debugLabel: 'root');

class AppRouter {
  static final GoRouter router = GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/',
    routes: [
      // Main 5-tab shell navigation
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) {
          return MainShell(navigationShell: navigationShell);
        },
        branches: [
          // Tab 0: Home
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/',
                builder: (context, state) => const HomeScreen(),
              ),
            ],
          ),
          // Tab 1: Explore
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/explore',
                builder: (context, state) => const ExploreScreen(),
              ),
            ],
          ),
          // Tab 2: Categories
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/categories',
                builder: (context, state) => const CategoriesScreen(),
              ),
            ],
          ),
          // Tab 3: Collections
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/collections',
                builder: (context, state) => const CollectionsScreen(),
              ),
            ],
          ),
          // Tab 4: Profile
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/profile',
                builder: (context, state) => const ProfileScreen(),
              ),
            ],
          ),
        ],
      ),

      // Direct Push Routes
      GoRoute(
        path: '/wallpaper/:id',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          return WallpaperDetailScreen(wallpaperId: id);
        },
      ),
      GoRoute(
        path: '/search',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) {
          final query = state.uri.queryParameters['q'];
          final category = state.uri.queryParameters['category'];
          return SearchScreen(
            initialQuery: query,
            initialCategory: category,
          );
        },
      ),
      GoRoute(
        path: '/favorites',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const FavoritesScreen(),
      ),
      GoRoute(
        path: '/downloads',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const DownloadsScreen(),
      ),
      GoRoute(
        path: '/login',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/register',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: '/settings',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const SettingsScreen(),
      ),
      GoRoute(
        path: '/notifications',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const NotificationScreen(),
      ),
      GoRoute(
        path: '/paywall',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const PaywallScreen(),
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      appBar: AppBar(title: const Text('Not Found')),
      body: Center(
        child: Text('Page not found: ${state.uri}'),
      ),
    ),
  );
}
