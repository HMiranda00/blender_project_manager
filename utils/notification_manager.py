import bpy
import json
import urllib.request
import urllib.error
import threading
import os
import time
from datetime import datetime
from enum import Enum

class NotificationType(Enum):
    FILE_OPENED = 0
    FILE_SAVED = 1
    FILE_LOCKED = 2
    FILE_UNLOCKED = 3
    NOTE_ADDED = 4
    PROJECT_CREATED = 5
    
class WebhookIntegration:
    """Base class for webhook integrations"""
    
    def __init__(self, url=""):
        self.webhook_url = url
        self.enabled = bool(url) and self._validate_webhook_url(url)
        print(f"Inicializando webhook: {'Ativado' if self.enabled else 'Desativado'}")
        if url:
            print(f"URL parcial: {url[:20]}..." if len(url) > 20 else url)
        
    def set_webhook_url(self, url):
        self.webhook_url = url
        self.enabled = bool(url) and self._validate_webhook_url(url)
        print(f"Configurando webhook: {'Ativado' if self.enabled else 'Desativado'}")
        if url:
            print(f"URL parcial: {url[:20]}..." if len(url) > 20 else url)
        
    def _validate_webhook_url(self, url):
        """Validate if a URL looks like a webhook URL"""
        if not url:
            return False
            
        # Verify if URL starts with https://
        if not url.startswith("https://"):
            print(f"WARNING: Webhook URL doesn't start with https://")
            return False
            
        # Specific checks for Discord
        if "discord" in url.lower():
            if not ("discord.com/api/webhooks/" in url.lower() or "discordapp.com/api/webhooks/" in url.lower()):
                print(f"WARNING: Discord URL doesn't appear to be valid. Should contain 'discord.com/api/webhooks/'")
                return False
                
            # Extract ID and token to verify format
            discord_id, discord_token = self._extract_discord_id_token(url)
            if not discord_id or not discord_token:
                print(f"WARNING: Discord URL has invalid format. Couldn't extract ID and token.")
                return False
                
        # Specific checks for Slack
        if "slack" in url.lower():
            if not "hooks.slack.com" in url.lower():
                print(f"WARNING: Slack URL doesn't appear to be valid. Should contain 'hooks.slack.com'")
                return False
                
        return True
        
    def _extract_discord_id_token(self, url):
        """Extracts ID and token from a Discord webhook"""
        try:
            # Possible formats:
            # https://discord.com/api/webhooks/ID/TOKEN
            # https://discordapp.com/api/webhooks/ID/TOKEN
            
            import re
            pattern = r'discord(?:app)?\.com/api/webhooks/(\d+)/([a-zA-Z0-9_-]+)'
            match = re.search(pattern, url)
            
            if match:
                discord_id = match.group(1)
                discord_token = match.group(2)
                
                # Verify if ID seems valid (only digits)
                if not discord_id.isdigit():
                    print(f"WARNING: Discord webhook ID ({discord_id}) doesn't appear valid")
                    return None, None
                    
                # Verify if token seems valid (minimum length)
                if len(discord_token) < 50:
                    print(f"WARNING: Discord webhook token too short, might be truncated")
                
                print(f"Webhook ID: {discord_id}")
                print(f"Webhook token detected (length: {len(discord_token)})")
                
                return discord_id, discord_token
            else:
                print(f"WARNING: Couldn't extract ID and token from Discord URL")
                return None, None
                
        except Exception as e:
            print(f"Error extracting ID and token: {str(e)}")
            return None, None
        
    def send_notification(self, notification_type, message, file_path="", user="", note=""):
        """Method to be implemented by subclasses"""
        pass

