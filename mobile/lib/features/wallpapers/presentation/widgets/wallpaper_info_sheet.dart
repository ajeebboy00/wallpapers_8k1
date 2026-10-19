import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:wallpapers_8k1/core/theme/app_colors.dart';
import 'package:wallpapers_8k1/shared/models/wallpaper_model.dart';
import 'package:wallpapers_8k1/shared/widgets/wallpaper_card.dart';

class WallpaperInfoSheet extends StatelessWidget {
  final WallpaperModel wallpaper;
  final List<WallpaperModel> relatedWallpapers;
  final Function(String reason, String? description) onReport;

  const WallpaperInfoSheet({
    super.key,
    required this.wallpaper,
    required this.relatedWallpapers,
    required this.onReport,
  });

  static Future<void> show(
    BuildContext context, {
    required WallpaperModel wallpaper,
    required List<WallpaperModel> relatedWallpapers,
    required Function(String reason, String? description) onReport,
  }) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) => WallpaperInfoSheet(
        wallpaper: wallpaper,
        relatedWallpapers: relatedWallpapers,
        onReport: onReport,
      ),
    );
  }

  void _showReportDialog(BuildContext context) {
    String selectedReason = 'INAPPROPRIATE';
    final descController = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setState) => AlertDialog(
          backgroundColor: AppColors.surface,
          title: const Text('Report Wallpaper', style: TextStyle(color: AppColors.textPrimary)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Reason for reporting:', style: TextStyle(color: AppColors.textSecondary, fontSize: 13)),
              const SizedBox(height: 8),
              DropdownButton<String>(
                value: selectedReason,
                isExpanded: true,
                dropdownColor: AppColors.surfaceElevated,
                items: const [
                  DropdownMenuItem(value: 'INAPPROPRIATE', child: Text('Inappropriate Content')),
                  DropdownMenuItem(value: 'COPYRIGHT', child: Text('Copyright Infringement')),
                  DropdownMenuItem(value: 'LOW_QUALITY', child: Text('Low Quality / Fake 8K')),
                  DropdownMenuItem(value: 'WRONG_CATEGORY', child: Text('Wrong Category / Tags')),
                  DropdownMenuItem(value: 'OTHER', child: Text('Other Issue')),
                ],
                onChanged: (val) {
                  if (val != null) setState(() => selectedReason = val);
                },
              ),
              const SizedBox(height: 12),
              TextField(
                controller: descController,
                style: const TextStyle(color: AppColors.textPrimary, fontSize: 13),
                decoration: const InputDecoration(
                  hintText: 'Additional details (optional)',
                  hintStyle: TextStyle(color: AppColors.textTertiary),
                  border: OutlineInputBorder(),
                ),
                maxLines: 2,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(ctx).pop(),
              child: const Text('Cancel', style: TextStyle(color: AppColors.textTertiary)),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: AppColors.error),
              onPressed: () {
                Navigator.of(ctx).pop();
                onReport(selectedReason, descController.text.trim());
              },
              child: const Text('Submit Report', style: TextStyle(color: Colors.white)),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final sizeMb = (wallpaper.fileSize / (1024 * 1024)).toStringAsFixed(1);

    return DraggableScrollableSheet(
      initialChildSize: 0.65,
      minChildSize: 0.4,
      maxChildSize: 0.9,
      expand: false,
      builder: (context, scrollController) {
        return SingleChildScrollView(
          controller: scrollController,
          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Drag handle
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

              // Title and Category
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          wallpaper.title,
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        if (wallpaper.category != null) ...[
                          const SizedBox(height: 4),
                          GestureDetector(
                            onTap: () {
                              Navigator.of(context).pop();
                              context.push('/search?category=${wallpaper.category!.slug}');
                            },
                            child: Text(
                              wallpaper.category!.name,
                              style: const TextStyle(
                                fontSize: 14,
                                color: AppColors.primary,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (wallpaper.isAiGenerated) ...[
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
                          margin: const EdgeInsets.only(right: 6),
                          decoration: BoxDecoration(
                            color: Colors.purple.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.purpleAccent),
                          ),
                          child: const Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.auto_awesome, size: 12, color: Colors.purpleAccent),
                              SizedBox(width: 4),
                              Text(
                                'AI',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w800,
                                  color: Colors.purpleAccent,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: AppColors.primary.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: AppColors.primary),
                        ),
                        child: Text(
                          wallpaper.resolution,
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w900,
                            color: AppColors.primary,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Description
              if (wallpaper.description != null && wallpaper.description!.isNotEmpty) ...[
                Text(
                  wallpaper.description!,
                  style: const TextStyle(
                    fontSize: 14,
                    color: AppColors.textSecondary,
                    height: 1.4,
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // Technical Specs Grid
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.surfaceElevated,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.white10),
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        _buildSpecItem(
                          icon: Icons.aspect_ratio_rounded,
                          label: 'Dimensions',
                          value: '${wallpaper.width} × ${wallpaper.height}',
                        ),
                        _buildSpecItem(
                          icon: Icons.hd_rounded,
                          label: 'Resolution',
                          value: wallpaper.resolution,
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        _buildSpecItem(
                          icon: Icons.data_usage_rounded,
                          label: 'File Size',
                          value: '$sizeMb MB',
                        ),
                        _buildSpecItem(
                          icon: Icons.image_outlined,
                          label: 'Format',
                          value: wallpaper.fileFormat.toUpperCase(),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Engagement Metrics Row
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildMetricItem(Icons.remove_red_eye_outlined, '${wallpaper.viewCount}', 'Views'),
                  _buildMetricItem(Icons.download_rounded, '${wallpaper.downloadCount}', 'Downloads'),
                  _buildMetricItem(Icons.favorite_rounded, '${wallpaper.favoriteCount}', 'Favorites'),
                  _buildMetricItem(Icons.share_outlined, '${wallpaper.shareCount}', 'Shares'),
                ],
              ),
              const SizedBox(height: 20),

              // Tags Section
              if (wallpaper.tags.isNotEmpty) ...[
                const Text(
                  'Tags',
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: wallpaper.tags.map((tag) {
                    return ActionChip(
                      label: Text('#${tag.name}', style: const TextStyle(fontSize: 12, color: AppColors.textPrimary)),
                      backgroundColor: AppColors.surfaceElevated,
                      onPressed: () {
                        Navigator.of(context).pop();
                        context.push('/search?q=${tag.name}');
                      },
                    );
                  }).toList(),
                ),
                const SizedBox(height: 24),
              ],

              // Color Palette Section
              if (wallpaper.colorPalette.isNotEmpty || wallpaper.dominantColor != null) ...[
                const Text(
                  'Color Palette',
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 10,
                  runSpacing: 8,
                  children: [
                    if (wallpaper.dominantColor != null)
                      _buildColorChip(context, wallpaper.dominantColor!, isDominant: true),
                    ...wallpaper.colorPalette
                        .where((c) => c != wallpaper.dominantColor)
                        .map((hex) => _buildColorChip(context, hex)),
                  ],
                ),
                const SizedBox(height: 24),
              ],

              // AI Semantic Tags Section
              if (wallpaper.aiTags.isNotEmpty) ...[
                const Row(
                  children: [
                    Icon(Icons.auto_awesome, size: 16, color: Colors.purpleAccent),
                    SizedBox(width: 6),
                    Text(
                      'AI Semantic Concepts',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: wallpaper.aiTags.map((tag) {
                    return ActionChip(
                      avatar: const Icon(Icons.psychology, size: 14, color: Colors.purpleAccent),
                      label: Text(tag, style: const TextStyle(fontSize: 12, color: AppColors.textPrimary)),
                      backgroundColor: Colors.purple.withOpacity(0.15),
                      side: const BorderSide(color: Colors.purpleAccent, width: 0.5),
                      onPressed: () {
                        Navigator.of(context).pop();
                        context.push('/search?q=$tag');
                      },
                    );
                  }).toList(),
                ),
                const SizedBox(height: 24),
              ],

              // Related Wallpapers Section
              if (relatedWallpapers.isNotEmpty) ...[
                const Text(
                  'More Like This',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 12),
                SizedBox(
                  height: 200,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemCount: relatedWallpapers.length,
                    separatorBuilder: (_, __) => const SizedBox(width: 10),
                    itemBuilder: (context, index) {
                      final rel = relatedWallpapers[index];
                      return SizedBox(
                        width: 112,
                        child: WallpaperCard(
                          id: rel.id,
                          title: rel.title,
                          thumbnailUrl: rel.thumbnailUrl.isNotEmpty ? rel.thumbnailUrl : rel.imageUrl,
                          resolution: rel.resolution,
                          aspectRatio: 0.5625,
                          onTap: () {
                            Navigator.of(context).pop();
                            context.push('/wallpaper/${rel.id}');
                          },
                        ),
                      );
                    },
                  ),
                ),
                const SizedBox(height: 24),
              ],

              // Report button
              Center(
                child: TextButton.icon(
                  onPressed: () => _showReportDialog(context),
                  icon: const Icon(Icons.flag_outlined, size: 16, color: AppColors.textTertiary),
                  label: const Text('Report Wallpaper', style: TextStyle(color: AppColors.textTertiary, fontSize: 13)),
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSpecItem({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Expanded(
      child: Row(
        children: [
          Icon(icon, size: 20, color: AppColors.primary),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: const TextStyle(fontSize: 11, color: AppColors.textTertiary)),
              Text(
                value,
                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMetricItem(IconData icon, String value, String label) {
    return Column(
      children: [
        Icon(icon, size: 20, color: AppColors.textSecondary),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
        Text(label, style: const TextStyle(fontSize: 11, color: AppColors.textTertiary)),
      ],
    );
  }

  Widget _buildColorChip(BuildContext context, String hex, {bool isDominant = false}) {
    Color? swatchColor;
    try {
      final cleanHex = hex.replaceAll('#', '');
      swatchColor = Color(int.parse('0xFF$cleanHex'));
    } catch (_) {
      swatchColor = Colors.grey;
    }

    return InkWell(
      onTap: () {
        Navigator.of(context).pop();
        context.push('/search?color=${hex.replaceAll("#", "")}');
      },
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: AppColors.surfaceElevated,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isDominant ? AppColors.primary : Colors.white24,
            width: isDominant ? 1.5 : 1.0,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 14,
              height: 14,
              decoration: BoxDecoration(
                color: swatchColor,
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white30, width: 0.8),
              ),
            ),
            const SizedBox(width: 6),
            Text(
              hex.toUpperCase(),
              style: TextStyle(
                fontSize: 11,
                fontFamily: 'monospace',
                fontWeight: isDominant ? FontWeight.bold : FontWeight.normal,
                color: isDominant ? AppColors.primary : AppColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
