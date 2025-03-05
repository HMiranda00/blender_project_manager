"""
Webhook handling for notifications.
"""

import bpy
import json
import urllib.request
import urllib.error
from bpy.types import Operator
from bpy.props import EnumProperty

class PROJECTMANAGER_OT_test_webhook(Operator):
    """Tests a webhook"""
    bl_idname = "project.test_webhook"
    bl_label = "Test Webhook"
    
    webhook_type: EnumProperty(
        name="Webhook Type",
        description="Type of webhook to test",
        items=[
            ('DISCORD', "Discord", "Test Discord webhook"),
            ('SLACK', "Slack", "Test Slack webhook"),
        ],
        default='DISCORD'
    )
    
    def execute(self, context):
        from .preference_utils import get_addon_preferences
        
        prefs = get_addon_preferences(context)
        
        # Check if the webhook URL is set
        webhook_url = ""
        if self.webhook_type == 'DISCORD':
            webhook_url = prefs.discord_webhook_url
        elif self.webhook_type == 'SLACK':
            webhook_url = prefs.slack_webhook_url
        
        if not webhook_url:
            self.report({'ERROR'}, f"{self.webhook_type} webhook URL is not set")
            return {'CANCELLED'}
        
        # Check if the username is set
        if not prefs.username:
            self.report({'WARNING'}, "Username is not set, using 'User'")
            username = "User"
        else:
            username = prefs.username
        
        # Send test message via webhook
        try:
            if self.webhook_type == 'DISCORD':
                result = self.send_discord_webhook(webhook_url, username)
            elif self.webhook_type == 'SLACK':
                result = self.send_slack_webhook(webhook_url, username)
            
            if result:
                self.report({'INFO'}, f"Test message sent to {self.webhook_type}")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, f"Failed to send test message to {self.webhook_type}")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error sending test message: {str(e)}")
            return {'CANCELLED'}
    
    def send_discord_webhook(self, webhook_url, username):
        """
        Send a test message to Discord
        
        Args:
            webhook_url: Discord webhook URL
            username: Username to display in the message
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare the data
            data = {
                "content": f"Test message from Blender Project Manager",
                "username": f"{username}'s Blender",
                "embeds": [
                    {
                        "title": "Webhook Test",
                        "description": "This is a test notification from Blender Project Manager",
                        "color": 5814783,  # Blue color
                        "fields": [
                            {
                                "name": "Blender Version",
                                "value": f"{bpy.app.version_string}",
                                "inline": True
                            },
                            {
                                "name": "Status",
                                "value": "Success!",
                                "inline": True
                            }
                        ],
                        "footer": {
                            "text": "Blender Project Manager"
                        }
                    }
                ]
            }
            
            # Convert data to JSON
            json_data = json.dumps(data).encode('utf-8')
            
            # Create a request
            request = urllib.request.Request(
                webhook_url,
                data=json_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Send the request
            with urllib.request.urlopen(request) as response:
                return response.status == 204  # Discord returns 204 No Content on success
                
        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
            return False
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
            return False
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    def send_slack_webhook(self, webhook_url, username):
        """
        Send a test message to Slack
        
        Args:
            webhook_url: Slack webhook URL
            username: Username to display in the message
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare the data
            data = {
                "text": "Test message from Blender Project Manager",
                "username": f"{username}'s Blender",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Webhook Test*\nThis is a test notification from Blender Project Manager"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Blender Version:*\n{bpy.app.version_string}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*Status:*\nSuccess!"
                            }
                        ]
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "Blender Project Manager"
                            }
                        ]
                    }
                ]
            }
            
            # Convert data to JSON
            json_data = json.dumps(data).encode('utf-8')
            
            # Create a request
            request = urllib.request.Request(
                webhook_url,
                data=json_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Send the request
            with urllib.request.urlopen(request) as response:
                return response.status == 200  # Slack returns 200 OK on success
                
        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
            return False
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
            return False
        except Exception as e:
            print(f"Error: {str(e)}")
            return False 