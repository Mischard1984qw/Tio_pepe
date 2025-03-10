"""Notification system for handling email and push notifications."""

from typing import Dict, Any, List, Optional
from enum import Enum
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
from datetime import datetime
from config.config import get_config
import requests

class NotificationType(Enum):
    """Types of notifications supported by the system."""
    EMAIL = 'email'
    PUSH = 'push'
    SMS = 'sms'

@dataclass
class NotificationTemplate:
    """Template for notification messages."""
    subject: str
    body: str
    type: NotificationType

@dataclass
class NotificationPreference:
    """User preferences for notifications."""
    user_id: str
    email: Optional[str] = None
    push_token: Optional[str] = None
    phone_number: Optional[str] = None
    push_enabled: bool = False
    email_enabled: bool = True
    sms_enabled: bool = False
    notification_types: List[NotificationType] = None

class NotificationManager:
    """Manages notification delivery and user preferences."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = get_config().get('notifications', {})
        self.preferences: Dict[str, NotificationPreference] = {}
        self.templates: Dict[str, NotificationTemplate] = self._load_default_templates()
        self.offline_queue: List[Dict[str, Any]] = []

    def _load_default_templates(self) -> Dict[str, NotificationTemplate]:
        """Load default notification templates."""
        return {
            'task_completed': NotificationTemplate(
                subject='Task Completed: {task_id}',
                body='Your task {task_id} has been completed successfully at {timestamp}.',
                type=NotificationType.EMAIL
            ),
            'task_failed': NotificationTemplate(
                subject='Task Failed: {task_id}',
                body='Your task {task_id} has failed. Error: {error_message}',
                type=NotificationType.EMAIL
            ),
            'system_alert': NotificationTemplate(
                subject='System Alert',
                body='{message}',
                type=NotificationType.PUSH
            )
        }

    def set_user_preferences(self, preference: NotificationPreference) -> None:
        """Set notification preferences for a user."""
        self.preferences[preference.user_id] = preference
        self.logger.info(f"Updated notification preferences for user {preference.user_id}")

    def send_email_notification(self, to_email: str, subject: str, body: str) -> bool:
        """Send an email notification."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.get('email_from', 'noreply@tiopepe.com')
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            smtp_config = self.config.get('smtp', {})
            with smtplib.SMTP(smtp_config.get('host', 'localhost'), smtp_config.get('port', 587)) as server:
                if smtp_config.get('use_tls', True):
                    server.starttls()
                if 'username' in smtp_config and 'password' in smtp_config:
                    server.login(smtp_config['username'], smtp_config['password'])
                server.send_message(msg)

            self.logger.info(f"Email notification sent to {to_email}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email notification: {str(e)}")
            if not self.is_connected():
                self._queue_notification('email', {'to': to_email, 'subject': subject, 'body': body})
            return False

    def send_push_notification(self, user_id: str, title: str, message: str) -> bool:
        """Send a push notification using FCM or similar service."""
        try:
            user_prefs = self.preferences.get(user_id)
            if not user_prefs or not user_prefs.push_token:
                return False

            push_config = self.config.get('push', {})
            response = requests.post(
                push_config.get('fcm_url', 'https://fcm.googleapis.com/fcm/send'),
                headers={
                    'Authorization': f"key={push_config.get('api_key')}",
                    'Content-Type': 'application/json'
                },
                json={
                    'to': user_prefs.push_token,
                    'notification': {
                        'title': title,
                        'body': message
                    }
                }
            )
            response.raise_for_status()
            self.logger.info(f"Push notification sent to user {user_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send push notification: {str(e)}")
            if not self.is_connected():
                self._queue_notification('push', {'user_id': user_id, 'title': title, 'message': message})
            return False

    def is_connected(self) -> bool:
        """Check if the system has network connectivity."""
        try:
            requests.get('https://www.google.com', timeout=3)
            return True
        except requests.RequestException:
            return False

    def _queue_notification(self, notification_type: str, data: Dict[str, Any]) -> None:
        """Queue a notification for later delivery when offline."""
        self.offline_queue.append({
            'type': notification_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
        self.logger.info(f"Queued {notification_type} notification for later delivery")

    def process_offline_queue(self) -> None:
        """Process queued notifications when back online."""
        if not self.is_connected():
            return

        queued_notifications = self.offline_queue.copy()
        self.offline_queue.clear()

        for notification in queued_notifications:
            try:
                if notification['type'] == 'email':
                    self.send_email_notification(
                        notification['data']['to'],
                        notification['data']['subject'],
                        notification['data']['body']
                    )
                elif notification['type'] == 'push':
                    self.send_push_notification(
                        notification['data']['user_id'],
                        notification['data']['title'],
                        notification['data']['message']
                    )
            except Exception as e:
                self.logger.error(f"Failed to process queued notification: {str(e)}")
                self.offline_queue.append(notification)

    def notify_task_completion(self, task_id: str, user_id: str, success: bool = True,
                             error_message: str = None) -> None:
        """Notify user about task completion status."""
        if user_id not in self.preferences:
            self.logger.warning(f"No notification preferences found for user {user_id}")
            return

        pref = self.preferences[user_id]
        template_key = 'task_completed' if success else 'task_failed'
        template = self.templates[template_key]

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        context = {
            'task_id': task_id,
            'timestamp': timestamp,
            'error_message': error_message
        }

        if pref.email and NotificationType.EMAIL in pref.notification_types:
            subject = template.subject.format(**context)
            body = template.body.format(**context)
            self.send_email_notification(pref.email, subject, body)

        if pref.push_enabled and NotificationType.PUSH in pref.notification_types:
            title = f"Task {task_id} {'Completed' if success else 'Failed'}"
            message = template.body.format(**context)
            self.send_push_notification(user_id, title, message)