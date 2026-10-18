import 'package:equatable/equatable.dart';
import '../../models/subscription_plan.dart';

enum MonetizationActionStatus { initial, loading, success, failure }

class MonetizationState extends Equatable {
  final bool isLoading;
  final String? errorMessage;
  final String? successMessage;
  final List<SubscriptionPlanItem> plans;
  final UserSubscriptionStatus? userStatus;
  final SubscriptionPlanItem? selectedPlan;
  final MonetizationActionStatus purchaseStatus;

  const MonetizationState({
    this.isLoading = false,
    this.errorMessage,
    this.successMessage,
    this.plans = const [],
    this.userStatus,
    this.selectedPlan,
    this.purchaseStatus = MonetizationActionStatus.initial,
  });

  MonetizationState copyWith({
    bool? isLoading,
    String? errorMessage,
    String? successMessage,
    List<SubscriptionPlanItem>? plans,
    UserSubscriptionStatus? userStatus,
    SubscriptionPlanItem? selectedPlan,
    MonetizationActionStatus? purchaseStatus,
  }) {
    return MonetizationState(
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
      successMessage: successMessage,
      plans: plans ?? this.plans,
      userStatus: userStatus ?? this.userStatus,
      selectedPlan: selectedPlan ?? this.selectedPlan,
      purchaseStatus: purchaseStatus ?? this.purchaseStatus,
    );
  }

  @override
  List<Object?> get props => [
        isLoading,
        errorMessage,
        successMessage,
        plans,
        userStatus,
        selectedPlan,
        purchaseStatus,
      ];
}
