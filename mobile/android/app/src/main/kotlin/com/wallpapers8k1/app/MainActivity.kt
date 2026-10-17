package com.wallpapers8k1.app

import android.app.WallpaperManager
import android.graphics.BitmapFactory
import android.os.Build
import androidx.annotation.NonNull
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.io.File
import java.io.FileInputStream
import java.io.IOException

class MainActivity: FlutterActivity() {
    private val CHANNEL = "com.wallpapers8k1.app/wallpaper"

    override fun configureFlutterEngine(@NonNull flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "setWallpaper" -> {
                    val filePath = call.argument<String>("filePath")
                    val destination = call.argument<Int>("destination") ?: 3 // 1: Home, 2: Lock, 3: Both

                    if (filePath == null) {
                        result.error("INVALID_ARGUMENT", "File path cannot be null", null)
                        return@setMethodCallHandler
                    }

                    val file = File(filePath)
                    if (!file.exists()) {
                        result.error("FILE_NOT_FOUND", "Wallpaper file does not exist at $filePath", null)
                        return@setMethodCallHandler
                    }

                    try {
                        val wallpaperManager = WallpaperManager.getInstance(applicationContext)
                        val bitmap = BitmapFactory.decodeFile(file.absolutePath)
                        
                        if (bitmap == null) {
                            result.error("DECODE_ERROR", "Failed to decode image file into bitmap", null)
                            return@setMethodCallHandler
                        }

                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                            var which = 0
                            if (destination == 1) {
                                which = WallpaperManager.FLAG_SYSTEM
                            } else if (destination == 2) {
                                which = WallpaperManager.FLAG_LOCK
                            } else {
                                which = WallpaperManager.FLAG_SYSTEM or WallpaperManager.FLAG_LOCK
                            }
                            wallpaperManager.setBitmap(bitmap, null, true, which)
                        } else {
                            // Fallback for pre-Nougat Android
                            wallpaperManager.setBitmap(bitmap)
                        }

                        result.success(true)
                    } catch (e: IOException) {
                        result.error("IO_ERROR", "Failed to set wallpaper: ${e.message}", null)
                    } catch (e: Exception) {
                        result.error("SET_WALLPAPER_ERROR", "Unexpected error: ${e.message}", null)
                    }
                }
                "isSupported" -> {
                    try {
                        val wallpaperManager = WallpaperManager.getInstance(applicationContext)
                        val isSupported = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                            wallpaperManager.isWallpaperSupported && wallpaperManager.isSetWallpaperAllowed
                        } else {
                            true
                        }
                        result.success(isSupported)
                    } catch (e: Exception) {
                        result.success(true)
                    }
                }
                else -> {
                    result.notImplemented()
                }
            }
        }
    }
}
