import 'package:equatable/equatable.dart';

class SubscriptionPlanItem extends Equatable {
  final String id;
  final String plan;
  final String name;
  final String description;
  final double priceAmount;
  final String currency;
  final String billingPeriod;
  final String? discountLabel;
  final String productId;
  final List<String> features;

  const SubscriptionPlanItem({
    required this.id,
    required this.plan,
    required this.name,
    required this.description,
    required this.priceAmount,
    required this.currency,
    required this.billingPeriod,
    this.discountLabel,
    required this.productId,
    required this.features,
  });

  factory SubscriptionPlanItem.fromJson(Map<String, dynamic> json) {
    return SubscriptionPlanItem(
      id: json['id'] as String? ?? '',
      plan: json['plan'] as String? ?? '',
      name: json['name'] as String? ?? '',
      description: json['description'] as String? ?? '',
      priceAmount: (json['price_amount'] as num?)?.toDouble() ?? 0.0,
      currency: json['currency'] as String? ?? 'USD',
      billingPeriod: json['billing_period'] as String? ?? '',
      discountLabel: json['discount_label'] as String?,
      productId: json['product_id'] as String? ?? '',
      features: (json['features'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          const [],
    );
  }

  @override
  List<Object?> get props => [
        id,
        plan,
        name,
        description,
        priceAmount,
        currency,
        billingPeriod,
        discountLabel,
        productId,
        features,
      ];
}

class UserSubscriptionStatus extends Equatable {
  final bool isPro;
  final String? plan;
  final String? expiresAt;
  final bool autoRenewing;

  const UserSubscriptionStatus({
    required this.isPro,
    this.plan,
    this.expiresAt,
    required this.autoRenewing,
  });

  factory UserSubscriptionStatus.fromJson(Map<String, dynamic> json) {
    return UserSubscriptionStatus(
      isPro: json['is_pro'] as bool? ?? false,
      plan: json['plan'] as String?,
      expiresAt: json['expires_at'] as String?,
      autoRenewing: json['auto_renewing'] as bool? ?? false,
    );
  }

  @override
  List<Object?> get props => [isPro, plan, expiresAt, autoRenewing];
}

class UserEntitlements extends Equatable {
  final bool isPro;
  final bool canDownload8k;
  final bool hasAdUnlock;
  final String? wallpaperId;
  final String? adUnlockExpiresAt;

  const UserEntitlements({
    required this.isPro,
    required this.canDownload8k,
    required this.hasAdUnlock,
    this.wallpaperId,
    this.adUnlockExpiresAt,
  });

  factory UserEntitlements.fromJson(Map<String, dynamic> json) {
    return UserEntitlements(
      isPro: json['is_pro'] as bool? ?? false,
      canDownload8k: json['can_download_8k'] as bool? ?? false,
      hasAdUnlock: json['has_ad_unlock'] as bool? ?? false,
      wallpaperId: json['wallpaper_id'] as String?,
      adUnlockExpiresAt: json['ad_unlock_expires_at'] as String?,
    );
  }

  @override
  List<Object?> get props => [
        isPro,
        canDownload8k,
        hasAdUnlock,
        wallpaperId,
        adUnlockExpiresAt,
      ];
}
