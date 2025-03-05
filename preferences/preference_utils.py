"""
Utility functions for working with addon preferences.
"""

import bpy
import importlib
import sys
import traceback
import os

def check_blender_version():
    """
    Check if this is Blender 4.0+ (extension system)
    
    Returns:
        bool: True if Blender version is 4.0 or higher
    """
    return bpy.app.version[0] >= 4

def _get_preference_bl_idname():
    """
    Get the bl_idname for preferences based on Blender version.
    
    This function handles both the addon system (Blender 3.x) and
    the new extension system (Blender 4.0+).
    
    Returns:
        str: The bl_idname for preferences class
    """
    # For Blender 4.0+ extension system
    if check_blender_version():
        # In extension mode, try to get the extension name from the module name
        # The correct approach is to use the name that Blender registered the extension with
        
        # First try to find the extension in the extensions list
        for ext in bpy.context.preferences.extensions:
            # Check module path to identify our extension
            module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if hasattr(ext, "__module__") and ext.__module__.startswith("blender_project_manager"):
                return ext.__module__.split(".")[0]
        
        # If not found in the list (e.g., during initial loading)
        # Use the current module name as a fallback
        try:
            return __package__.split('.')[0]
        except:
            # Absolute fallback
            return "blender_project_manager"
    else:
        # Legacy addon system (Blender 2.8 - 3.x)
        try:
            # Try to get from current module
            from .. import bl_info
            return __package__.split('.')[0]
        except:
            # Try to infer from calling module
            import inspect
            frame = inspect.currentframe().f_back
            calling_module = inspect.getmodule(frame)
            if calling_module:
                if '.' in calling_module.__name__:
                    # If the module is a submodule, get the root package
                    return calling_module.__name__.split('.')[0]
                else:
                    return calling_module.__name__
            else:
                # Final fallback
                return "blender_project_manager"

def get_addon_name():
    """
    Get the name of the addon
    
    Returns:
        str: The name of the addon
    """
    return _get_preference_bl_idname()

def get_addon_preferences(context=None):
    """
    Get the addon preferences
    
    Args:
        context: The Blender context (optional)
    
    Returns:
        AddonPreferences: The addon preferences
    """
    if context is None:
        context = bpy.context

    addon_name = _get_preference_bl_idname()
    
    # Print debug information
    print(f"Looking for preferences with id: {addon_name}")
        
    # Extension system (Blender 4.0+)
    if check_blender_version():
        # First try all possible variations of the name
        possible_names = [
            addon_name,
            addon_name.replace(".", "_"),
            f"ext_{addon_name}",
            f"extension_{addon_name}"
        ]
        
        # Print all available extensions for debugging
        print("Available extensions:")
        for ext in context.preferences.extensions:
            print(f" - {ext.name} (id: {ext.__class__.__module__})")
            
            # Try to match by module
            if hasattr(ext, "__module__"):
                if ext.__module__.startswith(addon_name):
                    print(f"Found match by module: {ext.__module__}")
                    return ext
        
        # Try all possible name variations
        for name in possible_names:
            try:
                prefs = context.preferences.extensions.get(name)
                if prefs:
                    print(f"Found preferences with name: {name}")
                    return prefs
            except:
                pass
                
        # Try reload as last resort
        try:
            for name in possible_names:
                try:
                    print(f"Trying to reload extension: {name}")
                    bpy.ops.extension.reload_by_name(name=name)
                    prefs = context.preferences.extensions.get(name)
                    if prefs:
                        print(f"Found preferences after reload: {name}")
                        return prefs
                except Exception as e:
                    print(f"Failed to reload {name}: {e}")
        except Exception as e:
            print(f"Error during extension reload: {e}")
            traceback.print_exc()
    
    # Legacy addons (Blender 2.8 - 3.x)
    try:
        # Try all possible variations of the name
        possible_names = [
            addon_name,
            addon_name.replace(".", "_")
        ]
        
        for name in possible_names:
            try:
                prefs = context.preferences.addons[name].preferences
                if prefs:
                    return prefs
            except:
                pass
                
        print(f"Could not find addon preferences for '{addon_name}'")
        return None
    except Exception as e:
        print(f"Error getting addon preferences: {e}")
        traceback.print_exc()
        return None 