class SlackWebhookIntegration(WebhookIntegration):
    """Slack integration using webhooks"""
    
    def send_notification(self, notification_type, message, file_path="", user="", note=""):
        if not self.enabled:
            return False
            
        emoji = self._get_emoji_for_type(notification_type)
        compact_message = f"{emoji} *{message}*"
        
        if file_path:
            compact_message += f"\n• *File:* `{os.path.basename(file_path)}`"
        if user:
            compact_message += f"\n• *User:* {user}"
        if note and notification_type == NotificationType.NOTE_ADDED:
            compact_message += f"\n• *Note:* _{note}_"
            
        payload = {
            "text": compact_message,
            "unfurl_links": False,
            "unfurl_media": False
        }
        
        return self._send_webhook_request(payload)
        
    def _get_emoji_for_type(self, notification_type):
        """Returns the appropriate emoji for each notification type"""
        emoji_map = {
            NotificationType.FILE_OPENED: "🔍",
            NotificationType.FILE_SAVED: "💾",
            NotificationType.FILE_LOCKED: "🔒",
            NotificationType.FILE_UNLOCKED: "🔓",
            NotificationType.NOTE_ADDED: "📝",
            NotificationType.PROJECT_CREATED: "🎬"
        }
        return emoji_map.get(notification_type, "🔔")
        
    def _send_webhook_request(self, payload):
        """Sends request to the Slack webhook"""
        try:
            # Log payload details before sending
            print(f"\n--- SLACK WEBHOOK DEBUG ---")
            print(f"URL (first 20 characters): {self.webhook_url[:20]}...")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            data = json.dumps(payload).encode('utf-8')
            headers = {'Content-Type': 'application/json'}
            print(f"Headers: {headers}")
            
            req = urllib.request.Request(self.webhook_url, data=data, headers=headers)
            
            # Try to make the request and capture the complete response
            try:
                response = urllib.request.urlopen(req)
                response_code = response.getcode()
                response_content = response.read().decode('utf-8')
                print(f"Response ({response_code}): {response_content}")
                return response_code == 200
                
            except urllib.error.HTTPError as http_error:
                # Capture specific details of HTTP errors
                error_body = http_error.read().decode('utf-8')
                print(f"HTTP Error {http_error.code}: {http_error.reason}")
                print(f"Error details: {error_body}")
                
                # Specific suggestions for 403 error
                if http_error.code == 403:
                    print(f"403 FORBIDDEN ERROR - Possible causes:")
                    print(f"1. Invalid or expired webhook URL")
                    print(f"2. Webhook was deleted in Slack")
                    print(f"3. Incorrect message format")
                    print(f"4. IP blocked by Slack")
                
                return False
                
        except urllib.error.URLError as e:
            print(f"Connection error: {e.reason}")
            return False
        except Exception as e:
            print(f"Unexpected error sending notification to Slack: {str(e)}")
            return False
        finally:
            print("--- END SLACK DEBUG ---\n")

