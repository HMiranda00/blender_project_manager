bl_info = {
    "name": "Blender Project Manager",
    "author": "Henrique Miranda",
    "version": (1, 5, 4, 0),
    "blender": (2, 80, 0),
    "location": "N-Panel",
    "description": "Addon for project management and organization",
    "category": "Project Management"
}

import bpy
from . import operators
from . import panels
from . import preferences

def register():
    preferences.register()
    operators.register()
    panels.register()
    
    # Registrar propriedades da cena
    bpy.types.Scene.current_project = bpy.props.StringProperty(name="Current Project")
    bpy.types.Scene.current_shot = bpy.props.StringProperty(name="Current Shot")
    bpy.types.Scene.current_role = bpy.props.StringProperty(name="Current Role")
    bpy.types.Scene.show_asset_manager = bpy.props.BoolProperty(name="Show Asset Manager")
    bpy.types.Scene.show_role_status = bpy.props.BoolProperty(name="Show Role Status")

def unregister():
    # Remover propriedades da cena
    del bpy.types.Scene.current_project
    del bpy.types.Scene.current_shot
    del bpy.types.Scene.current_role
    del bpy.types.Scene.show_asset_manager
    del bpy.types.Scene.show_role_status
    
    panels.unregister()
    operators.unregister()
    preferences.unregister()