"""
Operators module initialization
"""
import bpy
import importlib
import sys
from typing import Dict, Optional
from bpy.types import Operator

# List of modules to register
_modules = [
    "asset_browser_setup",
    "asset_browser_view",
    "asset_operators",
    "assembly_operators",
    "create_project",
    "create_shot",
    "duplicate_shot",
    "link_role",
    "load_project",
    "open_role_file",
    "project_operators",
    "recent_projects",
    "role_operators",
    "ui_operators",
    "version_operators",
]

# Cache of imported modules
_imported_modules: Dict[str, Optional[object]] = {}

def import_module(module_name: str) -> Optional[object]:
    """Import a module by name"""
    try:
        # Check cache first
        if module_name in _imported_modules:
            return _imported_modules[module_name]
            
        # Remove module from cache if exists
        full_name = f"{__package__}.{module_name}"
        if full_name in sys.modules:
            del sys.modules[full_name]
            
        # Import module
        module = importlib.import_module(f".{module_name}", __package__)
        _imported_modules[module_name] = module
        return module
        
    except Exception as e:
        print(f"Error importing {module_name}: {str(e)}")
        _imported_modules[module_name] = None
        return None

def register():
    """Register operators"""
    try:
        # Clear module cache
        _imported_modules.clear()
        
        # Import and register modules
        for module_name in _modules:
            module = import_module(module_name)
            if module and hasattr(module, 'register'):
                module.register()
                
        bpy.utils.register_class(PROJECTMANAGER_OT_update_project_type)
        
    except Exception as e:
        print(f"Error registering operators: {str(e)}")
        raise

def unregister():
    """Unregister operators"""
    try:
        # Unregister modules in reverse order
        for module_name in reversed(_modules):
            # Use cached module if available
            module = _imported_modules.get(module_name)
            if not module:
                # If not in cache, try to import
                module = import_module(module_name)
                
            if module and hasattr(module, 'unregister'):
                try:
                    module.unregister()
                except RuntimeError as e:
                    # Ignore already unregistered class errors
                    if "unregister_class(...)" not in str(e):
                        raise
                except Exception as e:
                    print(f"Error unregistering {module_name}: {str(e)}")
                    
        bpy.utils.unregister_class(PROJECTMANAGER_OT_update_project_type)
        
    except Exception as e:
        print(f"Error unregistering operators: {str(e)}")
        raise
    finally:
        # Clear module cache
        _imported_modules.clear()

class PROJECTMANAGER_OT_update_project_type(Operator):
    """Update project type based on project info"""
    bl_idname = "project.update_project_type"
    bl_label = "Update Project Type"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        from ..utils import get_project_info
        
        if context.scene.current_project:
            project_info = get_project_info(context.scene.current_project)
            if isinstance(project_info, dict):
                context.scene.project_settings.project_type = project_info.get('project_type', 'TEAM')
            elif isinstance(project_info, tuple):
                context.scene.project_settings.project_type = 'TEAM'  # Default para TEAM se for tupla
        
        return {'FINISHED'}