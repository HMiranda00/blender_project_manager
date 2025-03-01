import bpy
import os
from bpy.app.handlers import persistent

# Try to import notification and file lock managers
try:
    from .utils.notification_manager import notification_manager
    from .utils.file_lock_manager import file_lock_manager
    
    # Flag to indicate that modules were successfully imported
    INTEGRATION_AVAILABLE = True
except ImportError:
    print("Integration modules not found")
    INTEGRATION_AVAILABLE = False

@persistent
def load_handler(dummy):
    """Handler called when a file is loaded"""
    if not INTEGRATION_AVAILABLE:
        return
        
    # Update notification manager settings
    notification_manager.reload_settings()
    
    # Configure file lock manager
    addon_prefs = bpy.context.preferences.addons.get("blender_project_manager")
    if addon_prefs:
        prefs = addon_prefs.preferences
        
        # Define directory for lock files
        project_dir = get_project_root()
        if project_dir:
            locks_dir = os.path.join(project_dir, "project_locks")
            os.makedirs(locks_dir, exist_ok=True)
            
            # Configure lock manager
            username = prefs.username or "User"
            file_lock_manager.setup(locks_dir, username)
            
            # Set inactivity timeout
            if hasattr(prefs, "inactivity_timeout"):
                file_lock_manager.inactivity_timeout = prefs.inactivity_timeout
    
    # Notify about file opening
    filepath = bpy.data.filepath
    if filepath:
        if file_lock_manager:
            file_lock_manager.handle_file_open(filepath)

@persistent
def save_handler(dummy):
    """Handler called when a file is saved"""
    if not INTEGRATION_AVAILABLE:
        return
        
    filepath = bpy.data.filepath
    if filepath and file_lock_manager:
        file_lock_manager.handle_file_save(filepath)

def get_project_root():
    """Returns the current project root directory"""
    # Try to get root directory from addon settings
    addon_prefs = bpy.context.preferences.addons.get("blender_project_manager")
    if addon_prefs:
        prefs = addon_prefs.preferences
        
        # If using a fixed root directory
        if getattr(prefs, "use_fixed_root", False):
            fixed_root = getattr(prefs, "fixed_root_path", "")
            if fixed_root and os.path.exists(fixed_root):
                return fixed_root
    
    # If root directory not found, use current file directory
    filepath = bpy.data.filepath
    if filepath:
        return os.path.dirname(filepath)
    
    return None

def register_handlers():
    """Registers event handlers"""
    # Add handlers for loading and saving files
    if load_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_handler)
        
    if save_handler not in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.append(save_handler)
        
def unregister_handlers():
    """Removes event handlers"""
    # Remove handlers
    if load_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_handler)
        
    if save_handler in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(save_handler)
        
    # Stop activity monitoring
    if INTEGRATION_AVAILABLE and file_lock_manager:
        file_lock_manager.stop_monitoring() 