import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import '../../../../shared/models/wallpaper_model.dart';
import '../../../../shared/widgets/shimmer_placeholder.dart';

class FullscreenImageViewer extends StatefulWidget {
  final WallpaperModel wallpaper;
  final VoidCallback onToggleChrome;

  const FullscreenImageViewer({
    super.key,
    required this.wallpaper,
    required this.onToggleChrome,
  });

  @override
  State<FullscreenImageViewer> createState() => _FullscreenImageViewerState();
}

class _FullscreenImageViewerState extends State<FullscreenImageViewer>
    with SingleTickerProviderStateMixin {
  late final TransformationController _transformationController;
  late final AnimationController _animationController;
  Animation<Matrix4>? _animation;

  @override
  void initState() {
    super.initState();
    _transformationController = TransformationController();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 250),
    )..addListener(() {
        if (_animation != null) {
          _transformationController.value = _animation!.value;
        }
      });
  }

  @override
  void dispose() {
    _transformationController.dispose();
    _animationController.dispose();
    super.dispose();
  }

  void _handleDoubleTap(TapDownDetails details) {
    if (_animationController.isAnimating) return;

    final currentMatrix = _transformationController.value;
    final currentScale = currentMatrix.getMaxScaleOnAxis();

    final Matrix4 endMatrix;
    if (currentScale > 1.2) {
      // Zoom out to 1.0x
      endMatrix = Matrix4.identity();
    } else {
      // Zoom in to 2.5x centered on tap position
      final position = details.localPosition;
      endMatrix = Matrix4.identity()
        ..translate(-position.dx * 1.5, -position.dy * 1.5)
        ..scale(2.5);
    }

    _animation = Matrix4Tween(
      begin: currentMatrix,
      end: endMatrix,
    ).animate(CurvedAnimation(parent: _animationController, curve: Curves.easeOutCubic));

    _animationController.forward(from: 0);
  }

  @override
  Widget build(BuildContext context) {
    // Load previewUrl (or thumbnailUrl) for smooth high-res rendering
    final displayUrl = widget.wallpaper.previewUrl.isNotEmpty
        ? widget.wallpaper.previewUrl
        : widget.wallpaper.imageUrl;

    final lowResUrl = widget.wallpaper.thumbnailUrl;

    return GestureDetector(
      onTap: widget.onToggleChrome,
      onDoubleTapDown: _handleDoubleTap,
      child: Container(
        color: Colors.black,
        width: double.infinity,
        height: double.infinity,
        child: InteractiveViewer(
          transformationController: _transformationController,
          minScale: 1.0,
          maxScale: 4.0,
          clipBehavior: Clip.none,
          child: Center(
            child: CachedNetworkImage(
              imageUrl: displayUrl,
              fit: BoxFit.contain,
              width: double.infinity,
              height: double.infinity,
              placeholder: (context, url) {
                if (lowResUrl.isNotEmpty) {
                  return CachedNetworkImage(
                    imageUrl: lowResUrl,
                    fit: BoxFit.contain,
                  );
                }
                return const Center(child: ShimmerPlaceholder(width: double.infinity, height: double.infinity));
              },
              errorWidget: (context, url, error) => const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.broken_image_rounded, size: 64, color: Colors.white24),
                    SizedBox(height: 12),
                    Text('Failed to load full image', style: TextStyle(color: Colors.white54)),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
