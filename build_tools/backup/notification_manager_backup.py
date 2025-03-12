import bpy
import json
import urllib.request
import urllib.error
import threading
import os
import time
from datetime import datetime
from enum import Enum
from ..preferences import get_addon_preferences
import requests
import re

class NotificationType(Enum):
    FILE_OPENED = 0
    FILE_CLOSED = 1
    PROJECT_CREATED = 2
    SHOT_CREATED = 3
    ASSET_CREATED = 4
    
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
            if not "hooks.slack.com/services/" in url.lower():
                print(f"WARNING: Slack URL doesn't appear to be valid. Should contain 'hooks.slack.com/services/'")
                return False
                
        return True
        
    def _extract_discord_id_token(self, url):
        """Extract Discord webhook ID and token from URL"""
        pattern = r"discord(?:app)?\.com/api/webhooks/(\d+)/([A-Za-z0-9_\-]+)"
            match = re.search(pattern, url)
            
            if match:
                discord_id = match.group(1)
                discord_token = match.group(2)
            return discord_id, discord_token
                
                    return None, None
                    
    def send_notification(self, notification_type, message, **kwargs):
        """Send a notification through the webhook"""
        raise NotImplementedError("Subclasses must implement this method")
        
    def _is_enabled(self):
        """Check if the webhook is enabled and valid"""
        return self.enabled and bool(self.webhook_url)
        
    def test_webhook(self):
        """Send a test message to the webhook"""
        if not self._is_enabled():
            return False, "Webhook is not enabled or URL is invalid"
            
        try:
            timestamp = datetime.now().strftime("%H:%M")
            message = f"Teste de webhook enviado em {timestamp}"
            
            return self.send_notification(None, message, user="Test User")
        except Exception as e:
            return False, f"Error sending test message: {str(e)}"