class DiscordWebhookIntegration(WebhookIntegration):
    """Discord integration using webhooks"""
    
    def validate_webhook_with_simple_message(self):
        """Tests the webhook with a super simple message to check for formatting issues"""
        if not self.webhook_url:
            print("Webhook URL not configured")
            return False
            
        # Minimal payload for testing - as simple as possible
        basic_payload = {
            "content": "Test message from Blender Project Manager"
        }
        
        print("\n--- DISCORD WEBHOOK VALIDATION TEST ---")
        print(f"Testing webhook URL (first 30 chars): {self.webhook_url[:30] if len(self.webhook_url) > 30 else self.webhook_url}...")
        
        try:
            # Convert to JSON and send
            data = json.dumps(basic_payload).encode('utf-8')
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Blender Project Manager/1.0',
                'Accept': 'application/json',
                'Connection': 'keep-alive'
            }
            
            print(f"Enhanced headers: {headers}")
            print(f"Payload (raw): {data}")
            
            # Try Direct API first
            discord_id, discord_token = self._extract_discord_id_token(self.webhook_url)
            if discord_id and discord_token:
                print("Attempting direct API call first...")
                api_url = f"https://discord.com/api/v10/webhooks/{discord_id}/{discord_token}"
                
                try:
                    direct_req = urllib.request.Request(api_url, data=data, headers=headers)
                    direct_response = urllib.request.urlopen(direct_req)
                    
                    response_code = direct_response.getcode()
                    print(f"Direct API test successful! Status: {response_code}")
                    return True
                except Exception as direct_e:
                    print(f"Direct API failed, falling back to webhook URL: {str(direct_e)}")
                    # Continue with standard method
            
            req = urllib.request.Request(self.webhook_url, data=data, headers=headers)
            response = urllib.request.urlopen(req)
            
            response_code = response.getcode()
            print(f"Basic test successful! Status: {response_code}")
            return True
            
        except urllib.error.HTTPError as http_error:
            error_body = http_error.read().decode('utf-8')
            print(f"HTTP Error {http_error.code}: {http_error.reason}")
            print(f"URL appears invalid or inaccessible")
            print(f"Complete response: {error_body}")
            print(f"Request headers used: {headers}")
            
            # Advanced error diagnosis
            if "1010" in error_body:
                print("\nDETECTED CLOUDFLARE PROTECTION (ERROR 1010)")
                print("================================================")
                print("This error suggests your request is being blocked by Cloudflare protection.")
                print("Possible solutions:")
                print("1. Check your network connection - try from a different network")
                print("2. Your ISP or proxy might be blocked by Discord")
                print("3. Consider using a different notification method")
                print("================================================")
            
            # Detailed instructions if 403 error
            if http_error.code == 403:
                print("\nDETAILED TROUBLESHOOTING FOR ERROR 403:")
                print("================================================")
                print("1. Verify the webhook in Discord:")
                print("   - Go to server settings > Integrations > Webhooks")
                print("   - Check that your webhook exists and is active")
                print("   - Try the 'Try it' button in Discord's webhook interface")
                print("2. Network issues:")
                print("   - Your network might be blocked or restricted by Discord")
                print("   - Try from a different network if possible")
                print("3. Alternative integrations:")
                print("   - Try using Slack webhook instead")
                print("   - Consider email notifications via SMTP")
                print("================================================")
            
            return False
            
        except Exception as e:
            print(f"Unexpected error testing webhook: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            return False
            
        finally:
            print("--- END WEBHOOK TEST ---\n")
            
    def send_notification(self, notification_type, message, file_path="", user="", note=""):
        if not self.enabled:
            return False
            
        emoji = self._get_emoji_for_type(notification_type)
        compact_message = f"{emoji} **{message}**"
        
        if file_path:
            compact_message += f"\n• **File:** `{os.path.basename(file_path)}`"
        if user:
            compact_message += f"\n• **User:** {user}"
        if note and notification_type == NotificationType.NOTE_ADDED:
            compact_message += f"\n• **Note:** *{note}*"
            
        payload = {
            "content": compact_message,
            "allowed_mentions": {"parse": []}
        }
        
        return self._send_webhook_request(payload)
        
    def _get_emoji_for_type(self, notification_type):
        """Returns the appropriate emoji for each notification type"""
        emoji_map = {
            NotificationType.FILE_OPENED: "🔍",
            NotificationType.FILE_SAVED: "💾",
            NotificationType.FILE_LOCKED: "🔒",
            NotificationType.FILE_UNLOCKED: "🔓",
            NotificationType.NOTE_ADDED: "📝",
            NotificationType.PROJECT_CREATED: "🎬"
        }
        return emoji_map.get(notification_type, "🔔")
        
    def _send_webhook_request(self, payload):
        """Sends request to the Discord webhook"""
        try:
            # Log payload details before sending
            print(f"\n--- DISCORD WEBHOOK DEBUG ---")
            print(f"URL (first 20 characters): {self.webhook_url[:20]}...")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            # Extract ID and token for alternative method, if needed
            discord_id, discord_token = self._extract_discord_id_token(self.webhook_url)
            
            # Enhanced debugging for connectivity
            try:
                import socket
                host = "discord.com"
                port = 443
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                if result == 0:
                    print(f"Connection test to {host}:{port} successful")
                else:
                    print(f"Connection test to {host}:{port} failed with code {result}")
                sock.close()
            except Exception as conn_err:
                print(f"Connection test failed: {str(conn_err)}")
            
            # Try with enhanced headers and direct API first
            if discord_id and discord_token:
                print("Trying direct API call first...")
                
                enhanced_payload = payload.copy()
                if "username" not in enhanced_payload:
                    enhanced_payload["username"] = "Blender Project Manager"
                if "avatar_url" not in enhanced_payload:
                    enhanced_payload["avatar_url"] = "https://www.blender.org/wp-content/uploads/2020/07/blender_logo.png"
                
                api_url = f"https://discord.com/api/v10/webhooks/{discord_id}/{discord_token}"
                
                data = json.dumps(enhanced_payload).encode('utf-8')
                enhanced_headers = {
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Blender Project Manager/1.0',
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Content-Length': str(len(data))
                }
                
                print(f"Enhanced headers: {enhanced_headers}")
                print(f"Using direct API URL: {api_url}")
                
                try:
                    direct_req = urllib.request.Request(api_url, data=data, headers=enhanced_headers, method="POST")
                    direct_response = urllib.request.urlopen(direct_req)
                    
                    response_code = direct_response.getcode()
                    response_content = direct_response.read().decode('utf-8') if response_code != 204 else ""
                    print(f"Direct API success! Status: {response_code}, Response: {response_content}")
                    return True
                except urllib.error.HTTPError as direct_error:
                    direct_error_body = direct_error.read().decode('utf-8')
                    print(f"Direct API HTTP Error {direct_error.code}: {direct_error.reason}")
                    print(f"Direct API error details: {direct_error_body}")
                    # Fall through to standard method
                except Exception as direct_e:
                    print(f"Direct API failed: {str(direct_e)}")
                    # Fall through to standard method
            
            # Try standard method as fallback
            try:
                data = json.dumps(payload).encode('utf-8')
                headers = {
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Blender Project Manager/1.0',
                    'Accept': 'application/json',
                    'Connection': 'keep-alive'
                }
                print(f"Standard fallback - Headers: {headers}")
                
                req = urllib.request.Request(self.webhook_url, data=data, headers=headers)
                
                response = urllib.request.urlopen(req)
                response_code = response.getcode()
                response_content = response.read().decode('utf-8')
                print(f"Response ({response_code}): {response_content}")
                return response_code == 200 or response_code == 204
                
            except urllib.error.HTTPError as http_error:
                # Capture specific details of HTTP errors
                error_body = http_error.read().decode('utf-8')
                print(f"HTTP Error {http_error.code}: {http_error.reason}")
                print(f"Error details: {error_body}")
                
                # Advanced error diagnosis
                if "1010" in error_body:
                    print("\nDETECTED CLOUDFLARE PROTECTION (ERROR 1010)")
                    print("This suggests your request is being blocked by Cloudflare.")
                    print("Try from a different network connection or use a different notification method.")
                
                # Display webhook URL for verification
                if discord_id and discord_token:
                    safe_token = discord_token[:10] + "..." if len(discord_token) > 10 else discord_token
                    print(f"\nVerify this webhook info:")
                    print(f"Server ID: {discord_id}")
                    print(f"Token prefix: {safe_token}")
                    print(f"Full URL structure valid: {'Yes' if self._validate_webhook_url(self.webhook_url) else 'No'}")
                
                return False
                
        except urllib.error.URLError as e:
            print(f"Connection error: {e.reason}")
            
            # Show more network diagnostic info
            print("\nNETWORK DIAGNOSTIC INFO:")
            try:
                import socket
                remote_server = "discord.com"
                print(f"IP address of {remote_server}: {socket.gethostbyname(remote_server)}")
                print(f"Can resolve hostname: Yes")
            except socket.gaierror:
                print(f"Cannot resolve hostname {remote_server}")
            except Exception as sock_e:
                print(f"Network diagnostic error: {str(sock_e)}")
            
            return False
        except Exception as e:
            print(f"Unexpected error sending notification to Discord: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            print("--- END DISCORD DEBUG ---\n")

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
        
# Singleton para acessar de qualquer lugar
notification_manager = NotificationManager() 