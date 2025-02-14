"""
Shot list properties
"""
import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty
from .. import i18n

class ShotListItem(PropertyGroup):
    """Item da lista de shots e cargos"""
    name: StringProperty(
        name=i18n.translate("Name"),
        description=i18n.translate("Name of the shot or role"),
        default=""
    )
    
    type: StringProperty(
        name=i18n.translate("Type"),
        description=i18n.translate("Type of item (SHOT or ROLE)"),
        default="SHOT"
    )
    
    icon: StringProperty(
        name=i18n.translate("Icon"),
        description=i18n.translate("Icon to display"),
        default="NONE"
    )
    
    is_linked: BoolProperty(
        name=i18n.translate("Is Linked"),
        description=i18n.translate("Whether this role is linked"),
        default=False
    )

def register():
    bpy.utils.register_class(ShotListItem)
    if not hasattr(bpy.types.Scene, "shot_list"):
        bpy.types.Scene.shot_list = bpy.props.CollectionProperty(type=ShotListItem)
    if not hasattr(bpy.types.Scene, "active_shot_index"):
        bpy.types.Scene.active_shot_index = bpy.props.IntProperty()

def unregister():
    if hasattr(bpy.types.Scene, "active_shot_index"):
        del bpy.types.Scene.active_shot_index
    if hasattr(bpy.types.Scene, "shot_list"):
        del bpy.types.Scene.shot_list
    bpy.utils.unregister_class(ShotListItem) 