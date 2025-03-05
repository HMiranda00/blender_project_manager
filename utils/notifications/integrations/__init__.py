import re
import json
import urllib.request
import urllib.error
import os

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