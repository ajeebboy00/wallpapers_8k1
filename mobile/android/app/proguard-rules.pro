# =====================================================================
# WALLPAPERS_8K1 (W8K1) - PROGUARD / R8 RELEASE OBFUSCATION RULES
# =====================================================================

# Flutter Framework Internals
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.**  { *; }
-keep class io.flutter.util.**  { *; }
-keep class io.flutter.view.**  { *; }
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }

# Keep native methods and JNI callbacks
-keepclasseswithmembernames class * {
    native <methods>;
}

# Preserve Flutter generated plugins registration
-keep class io.flutter.plugins.GeneratedPluginRegistrant { *; }

# AndroidX & Support Libraries
-keep class androidx.core.app.** { *; }
-dontwarn androidx.**

# Gson / JSON Model Serialization
-keepattributes Signature
-keepattributes *Annotation*
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}

# Kotlin Coroutines & Stdlib
-dontwarn kotlin.**
-keep class kotlin.Metadata { *; }
-keepclassmembers class kotlin.Metadata {
    public <methods>;
}

# Image Cache & Wallpaper Setter Plugins
-keep class com.dexterous.flutterlocalnotifications.** { *; }
-dontwarn com.dexterous.flutterlocalnotifications.**

# Security & SharedPreferences / Biometrics
-keep class androidx.security.crypto.** { *; }
-dontwarn androidx.security.crypto.**

# Google Play Core & Flutter Deferred Components
-dontwarn com.google.android.play.core.**

