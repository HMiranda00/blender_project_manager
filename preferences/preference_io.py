"""
Import/Export operations for preferences configuration.
"""

import bpy
import os
import json
from bpy.types import Operator
from bpy.props import StringProperty

class PROJECTMANAGER_OT_export_config(Operator):
    """Exports settings to a JSON file"""
    bl_idname = "project.export_config"
    bl_label = "Export Settings"
    
    filepath: StringProperty(
        subtype='FILE_PATH',
        default="project_config.json"
    )
    
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
    )
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        from .preference_utils import get_addon_preferences
        
        prefs = get_addon_preferences(context)
        
        # Create a dictionary to store the settings
        config = {
            'roles': []
        }
        
        # Add the roles to the config
        for role in prefs.role_mappings:
            role_data = {
                'role_name': role.role_name,
                'description': role.description,
                'link_type': role.link_type,
                'icon': role.icon,
                'collection_color': role.collection_color,
                'hide_viewport_default': role.hide_viewport_default,
                'exclude_from_view_layer': role.exclude_from_view_layer,
                'show_status': role.show_status,
                'owns_world': role.owns_world,
                'skip_assembly': role.skip_assembly,
                'publish_path_preset': role.publish_path_preset,
                'custom_publish_path': role.custom_publish_path,
            }
            config['roles'].append(role_data)
        
        # Write the config to a JSON file
        try:
            with open(self.filepath, 'w') as file:
                json.dump(config, file, indent=4)
            self.report({'INFO'}, f"Settings exported to {self.filepath}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error exporting settings: {str(e)}")
            return {'CANCELLED'}

class PROJECTMANAGER_OT_import_config(Operator):
    """Imports settings from a JSON file"""
    bl_idname = "project.import_config"
    bl_label = "Import Settings"
    
    filepath: StringProperty(
        subtype='FILE_PATH'
    )
    
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
    )
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        from .preference_utils import get_addon_preferences
        
        prefs = get_addon_preferences(context)
        
        # Read the config from the JSON file
        try:
            with open(self.filepath, 'r') as file:
                config = json.load(file)
        except Exception as e:
            self.report({'ERROR'}, f"Error reading file: {str(e)}")
            return {'CANCELLED'}
        
        # Check if the config has the expected structure
        if 'roles' not in config:
            self.report({'ERROR'}, "Invalid configuration file: missing 'roles' key")
            return {'CANCELLED'}
        
        # Ask for confirmation before clearing existing roles
        clear_roles = True
        if prefs.role_mappings:
            bpy.context.window_manager.popup_menu(
                lambda self, context: self.layout.label(text="Existing roles will be removed."),
                title="Confirm Import",
                icon='QUESTION'
            )
        
        if clear_roles:
            # Clear existing roles
            while prefs.role_mappings:
                prefs.role_mappings.remove(0)
            
            # Add the roles from the config
            for role_data in config['roles']:
                role = prefs.role_mappings.add()
                role.role_name = role_data.get('role_name', "ROLE")
                role.description = role_data.get('description', "Role description")
                role.link_type = role_data.get('link_type', 'LINK')
                role.icon = role_data.get('icon', 'TOOL_SETTINGS')
                role.collection_color = role_data.get('collection_color', 'NONE')
                role.hide_viewport_default = role_data.get('hide_viewport_default', False)
                role.exclude_from_view_layer = role_data.get('exclude_from_view_layer', False)
                role.show_status = role_data.get('show_status', True)
                role.owns_world = role_data.get('owns_world', False)
                role.skip_assembly = role_data.get('skip_assembly', False)
                role.publish_path_preset = role_data.get('publish_path_preset', 'SHOTS')
                role.custom_publish_path = role_data.get('custom_publish_path', "")
            
            self.report({'INFO'}, f"Settings imported from {self.filepath}")
            return {'FINISHED'}
        else:
            self.report({'INFO'}, "Import cancelled by user")
            return {'CANCELLED'} 