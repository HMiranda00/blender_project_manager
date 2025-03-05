import bpy
import threading
from datetime import datetime
from .notification_types import NotificationType
from .integrations.slack import SlackWebhookIntegration
from .integrations.discord import DiscordWebhookIntegration

class NotificationManager:
    """Manages notifications for external services"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NotificationManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.slack_integration = SlackWebhookIntegration()
        self.discord_integration = DiscordWebhookIntegration()
        
        self.username = ""
        self.project_name = ""
        
        # Load settings from preferences if available
        self._load_settings_from_preferences()
        
        self._initialized = True
    
    def _load_settings_from_preferences(self):
        """Loads settings from addon preferences"""
        addon_prefs = None
        try:
            addon_prefs = bpy.context.preferences.addons["blender_project_manager"].preferences
            
            if hasattr(addon_prefs, "slack_webhook_url"):
                self.slack_integration.set_webhook_url(addon_prefs.slack_webhook_url)
                
            if hasattr(addon_prefs, "discord_webhook_url"):
                self.discord_integration.set_webhook_url(addon_prefs.discord_webhook_url)
                
            if hasattr(addon_prefs, "username"):
                self.username = addon_prefs.username
                
            if hasattr(addon_prefs, "current_project"):
                self.project_name = addon_prefs.current_project
        except:
            pass
    
    def reload_settings(self):
        """Reloads settings from preferences"""
        self._load_settings_from_preferences()
        
    def notify_file_opened(self, file_path):
        """Sends notification when a file is opened"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"File opened ({timestamp})"
        
        self._send_notification_async(
            NotificationType.FILE_OPENED, 
            message, 
            file_path=file_path,
            user=self.username
        )
    
    def notify_file_saved(self, file_path):
        """Sends notification when a file is saved"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"File saved ({timestamp})"
        
        self._send_notification_async(
            NotificationType.FILE_SAVED, 
            message, 
            file_path=file_path,
            user=self.username
        )
    
    def notify_file_locked(self, file_path):
        """Sends notification when a file is locked"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"File locked ({timestamp})"
        
        self._send_notification_async(
            NotificationType.FILE_LOCKED, 
            message, 
            file_path=file_path,
            user=self.username
        )
    
    def notify_file_unlocked(self, file_path):
        """Sends notification when a file is unlocked"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"File unlocked ({timestamp})"
        
        self._send_notification_async(
            NotificationType.FILE_UNLOCKED, 
            message, 
            file_path=file_path,
            user=self.username
        )
        
    def notify_note_added(self, file_path, note):
        """Sends notification when a note is added"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"Note added ({timestamp})"
        
        self._send_notification_async(
            NotificationType.NOTE_ADDED, 
            message, 
            file_path=file_path,
            user=self.username,
            note=note
        )
        
    def notify_project_created(self, project_name):
        """Sends notification when a project is created"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"Project created: {project_name} ({timestamp})"
        
        self._send_notification_async(
            NotificationType.PROJECT_CREATED, 
            message, 
            user=self.username
        )
        
    def _send_notification_async(self, notification_type, message, file_path="", user="", note=""):
        """Sends notifications in a separate thread to avoid blocking the UI"""
        
        def send_task():
            # Try to send to Discord
            if self.discord_integration.enabled:
                self.discord_integration.send_notification(
                    notification_type, message, file_path, user, note
                )
                
            # Try to send to Slack
            if self.slack_integration.enabled:
                self.slack_integration.send_notification(
                    notification_type, message, file_path, user, note
                )
                
        # Start thread to send notifications
        thread = threading.Thread(target=send_task)
        thread.daemon = True
        thread.start() 