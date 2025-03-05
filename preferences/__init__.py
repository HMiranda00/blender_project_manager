"""
Preferences module for Blender Project Manager addon.
Contains classes and functions for handling addon preferences.
"""

import bpy
import os
import importlib
import inspect
import traceback

from .role_definitions import RoleMapping, PROJECTMANAGER_OT_add_role_mapping, PROJECTMANAGER_OT_remove_role_mapping
from .preference_io import PROJECTMANAGER_OT_export_config, PROJECTMANAGER_OT_import_config
from .preference_utils import get_addon_preferences, _get_preference_bl_idname, get_addon_name, check_blender_version
from .webhooks import PROJECTMANAGER_OT_test_webhook
from .preference_class import ProjectPreferences, RecentProject

def initialize():
    """
    Initialize preference module settings.
    This should be called before registering classes.
    
    This function properly configures the bl_idname for the 
    preferences class based on the Blender version and
    extension/addon system being used.
    """
    try:
        # Only set bl_idname if it's not already defined or running for the first time
        if not hasattr(ProjectPreferences, 'bl_idname') or not ProjectPreferences.bl_idname:
            # For Blender 4.0+ (extension system)
            if check_blender_version():
                # Try to determine the extension's registered name
                # In Blender 4.0+, extensions can have a different naming scheme
                
                # First try to get the main module name
                main_module = inspect.getmodule(inspect.stack()[1][0])
                if main_module:
                    module_name = main_module.__name__.split('.')[0]
                    print(f"Setting bl_idname to module name: {module_name}")
                    ProjectPreferences.bl_idname = module_name
                else:
                    # Fallback to the utility function
                    addon_name = _get_preference_bl_idname()
                    print(f"Setting bl_idname using utility function: {addon_name}")
                    ProjectPreferences.bl_idname = addon_name
            else:
                # For Blender 3.x (addon system)
                # Use the package name as bl_idname
                addon_name = _get_preference_bl_idname()
                print(f"Setting bl_idname for addon: {addon_name}")
                ProjectPreferences.bl_idname = addon_name
        
        # Print the final bl_idname for debugging
        print(f"Initialized preferences with bl_idname: {ProjectPreferences.bl_idname}")
    except Exception as e:
        print(f"Error initializing preferences: {e}")
        traceback.print_exc()
        # Set a default as fallback
        ProjectPreferences.bl_idname = "blender_project_manager"

def register():
    # Initialize settings before registration
    initialize()
    
    try:
        # Register classes in order of dependencies
        bpy.utils.register_class(RecentProject)
        bpy.utils.register_class(RoleMapping)
        
        # Set the collection property types explicitly before registering the main preference class
        ProjectPreferences.role_mappings.type = RoleMapping
        ProjectPreferences.recent_projects.type = RecentProject
        
        # Register operator classes
        bpy.utils.register_class(PROJECTMANAGER_OT_add_role_mapping)
        bpy.utils.register_class(PROJECTMANAGER_OT_remove_role_mapping)
        bpy.utils.register_class(PROJECTMANAGER_OT_export_config)
        bpy.utils.register_class(PROJECTMANAGER_OT_import_config)
        bpy.utils.register_class(PROJECTMANAGER_OT_test_webhook)
        
        # Register the main preference class
        print(f"Registering ProjectPreferences with bl_idname: {ProjectPreferences.bl_idname}")
        bpy.utils.register_class(ProjectPreferences)
        print("Successfully registered ProjectPreferences")
    except Exception as e:
        print(f"Error during preferences registration: {e}")
        traceback.print_exc()

def unregister():
    # Unregister in reverse order
    try:
        bpy.utils.unregister_class(ProjectPreferences)
        bpy.utils.unregister_class(PROJECTMANAGER_OT_test_webhook)
        bpy.utils.unregister_class(PROJECTMANAGER_OT_import_config)
        bpy.utils.unregister_class(PROJECTMANAGER_OT_export_config)
        bpy.utils.unregister_class(PROJECTMANAGER_OT_remove_role_mapping)
        bpy.utils.unregister_class(PROJECTMANAGER_OT_add_role_mapping)
        bpy.utils.unregister_class(RoleMapping)
        bpy.utils.unregister_class(RecentProject)
    except Exception as e:
        print(f"Error during preferences unregistration: {e}")
        traceback.print_exc() 