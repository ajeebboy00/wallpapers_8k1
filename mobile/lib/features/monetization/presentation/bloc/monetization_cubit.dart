import 'dart:math';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../data/monetization_repository.dart';
import '../../models/subscription_plan.dart';
import 'monetization_state.dart';

class MonetizationCubit extends Cubit<MonetizationState> {
  final MonetizationRepository repository;

  MonetizationCubit(this.repository) : super(const MonetizationState());

  Future<void> loadMonetizationData() async {
    emit(state.copyWith(isLoading: true, errorMessage: null));
    try {
      final plans = await repository.getPlans();
      UserSubscriptionStatus? status;
      try {
        status = await repository.getSubscriptionStatus();
      } catch (_) {
        // User might not be logged in or free tier
      }

      SubscriptionPlanItem? defaultPlan;
      if (plans.isNotEmpty) {
        // Prefer annual if available, otherwise first
        defaultPlan = plans.firstWhere(
          (p) => p.plan == 'PRO_ANNUAL',
          orElse: () => plans.first,
        );
      }

      emit(state.copyWith(
        isLoading: false,
        plans: plans,
        userStatus: status,
        selectedPlan: defaultPlan,
      ));
    } catch (e) {
      emit(state.copyWith(
        isLoading: false,
        errorMessage: 'Unable to load subscription plans. Please try again.',
      ));
    }
  }

  void selectPlan(SubscriptionPlanItem plan) {
    emit(state.copyWith(selectedPlan: plan));
  }

  Future<void> purchaseSelectedPlan() async {
    final plan = state.selectedPlan;
    if (plan == null) return;

    emit(state.copyWith(
      purchaseStatus: MonetizationActionStatus.loading,
      errorMessage: null,
      successMessage: null,
    ));

    try {
      // In mobile apps with Google Play Billing / App Store In-App Purchases,
      // the native purchase flow yields a purchaseToken upon completion.
      // We verify this token with our backend endpoint.
      final mockToken = 'gplay_token_${DateTime.now().millisecondsSinceEpoch}_${Random().nextInt(999999)}';
      final orderId = 'GPA.${Random().nextInt(9999)}-${Random().nextInt(9999)}-${Random().nextInt(99999)}';

      await repository.verifyPurchase(
        store: 'google_play',
        productId: plan.productId,
        purchaseToken: mockToken,
        plan: plan.plan,
        orderId: orderId,
      );

      // Refresh user status
      final updatedStatus = await repository.getSubscriptionStatus();

      emit(state.copyWith(
        purchaseStatus: MonetizationActionStatus.success,
        successMessage: 'Welcome to W8K Pro VIP! All 8K Ultra-HD wallpapers unlocked.',
        userStatus: updatedStatus,
      ));
    } catch (e) {
      emit(state.copyWith(
        purchaseStatus: MonetizationActionStatus.failure,
        errorMessage: 'Purchase verification failed. Please try again.',
      ));
    }
  }

  Future<void> restorePurchases() async {
    emit(state.copyWith(
      purchaseStatus: MonetizationActionStatus.loading,
      errorMessage: null,
    ));

    try {
      final status = await repository.getSubscriptionStatus();
      if (status.isPro) {
        emit(state.copyWith(
          purchaseStatus: MonetizationActionStatus.success,
          successMessage: 'Previous subscription successfully restored!',
          userStatus: status,
        ));
      } else {
        emit(state.copyWith(
          purchaseStatus: MonetizationActionStatus.failure,
          errorMessage: 'No active subscription found for this account.',
        ));
      }
    } catch (e) {
      emit(state.copyWith(
        purchaseStatus: MonetizationActionStatus.failure,
        errorMessage: 'Unable to restore purchases at this moment.',
      ));
    }
  }

  Future<bool> unlockViaAdReward(String wallpaperId) async {
    try {
      final txId = 'admob_tx_${DateTime.now().millisecondsSinceEpoch}_${Random().nextInt(999999)}';
      final res = await repository.claimAdReward(
        wallpaperId: wallpaperId,
        transactionId: txId,
      );
      return res['unlocked'] == true;
    } catch (_) {
      return false;
    }
  }
}
