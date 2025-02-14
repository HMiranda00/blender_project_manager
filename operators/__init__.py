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
    """Import a module and return it"""
    if module_name in _imported_modules:
        return _imported_modules[module_name]
    
    try:
        full_module_name = f"{__package__}.{module_name}"
        if full_module_name in sys.modules:
            importlib.reload(sys.modules[full_module_name])
        else:
            importlib.import_module(full_module_name)
        _imported_modules[module_name] = sys.modules[full_module_name]
        return _imported_modules[module_name]
    except Exception as e:
        print(f"Error importing {module_name}: {str(e)}")
        _imported_modules[module_name] = None
        return None

def register():
    """Register all operators"""
    for module_name in _modules:
        module = import_module(module_name)
        if module and hasattr(module, "register"):
            try:
                module.register()
            except Exception as e:
                print(f"Error registering {module_name}: {str(e)}")

def unregister():
    """Unregister all operators"""
    for module_name in reversed(_modules):
        if module_name in _imported_modules and _imported_modules[module_name]:
            module = _imported_modules[module_name]
            if hasattr(module, "unregister"):
                try:
                    module.unregister()
                except Exception as e:
                    print(f"Error unregistering {module_name}: {str(e)}")
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
