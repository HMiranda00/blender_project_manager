from enum import Enum

class NotificationType(Enum):
    """Enumeration of notification types supported by the system"""
    FILE_OPENED = 0
    FILE_SAVED = 1
    FILE_LOCKED = 2
    FILE_UNLOCKED = 3
    NOTE_ADDED = 4
    PROJECT_CREATED = 5 