class SlackWebhookIntegration(WebhookIntegration):
    """Integration with Slack webhooks"""
    
    def send_notification(self, notification_type, message, **kwargs):
        """Send a notification to Slack"""
        if not self._is_enabled():
            return False, "Slack webhook is not enabled"
            
        try:
            # Extract additional info from kwargs
            user = kwargs.get('user', 'Unknown')
            project_name = kwargs.get('project_name', 'Unknown Project')
            file_path = kwargs.get('file_path', '')
            timestamp = datetime.now().strftime("%Hh%M")
            
        payload = {
                "blocks": []
            }
            
            # Título com ícone baseado no tipo de notificação
            header_text = "💻 **" + project_name + "**"
            icon = "🔄"  # Ícone padrão
            
            # Determinar o ícone e título baseado no tipo de notificação
            if notification_type == NotificationType.PROJECT_CREATED:
                icon = "🆕"
                header_text = f"{icon} **New project created**"
            elif notification_type == NotificationType.FILE_OPENED:
                icon = "🔴"
                divider_text = f"------------------------------------------------------\n{icon} **File in use** | 🙅 `{user}` | `{timestamp}`\n------------------------------------------------------"
                if file_path:
                    file_name = os.path.basename(file_path)
                    file_text = f"> **File ** *`{file_name}`*"
                    
                    # Adicionar blocos
                    payload["blocks"].append({
                        "type": "section", 
                        "text": {"type": "mrkdwn", "text": header_text}
                    })
                    payload["blocks"].append({
                        "type": "section", 
                        "text": {"type": "mrkdwn", "text": divider_text}
                    })
                    payload["blocks"].append({
                        "type": "section", 
                        "text": {"type": "mrkdwn", "text": file_text}
                    })
            elif notification_type == NotificationType.FILE_CLOSED:
                icon = "🟢"
                divider_text = f"------------------------------------------------------\n{icon} **File Available** | 🙋 `{user}` | `{timestamp}`\n------------------------------------------------------"
                if file_path:
                    file_name = os.path.basename(file_path)
                    file_text = f"> **File ** *`{file_name}`*"
                    
                    # Adicionar blocos
                    payload["blocks"].append({
                        "type": "section", 
                        "text": {"type": "mrkdwn", "text": header_text}
                    })
                    payload["blocks"].append({
                        "type": "section", 
                        "text": {"type": "mrkdwn", "text": divider_text}
                    })
                    payload["blocks"].append({
                        "type": "section", 
                        "text": {"type": "mrkdwn", "text": file_text}
                    })
            elif notification_type == NotificationType.SHOT_CREATED:
                icon = "📂"
                shot_name = kwargs.get('shot_name', 'Unknown')
                role_name = kwargs.get('role_name', 'Unknown')
                
                divider_text = f"------------------------------------------------------\n{icon} **New Shot Created** | 🙋 `{user}` | `{timestamp}`\n------------------------------------------------------"
                shot_text = f"> **SHOT** {shot_name} | 🎬 {role_name}"
                
                if file_path:
                    file_name = os.path.basename(file_path)
                    file_text = f"> **File ** *`{file_name}`*"
                    
                    # Adicionar blocos
                    payload["blocks"].append({
                        "type": "section", 
                        "text": {"type": "mrkdwn", "text": header_text}
                    })
                    payload["blocks"].append({
                        "type": "section", 
                        "text": {"type": "mrkdwn", "text": divider_text}
                    })
                    payload["blocks"].append({
                        "type": "section", 
                        "text": {"type": "mrkdwn", "text": shot_text}
                    })
                    payload["blocks"].append({
                        "type": "section", 
                        "text": {"type": "mrkdwn", "text": file_text}
                    })
            elif notification_type == NotificationType.ASSET_CREATED:
                icon = "🧩"
                asset_name = kwargs.get('asset_name', 'Unknown')
                asset_type = kwargs.get('asset_type', 'Unknown')
                
                divider_text = f"------------------------------------------------------\n{icon} **New Asset Created** | 🙋 `{user}` | `{timestamp}`\n------------------------------------------------------"
                asset_text = f"> **ASSET** {asset_name} | 🏷️ {asset_type}"
                
                if file_path:
                    file_name = os.path.basename(file_path)
                    file_text = f"> **File ** *`{file_name}`*"
                    
                    # Adicionar blocos
                    payload["blocks"].append({
                        "type": "section", 
                        "text": {"type": "mrkdwn", "text": header_text}
                    })
                    payload["blocks"].append({
                        "type": "section", 
                        "text": {"type": "mrkdwn", "text": divider_text}
                    })
                    payload["blocks"].append({
                        "type": "section", 
                        "text": {"type": "mrkdwn", "text": asset_text}
                    })
                    payload["blocks"].append({
                        "type": "section", 
                        "text": {"type": "mrkdwn", "text": file_text}
                    })
            elif notification_type == NotificationType.PROJECT_CREATED:
                project_text = f"> **Project Name:** {project_name}\n> 🙋 `{user}` | `{timestamp}`"
                
                # Adicionar blocos
                payload["blocks"].append({
                    "type": "section", 
                    "text": {"type": "mrkdwn", "text": header_text}
                })
                payload["blocks"].append({
                    "type": "section", 
                    "text": {"type": "mrkdwn", "text": project_text}
                })
            else:
                # Formato genérico para outros tipos de notificação
                payload["blocks"].append({
                    "type": "section", 
                    "text": {"type": "mrkdwn", "text": header_text}
                })
                payload["blocks"].append({
                    "type": "section", 
                    "text": {"type": "mrkdwn", "text": message}
                })
            
            # Se não há blocos definidos, usar o formato padrão
            if not payload["blocks"]:
                payload["text"] = message
            
            print("--- SLACK DEBUG ---")
            print(f"Sending to Slack: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                self.webhook_url,
                json=payload
            )
            
            response.raise_for_status()
            return True, "Notification sent successfully"
            
        except requests.exceptions.RequestException as e:
            print(f"Error sending to Slack: {str(e)}")
            return False, f"Error sending to Slack: {str(e)}"
        finally:
            print("--- END SLACK DEBUG ---\n")

