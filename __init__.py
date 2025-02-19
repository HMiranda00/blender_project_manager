bl_info = {
    "name": "Blender Project Manager",
    "author": "Henrique Miranda",
    "version": (1, 6, 0),
    "blender": (2, 80, 0),
    "location": "N-Panel",
    "description": "Addon for project management and organization",
    "category": "Project Management"
}

import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty, IntProperty
from . import operators
from . import panels
from . import preferences

def register():
    preferences.register()
    operators.register()
    panels.register()
    
    # Registrar propriedades da cena
    bpy.types.Scene.current_project = StringProperty(
        name="Current Project",
        description="Path to the current project",
        default="",
        subtype='DIR_PATH'
    )
    
    bpy.types.Scene.current_shot = StringProperty(
        name="Current Shot",
        description="Name of the current shot",
        default=""
    )
    
    bpy.types.Scene.current_role = StringProperty(
        name="Current Role",
        description="Name of the current role",
        default=""
    )
    
    bpy.types.Scene.previous_file = StringProperty(
        name="Previous File",
        description="Path to the previous file before opening assembly",
        default=""
    )
    
    bpy.types.Scene.show_asset_manager = bpy.props.BoolProperty(name="Show Asset Manager")
    bpy.types.Scene.show_role_status = bpy.props.BoolProperty(name="Show Role Status")

def unregister():
    # Remover propriedades da cena
    del bpy.types.Scene.current_project
    del bpy.types.Scene.current_shot
    del bpy.types.Scene.current_role
    del bpy.types.Scene.previous_file
    del bpy.types.Scene.show_asset_manager
    del bpy.types.Scene.show_role_status
    
    panels.unregister()
    operators.unregister()
    preferences.unregister()