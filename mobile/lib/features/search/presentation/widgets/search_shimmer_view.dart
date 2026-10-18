import 'package:flutter/material.dart';
import '../../../../shared/widgets/shimmer_placeholder.dart';

class SearchShimmerView extends StatelessWidget {
  const SearchShimmerView({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Filter row shimmer
          Row(
            children: [
              ShimmerPlaceholder(width: 80, height: 28, borderRadius: BorderRadius.circular(14)),
              const SizedBox(width: 8),
              ShimmerPlaceholder(width: 100, height: 28, borderRadius: BorderRadius.circular(14)),
            ],
          ),
          const SizedBox(height: 16),

          // 2-Column Grid Shimmer
          Expanded(
            child: GridView.builder(
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: 0.5625,
              ),
              itemCount: 6,
              itemBuilder: (context, index) {
                return ShimmerPlaceholder(
                  width: double.infinity,
                  height: double.infinity,
                  borderRadius: BorderRadius.circular(16),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
