import bpy
from . import properties
from . import operators
from . import panels
from . import preferences
from . import i18n
from .core.project_context import (
    ProjectContextManager, 
    load_project_context, 
    save_project_context,
    get_project_context
)

bl_info = {
    "name": "Blender Project Manager",
    "author": "Henrique Carvalho",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > N",
    "description": "Project management tools",
    "category": "3D View",
}

@bpy.app.handlers.persistent
def load_context_handler(dummy):
    """Handler para carregar o contexto quando um arquivo é aberto"""
    load_project_context()

@bpy.app.handlers.persistent
def save_context_handler(dummy):
    """Handler para salvar o contexto quando um arquivo é salvo"""
    save_project_context()

def register():
    """Register the addon"""
    print("=== Starting Project Manager Registration ===")
    
    # Primeiro, verificar se o addon já está registrado
    if "blender_project_manager" in bpy.context.preferences.addons:
        print("Addon já está registrado, tentando desregistrar primeiro...")
        try:
            bpy.ops.preferences.addon_disable(module="blender_project_manager")
        except Exception as e:
            print(f"Erro ao desabilitar addon existente: {str(e)}")
    
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
                default=""
            )
        
        if not hasattr(bpy.types.Scene, "current_shot"):
            bpy.types.Scene.current_shot = bpy.props.StringProperty(
                name="Current Shot",
                description="Current shot name",
                default=""
            )
        
        if not hasattr(bpy.types.Scene, "current_role"):
            bpy.types.Scene.current_role = bpy.props.StringProperty(
                name="Current Role",
                description="Current role name",
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
    
    # Inicializa o contexto
    print("Initializing project context...")
    try:
        project_context = get_project_context()
    except Exception as e:
        print(f"Error initializing context: {str(e)}")
    
    # Registra os handlers de contexto
    if load_context_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_context_handler)
    if save_context_handler not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.append(save_context_handler)
    
    print("=== Project Manager Registration Complete ===")

def unregister():
    """Unregister the addon"""
    # Remove os handlers de contexto
    if load_context_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_context_handler)
    if save_context_handler in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(save_context_handler)
    
    # Unregister modules in reverse order
    try:
        panels.unregister()
        operators.unregister()
        preferences.unregister()
        properties.unregister()
        i18n.unregister()
        
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

if __name__ == "__main__":
    register()