class DiscordWebhookIntegration(WebhookIntegration):
    """Integration with Discord webhooks"""
    
    def send_notification(self, notification_type, message, **kwargs):
        """Send a notification to Discord"""
        if not self._is_enabled():
            return False, "Discord webhook is not enabled"
            
        try:
            # Extract additional info from kwargs
            user = kwargs.get('user', 'Unknown')
            project_name = kwargs.get('project_name', 'Unknown Project')
            file_path = kwargs.get('file_path', '')
            timestamp = datetime.now().strftime("%Hh%M")
            
            # Conteúdo baseado no tipo de notificação
            content = ""
            embeds = []
            
            if notification_type == NotificationType.PROJECT_CREATED:
                embed = {
                    "title": "🆕 **New project created**",
                    "description": f"**Project Name:** {project_name}\n🙋 `{user}` | `{timestamp}`",
                    "color": 5814783  # Azul claro
                }
                embeds.append(embed)
            elif notification_type == NotificationType.FILE_OPENED:
                if file_path:
                    file_name = os.path.basename(file_path)
                    embed = {
                        "title": f"💻 **{project_name}**",
                        "description": f"------------------------------------------------------\n🔴 **File in use** | 🙅 `{user}` | `{timestamp}`\n------------------------------------------------------\n> **File ** *`{file_name}`*",
                        "color": 16711680  # Vermelho
                    }
                    embeds.append(embed)
            elif notification_type == NotificationType.FILE_CLOSED:
                if file_path:
                    file_name = os.path.basename(file_path)
                    embed = {
                        "title": f"💻 **{project_name}**",
                        "description": f"------------------------------------------------------\n🟢 **File Available** | 🙋 `{user}` | `{timestamp}`\n------------------------------------------------------\n> **File ** *`{file_name}`*",
                        "color": 5763719  # Verde
                    }
                    embeds.append(embed)
            elif notification_type == NotificationType.SHOT_CREATED:
                shot_name = kwargs.get('shot_name', 'Unknown')
                role_name = kwargs.get('role_name', 'Unknown')
                
                if file_path:
                    file_name = os.path.basename(file_path)
                    embed = {
                        "title": f"💻 **{project_name}**",
                        "description": f"------------------------------------------------------\n📂 **New Shot Created** | 🙋 `{user}` | `{timestamp}`\n------------------------------------------------------\n> **SHOT** {shot_name} | 🎬 {role_name}\n> **File ** *`{file_name}`*",
                        "color": 16750848  # Laranja
                    }
                    embeds.append(embed)
            elif notification_type == NotificationType.ASSET_CREATED:
                asset_name = kwargs.get('asset_name', 'Unknown')
                asset_type = kwargs.get('asset_type', 'Unknown')
                
                if file_path:
                    file_name = os.path.basename(file_path)
                    embed = {
                        "title": f"💻 **{project_name}**",
                        "description": f"------------------------------------------------------\n🧩 **New Asset Created** | 🙋 `{user}` | `{timestamp}`\n------------------------------------------------------\n> **ASSET** {asset_name} | 🏷️ {asset_type}\n> **File ** *`{file_name}`*",
                        "color": 10181046  # Roxo
                    }
                    embeds.append(embed)
            else:
                # Formato genérico para qualquer outro tipo
                embed = {
                    "title": f"💻 **{project_name}**",
                    "description": message,
                    "color": 8421504  # Cinza
                }
                embeds.append(embed)
            
            payload = {
                "username": "Blender Project Manager",
                "embeds": embeds
            }
            
            if content:
                payload["content"] = content
                
            print("--- DISCORD DEBUG ---")
            print(f"Sending to Discord: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                self.webhook_url,
                json=payload
            )
            
            response.raise_for_status()
            return True, "Notification sent successfully"
            
        except Exception as e:
            print(f"Unexpected error sending notification to Discord: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False, f"Error sending to Discord: {str(e)}"
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
            addon_prefs = get_addon_preferences()
            
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
        
    def _get_project_name_from_path(self, file_path):
        """Extract project name from file path"""
        if not file_path:
            return self.project_name
            
        try:
            # Tenta extrair o nome do projeto do caminho do arquivo
            parts = os.path.normpath(file_path).split(os.sep)
            
            # Procura por padrões típicos em caminhos de projeto
            for i, part in enumerate(parts):
                # Padrão "###_SHOT_NAME" ou padrão "### - Nome do Projeto"
                if (re.match(r'^\d{3}_', part) or re.match(r'^\d{3}\s-\s', part)) and i > 0:
                    return part
            
            # Se não encontrou padrão específico, usa o nome da pasta pai
            if len(parts) > 1:
                return parts[-2]
        except:
            pass
            
        return self.project_name or "Unknown Project"
        
    def _send_notification_async(self, notification_type, message, **kwargs):
        """Send notification asynchronously"""
        thread = threading.Thread(
            target=self._send_notification,
            args=(notification_type, message),
            kwargs=kwargs
        )
        thread.daemon = True
        thread.start()
        
    def _send_notification(self, notification_type, message, **kwargs):
        """Send notification to all configured services"""
        # Add default user if not provided
        if 'user' not in kwargs:
            kwargs['user'] = self.username or "Unknown"
            
        # Add project name if not provided
        if 'project_name' not in kwargs and 'file_path' in kwargs:
            kwargs['project_name'] = self._get_project_name_from_path(kwargs['file_path'])
        elif 'project_name' not in kwargs:
            kwargs['project_name'] = self.project_name or "Unknown Project"
            
        # Send to Discord
        if self.discord_integration._is_enabled():
            self.discord_integration.send_notification(notification_type, message, **kwargs)
            
        # Send to Slack
        if self.slack_integration._is_enabled():
            self.slack_integration.send_notification(notification_type, message, **kwargs)
        
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
    
    def notify_file_closed(self, file_path):
        """Sends notification when a file is closed"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"File closed ({timestamp})"
        
        self._send_notification_async(
            NotificationType.FILE_CLOSED, 
            message, 
            file_path=file_path,
            user=self.username
        )
    
    def notify_project_created(self, project_name):
        """Sends notification when a project is created"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"New project created: {project_name}"
        
        self._send_notification_async(
            NotificationType.PROJECT_CREATED, 
            message, 
            project_name=project_name,
            user=self.username
        )
    
    def notify_shot_created(self, shot_name, role_name, file_path):
        """Sends notification when a shot is created"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"New shot created: {shot_name} ({role_name})"
        
        self._send_notification_async(
            NotificationType.SHOT_CREATED, 
            message, 
            shot_name=shot_name,
            role_name=role_name,
            file_path=file_path,
            user=self.username
        )
        
    def notify_asset_created(self, asset_name, asset_type, file_path):
        """Sends notification when an asset is created"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"New asset created: {asset_name} ({asset_type})"
        
        self._send_notification_async(
            NotificationType.ASSET_CREATED, 
            message, 
            asset_name=asset_name,
            asset_type=asset_type,
            file_path=file_path,
            user=self.username
        )
        
    def test_webhook(self, webhook_type):
        """Test a webhook"""
        if webhook_type == 'DISCORD':
            if not self.discord_integration._is_enabled():
                return False, "Discord webhook is not enabled or URL is invalid"
            return self.discord_integration.test_webhook()
        elif webhook_type == 'SLACK':
            if not self.slack_integration._is_enabled():
                return False, "Slack webhook is not enabled or URL is invalid"
            return self.slack_integration.test_webhook()
        else:
            return False, "Unknown webhook type"

# Create singleton instance
notification_manager = NotificationManager() 