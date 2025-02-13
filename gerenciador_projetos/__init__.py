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
    "name": "Project Manager",
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
    
    print("Registering translations...")
    try:
        # Limpa o cache de traduções antes de registrar
        if "gerenciador_projetos.i18n" in bpy.app.translations.locales:
            bpy.app.translations.unregister("gerenciador_projetos.i18n")
        i18n.register()
    except Exception as e:
        print(f"Error registering translations: {str(e)}")
    
    print("Registering properties...")
    properties.register()
    
    print("Registering preferences...")
    preferences.register()
    
    print("Registering operators...")
    operators.register()
    
    print("Registering panels...")
    panels.register()
    
    print("Registering scene properties...")
    bpy.types.Scene.current_project = bpy.props.StringProperty(
        name="Current Project",
        description="Current project path",
        default=""
    )
    
    bpy.types.Scene.current_shot = bpy.props.StringProperty(
        name="Current Shot",
        description="Current shot name",
        default=""
    )
    
    bpy.types.Scene.current_role = bpy.props.StringProperty(
        name="Current Role",
        description="Current role name",
        default=""
    )
    
    print("Registering WindowManager properties...")
    bpy.types.WindowManager.project_settings = bpy.props.PointerProperty(type=properties.ProjectSettings)
    
    # Inicializa o contexto
    print("Initializing project context...")
    try:
        project_context = get_project_context()
        # Não tenta carregar o contexto durante o registro
        # O handler load_context_handler fará isso quando apropriado
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
    panels.unregister()
    operators.unregister()
    preferences.unregister()
    properties.unregister()
    i18n.unregister()
    
    # Remove scene properties
    del bpy.types.Scene.current_project
    del bpy.types.Scene.current_shot
    del bpy.types.Scene.current_role
    del bpy.types.WindowManager.project_settings

if __name__ == "__main__":
    register()