from .notification_types import NotificationType
from .manager import NotificationManager

# Singleton para acessar de qualquer lugar
notification_manager = NotificationManager()

__all__ = ['NotificationType', 'notification_manager'] 