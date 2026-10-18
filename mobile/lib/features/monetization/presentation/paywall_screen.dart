import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../../core/network/api_client.dart';
import '../../../core/storage/secure_storage_service.dart';
import '../../../core/theme/app_colors.dart';
import '../data/monetization_repository.dart';
import '../models/subscription_plan.dart';
import 'bloc/monetization_cubit.dart';
import 'bloc/monetization_state.dart';

class PaywallScreen extends StatelessWidget {
  const PaywallScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider<MonetizationCubit>(
      create: (context) {
        final storage = SecureStorageService();
        final apiClient = ApiClient(storage: storage);
        final repository = MonetizationRepository(apiClient);
        return MonetizationCubit(repository)..loadMonetizationData();
      },
      child: const _PaywallContent(),
    );
  }
}

class _PaywallContent extends StatelessWidget {
  const _PaywallContent();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.darkBackground,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.close, color: Colors.white70),
          onPressed: () => context.pop(),
        ),
        actions: [
          TextButton(
            onPressed: () => context.read<MonetizationCubit>().restorePurchases(),
            child: const Text(
              'Restore',
              style: TextStyle(
                color: Colors.white70,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
      body: BlocConsumer<MonetizationCubit, MonetizationState>(
        listener: (context, state) {
          if (state.successMessage != null) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.successMessage!),
                backgroundColor: AppColors.success,
                behavior: SnackBarBehavior.floating,
              ),
            );
            context.pop();
          } else if (state.errorMessage != null) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.errorMessage!),
                backgroundColor: AppColors.error,
                behavior: SnackBarBehavior.floating,
              ),
            );
          }
        },
        builder: (context, state) {
          if (state.isLoading) {
            return const Center(
              child: CircularProgressIndicator(color: AppColors.primary),
            );
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Glowing Pro Badge
                Container(
                  width: 64,
                  height: 64,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: const LinearGradient(
                      colors: [AppColors.primary, AppColors.accent],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.primary.withOpacity(0.4),
                        blurRadius: 20,
                        spreadRadius: 2,
                      ),
                    ],
                  ),
                  child: const Icon(Icons.workspace_premium, color: Colors.white, size: 36),
                ),
                const SizedBox(height: 16),

                // Title
                const Text(
                  'Unlock W8K Pro',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 26,
                    fontWeight: FontWeight.w800,
                    letterSpacing: -0.5,
                  ),
                ),
                const SizedBox(height: 6),
                const Text(
                  'Experience true 8K Ultra-HD with zero ads and unlimited downloads.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: AppColors.textDarkSecondary,
                    fontSize: 14,
                    height: 1.4,
                  ),
                ),
                const SizedBox(height: 24),

                // Pro Features List
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: AppColors.darkSurface,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: AppColors.darkBorder),
                  ),
                  child: Column(
                    children: const [
                      _FeatureRow(
                        icon: Icons.high_quality,
                        title: '8K UHD Master Quality',
                        subtitle: 'Full 7680x4320 uncompressed native downloads',
                      ),
                      Divider(color: AppColors.darkBorder, height: 24),
                      _FeatureRow(
                        icon: Icons.block,
                        title: '100% Ad-Free',
                        subtitle: 'No video ads, banner ads, or download interruptions',
                      ),
                      Divider(color: AppColors.darkBorder, height: 24),
                      _FeatureRow(
                        icon: Icons.bolt,
                        title: 'Lightning CDN Speed',
                        subtitle: 'Zero bandwidth caps with high-priority edge servers',
                      ),
                      Divider(color: AppColors.darkBorder, height: 24),
                      _FeatureRow(
                        icon: Icons.auto_awesome,
                        title: 'Daily VIP Wallpapers',
                        subtitle: 'Exclusive curation for Pro members every morning',
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Subscription Plan Cards
                if (state.plans.isNotEmpty) ...[
                  ...state.plans.map(
                    (plan) => _PlanCard(
                      plan: plan,
                      isSelected: state.selectedPlan?.id == plan.id,
                      onTap: () => context.read<MonetizationCubit>().selectPlan(plan),
                    ),
                  ),
                ],
                const SizedBox(height: 24),

                // Unlock Button
                SizedBox(
                  width: double.infinity,
                  height: 54,
                  child: ElevatedButton(
                    onPressed: state.purchaseStatus == MonetizationActionStatus.loading
                        ? null
                        : () => context.read<MonetizationCubit>().purchaseSelectedPlan(),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      foregroundColor: Colors.white,
                      elevation: 8,
                      shadowColor: AppColors.primary.withOpacity(0.5),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                      ),
                    ),
                    child: state.purchaseStatus == MonetizationActionStatus.loading
                        ? const SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                          )
                        : Text(
                            state.selectedPlan != null
                                ? 'Unlock for \$${state.selectedPlan!.priceAmount.toStringAsFixed(2)} / ${state.selectedPlan!.billingPeriod}'
                                : 'Unlock 8K Pro',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                  ),
                ),
                const SizedBox(height: 16),

                // Footnote
                const Text(
                  'Auto-renews until cancelled. Cancel anytime in Google Play Store settings.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: AppColors.textDarkMuted,
                    fontSize: 11,
                    height: 1.3,
                  ),
                ),
                const SizedBox(height: 24),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _FeatureRow extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;

  const _FeatureRow({
    required this.icon,
    required this.title,
    required this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: AppColors.primaryDark.withOpacity(0.3),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(icon, color: AppColors.primaryLight, size: 22),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                subtitle,
                style: const TextStyle(
                  color: AppColors.textDarkSecondary,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _PlanCard extends StatelessWidget {
  final SubscriptionPlanItem plan;
  final bool isSelected;
  final VoidCallback onTap;

  const _PlanCard({
    required this.plan,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.darkSurfaceElevated : AppColors.darkSurface,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color: isSelected ? AppColors.primary : AppColors.darkBorder,
            width: isSelected ? 2 : 1,
          ),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: AppColors.primary.withOpacity(0.2),
                    blurRadius: 12,
                    spreadRadius: 1,
                  ),
                ]
              : null,
        ),
        child: Row(
          children: [
            // Radio circle
            Container(
              width: 20,
              height: 20,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: isSelected ? AppColors.primary : AppColors.textDarkMuted,
                  width: 2,
                ),
                color: isSelected ? AppColors.primary : Colors.transparent,
              ),
              child: isSelected
                  ? const Icon(Icons.check, size: 14, color: Colors.white)
                  : null,
            ),
            const SizedBox(width: 14),

            // Plan details
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        plan.name,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      if (plan.discountLabel != null) ...[
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppColors.accent.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(color: AppColors.accent.withOpacity(0.5)),
                          ),
                          child: Text(
                            plan.discountLabel!,
                            style: const TextStyle(
                              color: AppColors.accent,
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    plan.description,
                    style: const TextStyle(
                      color: AppColors.textDarkSecondary,
                      fontSize: 11,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),

            // Price
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '\$${plan.priceAmount.toStringAsFixed(2)}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                Text(
                  '/${plan.billingPeriod}',
                  style: const TextStyle(
                    color: AppColors.textDarkMuted,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
