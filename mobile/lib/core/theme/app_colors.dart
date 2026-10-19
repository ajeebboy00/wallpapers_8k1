import 'package:flutter/material.dart';

/// Design system color palette for Wallpapers_8k1
class AppColors {
  // Brand Accents
  static const Color primary = Color(0xFF8B5CF6); // Deep Electric Violet
  static const Color primaryLight = Color(0xFFA78BFA);
  static const Color primaryDark = Color(0xFF6D28D9);
  static const Color accent = Color(0xFF38BDF8); // Cyan Accent

  // AMOLED Dark Theme Surfaces
  static const Color darkBackground = Color(0xFF0A0A0C);
  static const Color darkSurface = Color(0xFF121217);
  static const Color darkSurfaceElevated = Color(0xFF1A1A22);
  static const Color darkBorder = Color(0xFF22222E);

  // Light Theme Surfaces
  static const Color lightBackground = Color(0xFFF8FAFC);
  static const Color lightSurface = Color(0xFFFFFFFF);
  static const Color lightSurfaceElevated = Color(0xFFF1F5F9);
  static const Color lightBorder = Color(0xFFE2E8F0);

  // Typography Colors
  static const Color textDarkPrimary = Color(0xFFF8FAFC);
  static const Color textDarkSecondary = Color(0xFF94A3B8);
  static const Color textDarkMuted = Color(0xFF64748B);

  static const Color textLightPrimary = Color(0xFF0F172A);
  static const Color textLightSecondary = Color(0xFF475569);
  static const Color textLightMuted = Color(0xFF94A3B8);

  // Status & Badges
  static const Color success = Color(0xFF10B981);
  static const Color warning = Color(0xFFF59E0B);
  static const Color error = Color(0xFFEF4444);
  static const Color favorite = Color(0xFFFF3366);

  // Convenience Aliases (AMOLED Dark)
  static const Color background = darkBackground;
  static const Color surface = darkSurface;
  static const Color surfaceElevated = darkSurfaceElevated;
  static const Color border = darkBorder;
  static const Color divider = darkBorder;
  static const Color textPrimary = textDarkPrimary;
  static const Color textSecondary = textDarkSecondary;
  static const Color textTertiary = textDarkMuted;
}
