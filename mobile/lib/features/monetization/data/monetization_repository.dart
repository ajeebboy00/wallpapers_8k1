import '../../../core/network/api_client.dart';
import '../models/subscription_plan.dart';

class MonetizationRepository {
  final ApiClient apiClient;

  MonetizationRepository(this.apiClient);

  Future<List<SubscriptionPlanItem>> getPlans() async {
    final response = await apiClient.get('/api/v1/subscriptions/plans');
    final data = response.data['data'] as List<dynamic>? ?? [];
    return data
        .map((e) => SubscriptionPlanItem.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<UserSubscriptionStatus> getSubscriptionStatus() async {
    final response = await apiClient.get('/api/v1/subscriptions/status');
    final data = response.data['data'] as Map<String, dynamic>? ?? {};
    return UserSubscriptionStatus.fromJson(data);
  }

  Future<Map<String, dynamic>> verifyPurchase({
    required String store,
    required String productId,
    required String purchaseToken,
    required String plan,
    String? orderId,
  }) async {
    final response = await apiClient.post(
      '/api/v1/subscriptions/verify',
      data: {
        'store': store,
        'product_id': productId,
        'purchase_token': purchaseToken,
        'plan': plan,
        if (orderId != null) 'order_id': orderId,
      },
    );
    return response.data['data'] as Map<String, dynamic>? ?? {};
  }

  Future<Map<String, dynamic>> cancelSubscription({String? reason}) async {
    final response = await apiClient.post(
      '/api/v1/subscriptions/cancel',
      data: {
        if (reason != null) 'reason': reason,
      },
    );
    return response.data['data'] as Map<String, dynamic>? ?? {};
  }

  Future<Map<String, dynamic>> claimAdReward({
    required String wallpaperId,
    required String transactionId,
    String? deviceId,
    String rewardType = 'wallpaper_download',
    String adNetwork = 'admob',
  }) async {
    final response = await apiClient.post(
      '/api/v1/monetization/ad-reward',
      data: {
        'wallpaper_id': wallpaperId,
        'transaction_id': transactionId,
        if (deviceId != null) 'device_id': deviceId,
        'reward_type': rewardType,
        'ad_network': adNetwork,
      },
    );
    return response.data['data'] as Map<String, dynamic>? ?? {};
  }

  Future<UserEntitlements> checkEntitlements({
    String? wallpaperId,
    String? deviceId,
  }) async {
    final queryParams = <String, dynamic>{};
    if (wallpaperId != null) queryParams['wallpaper_id'] = wallpaperId;
    if (deviceId != null) queryParams['device_id'] = deviceId;

    final response = await apiClient.get(
      '/api/v1/monetization/entitlements',
      queryParameters: queryParams,
    );
    final data = response.data['data'] as Map<String, dynamic>? ?? {};
    return UserEntitlements.fromJson(data);
  }
}
