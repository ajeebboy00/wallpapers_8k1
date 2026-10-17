import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class DeliveryReport:
    success: bool
    sent_count: int
    failure_count: int
    message: str
    delivery_mode: str  # "fcm_live" | "fcm_mock_fallback"
    details: Optional[List[Dict[str, Any]]] = None

class FCMService:
    def __init__(self):
        self._firebase_app = None
        self._is_live = False
        self._initialize_firebase()

    def _initialize_firebase(self):
        if settings.FCM_SERVICE_ACCOUNT_JSON:
            try:
                import firebase_admin
                from firebase_admin import credentials

                if not firebase_admin._apps:
                    if settings.FCM_SERVICE_ACCOUNT_JSON.startswith("{"):
                        cred_dict = json.loads(settings.FCM_SERVICE_ACCOUNT_JSON)
                        cred = credentials.Certificate(cred_dict)
                    else:
                        cred = credentials.Certificate(settings.FCM_SERVICE_ACCOUNT_JSON)
                    self._firebase_app = firebase_admin.initialize_app(cred)
                else:
                    self._firebase_app = firebase_admin.get_app()
                self._is_live = True
                logger.info("Firebase Admin SDK successfully initialized for live push messaging.")
            except Exception as e:
                logger.warning(f"Could not initialize live Firebase Admin SDK: {e}. Defaulting to structured fallback mode.")
                self._is_live = False
        else:
            logger.debug("FCM_SERVICE_ACCOUNT_JSON not set. FCMService operating in structured fallback mode.")
            self._is_live = False

    async def send_multicast(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        image_url: Optional[str] = None
    ) -> DeliveryReport:
        """Sends push notification to multiple FCM registration tokens."""
        if not tokens:
            return DeliveryReport(
                success=True,
                sent_count=0,
                failure_count=0,
                message="No target tokens provided",
                delivery_mode="fcm_live" if self._is_live else "fcm_mock_fallback"
            )

        # Standardize data payload strings
        payload_data = {str(k): str(v) for k, v in (data or {}).items()}

        if self._is_live:
            try:
                from firebase_admin import messaging

                notification = messaging.Notification(
                    title=title,
                    body=body,
                    image=image_url
                )
                message = messaging.MulticastMessage(
                    tokens=tokens,
                    notification=notification,
                    data=payload_data,
                    android=messaging.AndroidConfig(
                        priority="high",
                        notification=messaging.AndroidNotification(
                            icon="ic_notification",
                            color="#9333EA",
                            sound="default"
                        )
                    )
                )
                response = messaging.send_each_for_multicast(message)
                return DeliveryReport(
                    success=response.success_count > 0 or response.failure_count == 0,
                    sent_count=response.success_count,
                    failure_count=response.failure_count,
                    message=f"Dispatched {response.success_count}/{len(tokens)} push messages",
                    delivery_mode="fcm_live"
                )
            except Exception as e:
                logger.error(f"Error executing live FCM multicast delivery: {e}")
                return DeliveryReport(
                    success=False,
                    sent_count=0,
                    failure_count=len(tokens),
                    message=f"Live FCM dispatch failed: {str(e)}",
                    delivery_mode="fcm_live"
                )

        # Structured Fallback Mode (Production-grade simulation logging)
        logger.info(
            f"[FCM Mock Dispatch] Target count={len(tokens)} | Title='{title}' | "
            f"Body='{body}' | Image='{image_url}' | Data keys={list(payload_data.keys())}"
        )
        return DeliveryReport(
            success=True,
            sent_count=len(tokens),
            failure_count=0,
            message=f"Simulated push delivery to {len(tokens)} devices successfully",
            delivery_mode="fcm_mock_fallback"
        )

    async def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        image_url: Optional[str] = None
    ) -> DeliveryReport:
        """Sends push notification to a specific subscribed topic."""
        payload_data = {str(k): str(v) for k, v in (data or {}).items()}

        if self._is_live:
            try:
                from firebase_admin import messaging

                notification = messaging.Notification(
                    title=title,
                    body=body,
                    image=image_url
                )
                message = messaging.Message(
                    topic=topic,
                    notification=notification,
                    data=payload_data,
                    android=messaging.AndroidConfig(
                        priority="high",
                        notification=messaging.AndroidNotification(
                            icon="ic_notification",
                            color="#9333EA",
                            sound="default"
                        )
                    )
                )
                msg_id = messaging.send(message)
                return DeliveryReport(
                    success=True,
                    sent_count=1,
                    failure_count=0,
                    message=f"Dispatched to topic '{topic}', message_id={msg_id}",
                    delivery_mode="fcm_live"
                )
            except Exception as e:
                logger.error(f"Error executing live FCM topic delivery: {e}")
                return DeliveryReport(
                    success=False,
                    sent_count=0,
                    failure_count=1,
                    message=f"Live FCM topic dispatch failed: {str(e)}",
                    delivery_mode="fcm_live"
                )

        # Fallback mode
        logger.info(
            f"[FCM Topic Dispatch] Topic='{topic}' | Title='{title}' | "
            f"Body='{body}' | Data={payload_data}"
        )
        return DeliveryReport(
            success=True,
            sent_count=1,
            failure_count=0,
            message=f"Simulated topic push delivery to topic '{topic}' successfully",
            delivery_mode="fcm_mock_fallback"
        )

fcm_service = FCMService()
