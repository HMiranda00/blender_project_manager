"""
Blender Project Manager addon
"""
import bpy
import addon_utils
from . import properties
from . import operators
from . import panels
from . import preferences
from . import i18n
from .utils.project_utils import get_addon_prefs
from .core.project_context import (
    ProjectContextManager, 
    load_project_context, 
    save_project_context,
    get_project_context
)
import os

bl_info = {
    "name": "Blender Project Manager",
    "author": "Henrique Miranda, Higor Pereira",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > N",
    "description": "Project management tools",
    "category": "3D View",
}

# Export utility functions
__all__ = [
    'get_addon_prefs',
    'ProjectContextManager',
    'load_project_context',
    'save_project_context',
    'get_project_context'
]

@bpy.app.handlers.persistent
def load_context_handler(dummy):
    """Handler para carregar o contexto quando um arquivo é aberto"""
    load_project_context()

@bpy.app.handlers.persistent
def save_context_handler(dummy):
    """Handler para salvar o contexto quando um arquivo é salvo"""
    save_project_context()

def update_current_project(self, context):
    """Callback para atualizar listas quando o projeto muda"""
    try:
        # Verificar se estamos em um contexto válido
        if not hasattr(context.scene, "project_settings"):
            return None
            
        # Verificar se o projeto existe
        if not self or not os.path.exists(self):
            return None
            
        # Atualizar listas
        bpy.ops.project.update_shot_list()
        
        # Salvar contexto
        save_project_context()
    except:
        pass
    return None

@bpy.app.handlers.persistent
def update_shot_list_handler(dummy):
    """Handler para atualizar a lista de shots"""
    try:
        # Verificar se estamos em um contexto válido
        if not hasattr(bpy.context.scene, "shot_list"):
            return None
            
        # Verificar se temos um projeto
        if not bpy.context.scene.current_project:
            return None
            
        # Verificar se o projeto existe
        if not os.path.exists(bpy.context.scene.current_project):
            return None
            
        # Atualizar listas
        bpy.ops.project.update_shot_list()
    except:
        pass
    return None

def update_current_shot(self, context):
    """Callback para atualizar listas quando o shot atual muda"""
    try:
        # Verificar se estamos em um contexto válido
        if not hasattr(context.scene, "project_settings"):
            return None
            
        # Verificar se temos um projeto
        if not context.scene.current_project:
            return None
            
        # Atualizar listas
        bpy.ops.project.update_shot_list()
        
        # Salvar contexto
        save_project_context()
    except:
        pass
    return None

def unregister_addon():
    """Unregister the addon completely"""
    try:
        # Remove handlers first
        if load_context_handler in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(load_context_handler)
        if save_context_handler in bpy.app.handlers.save_pre:
            bpy.app.handlers.save_pre.remove(save_context_handler)
        
        # Unregister modules in reverse order
        try:
            panels.unregister()
        except:
            pass
            
        try:
            operators.unregister()
        except:
            pass
            
        try:
            preferences.unregister()
        except:
            pass
            
        try:
            properties.unregister()
        except:
            pass
            
        try:
            i18n.unregister()
        except:
            pass
        
        # Remove scene properties
        if hasattr(bpy.types.Scene, "current_project"):
            del bpy.types.Scene.current_project
        if hasattr(bpy.types.Scene, "current_shot"):
            del bpy.types.Scene.current_shot
        if hasattr(bpy.types.Scene, "current_role"):
            del bpy.types.Scene.current_role
        if hasattr(bpy.types.WindowManager, "project_settings"):
            del bpy.types.WindowManager.project_settings
            
    except Exception as e:
        print(f"Error unregistering addon: {str(e)}")

def register():
    """Register the addon"""
    print("=== Starting Project Manager Registration ===")
    
    # First, try to unregister completely
    if "blender_project_manager" in bpy.context.preferences.addons:
        print("Addon already registered, trying to unregister first...")
        try:
            unregister_addon()
        except Exception as e:
            print(f"Error unregistering existing addon: {str(e)}")
    
    print("Registering translations...")
    try:
        i18n.register()
    except Exception as e:
        print(f"Error registering translations: {str(e)}")
    
    print("Registering properties...")
    try:
        properties.register()
    except Exception as e:
        print(f"Error registering properties: {str(e)}")
        raise
    
    print("Registering preferences...")
    try:
        preferences.register()
    except Exception as e:
        print(f"Error registering preferences: {str(e)}")
        raise
    
    print("Registering operators...")
    try:
        operators.register()
    except Exception as e:
        print(f"Error registering operators: {str(e)}")
        raise
    
    print("Registering panels...")
    try:
        panels.register()
    except Exception as e:
        print(f"Error registering panels: {str(e)}")
        raise
    
    print("Registering scene properties...")
    try:
        if not hasattr(bpy.types.Scene, "current_project"):
            bpy.types.Scene.current_project = bpy.props.StringProperty(
                name="Current Project",
                description="Current project path",
                default="",
                update=update_current_project
            )
        
        if not hasattr(bpy.types.Scene, "current_shot"):
            bpy.types.Scene.current_shot = bpy.props.StringProperty(
                name="Current Shot",
                description="Current shot name",
                default="",
                update=update_current_shot
            )
        
        if not hasattr(bpy.types.Scene, "current_role"):
            bpy.types.Scene.current_role = bpy.props.StringProperty(
                name="Current Role",
                description="Current role name",
                default="",
                update=lambda self, context: save_project_context()
            )
            
        if not hasattr(bpy.types.Scene, "current_project_name"):
            bpy.types.Scene.current_project_name = bpy.props.StringProperty(
                name="Project Name",
                description="Current project name",
                default=""
            )
    except Exception as e:
        print(f"Error registering scene properties: {str(e)}")
        raise
    
    print("Registering WindowManager properties...")
    try:
        if not hasattr(bpy.types.WindowManager, "project_settings"):
            bpy.types.WindowManager.project_settings = bpy.props.PointerProperty(type=properties.ProjectSettings)
    except Exception as e:
        print(f"Error registering WindowManager properties: {str(e)}")
        raise
    
    # Initialize context
    print("Initializing project context...")
    try:
        project_context = get_project_context()
    except Exception as e:
        print(f"Error initializing context: {str(e)}")
    
    # Register context handlers
    if load_context_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_context_handler)
    if save_context_handler not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.append(save_context_handler)
    if update_shot_list_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(update_shot_list_handler)
    
    print("=== Project Manager Registration Complete ===")

def unregister():
    """Unregister the addon"""
    unregister_addon()

if __name__ == "__main__":
    register()
