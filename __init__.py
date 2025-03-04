# Este é um addon para gerenciamento de projetos e cenas no Blender
# Compatível com Blender 3.x e 4.x (modo extensão)

bl_info = {
    "name": "Blender Project Manager",
    "author": "Henrique Miranda",
    "version": (1, 6, 1),
    "blender": (3, 0, 0),
    "location": "View3D > Project",
    "description": "Tools for managing Blender production projects",
    "warning": "",
    "wiki_url": "",
    "category": "Pipeline",
}

import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty, IntProperty
from . import operators
from . import panels
from . import preferences
from . import handlers

def register():
    try:
        # Registrar as pastas utils primeiro
        try:
            from . import utils
        except Exception as e:
            print(f"Erro ao importar o módulo utils: {str(e)}")
        
        # Registrar módulos na ordem correta - preferences primeiro
        try:
            preferences.register()
        except Exception as e:
            print(f"Erro ao registrar preferências: {str(e)}")
            
        try:
            operators.register()
        except Exception as e:
            print(f"Erro ao registrar operadores: {str(e)}")
            
        try:
            panels.register()
        except Exception as e:
            print(f"Erro ao registrar painéis: {str(e)}")
        
        # Registrar handlers
        try:
            handlers.register_handlers()
        except Exception as e:
            print(f"Erro ao registrar handlers: {str(e)}")
        
        # Registrar propriedades da cena
        try:
            if not hasattr(bpy.types.Scene, "current_project"):
                bpy.types.Scene.current_project = StringProperty(
                    name="Current Project",
                    description="Path to the current project",
                    default="",
                    subtype='DIR_PATH'
                )
            
            if not hasattr(bpy.types.Scene, "current_shot"):
                bpy.types.Scene.current_shot = StringProperty(
                    name="Current Shot",
                    description="Name of the current shot",
                    default=""
                )
            
            if not hasattr(bpy.types.Scene, "current_role"):
                bpy.types.Scene.current_role = StringProperty(
                    name="Current Role",
                    description="Name of the current role",
                    default=""
                )
            
            if not hasattr(bpy.types.Scene, "previous_file"):
                bpy.types.Scene.previous_file = StringProperty(
                    name="Previous File",
                    description="Path to the previous file before opening assembly",
                    default=""
                )
            
            if not hasattr(bpy.types.Scene, "show_asset_manager"):
                bpy.types.Scene.show_asset_manager = bpy.props.BoolProperty(name="Show Asset Manager")
                
            if not hasattr(bpy.types.Scene, "show_role_status"):
                bpy.types.Scene.show_role_status = bpy.props.BoolProperty(name="Show Role Status")
        except Exception as e:
            print(f"Erro ao registrar propriedades da cena: {str(e)}")
    except Exception as e:
        print(f"Erro ao registrar o addon Blender Project Manager: {str(e)}")

def unregister():
    try:
        # Parar os handlers
        try:
            handlers.unregister_handlers()
        except Exception as e:
            print(f"Erro ao desregistrar handlers: {str(e)}")
        
        # Remover propriedades da cena
        try:
            if hasattr(bpy.types.Scene, "current_project"):
                del bpy.types.Scene.current_project
                
            if hasattr(bpy.types.Scene, "current_shot"):
                del bpy.types.Scene.current_shot
                
            if hasattr(bpy.types.Scene, "current_role"):
                del bpy.types.Scene.current_role
                
            if hasattr(bpy.types.Scene, "previous_file"):
                del bpy.types.Scene.previous_file
                
            if hasattr(bpy.types.Scene, "show_asset_manager"):
                del bpy.types.Scene.show_asset_manager
                
            if hasattr(bpy.types.Scene, "show_role_status"):
                del bpy.types.Scene.show_role_status
        except Exception as e:
            print(f"Erro ao remover propriedades da cena: {str(e)}")
        
        # Desregistrar módulos na ordem inversa
        try:
            panels.unregister()
        except Exception as e:
            print(f"Erro ao desregistrar painéis: {str(e)}")
            
        try:
            operators.unregister()
        except Exception as e:
            print(f"Erro ao desregistrar operadores: {str(e)}")
            
        try:
            preferences.unregister()
        except Exception as e:
            print(f"Erro ao desregistrar preferências: {str(e)}")
    except Exception as e:
        print(f"Erro ao desregistrar o addon Blender Project Manager: {str(e)}")