"""
Panels module initialization
"""
import bpy
import importlib
import sys
from typing import Dict, Optional

# List of modules to register
_modules = [
    "project_panel",
    "assembly_panel"
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
    """Register all panels"""
    for module_name in _modules:
        module = import_module(module_name)
        if module and hasattr(module, "register"):
            try:
                module.register()
            except Exception as e:
                print(f"Error registering {module_name}: {str(e)}")

def unregister():
    """Unregister all panels"""
    for module_name in reversed(_modules):
        if module_name in _imported_modules and _imported_modules[module_name]:
            module = _imported_modules[module_name]
            if hasattr(module, "unregister"):
                try:
                    module.unregister()
                except Exception as e:
                    print(f"Error unregistering {module_name}: {str(e)}")
    _imported_modules.clear()
