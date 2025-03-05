import json
import urllib.request
import urllib.error
import os
import socket
from ..notification_types import NotificationType
from . import WebhookIntegration

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