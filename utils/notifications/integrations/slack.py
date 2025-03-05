import json
import urllib.request
import urllib.error
import os
from ..notification_types import NotificationType
from . import WebhookIntegration

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