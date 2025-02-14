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

def register_shot_list():
    """Registra as propriedades da lista de shots"""
    try:
        # Registrar classe
        bpy.utils.register_class(ShotListItem)
        
        # Registrar propriedades
        if not hasattr(bpy.types.Scene, "shot_list"):
            bpy.types.Scene.shot_list = bpy.props.CollectionProperty(
                type=ShotListItem,
                options={'SKIP_SAVE'}
            )
            
        if not hasattr(bpy.types.Scene, "active_shot_index"):
            bpy.types.Scene.active_shot_index = bpy.props.IntProperty(
                options={'SKIP_SAVE'}
            )
            
        if not hasattr(bpy.types.Scene, "role_list"):
            bpy.types.Scene.role_list = bpy.props.CollectionProperty(
                type=ShotListItem,
                options={'SKIP_SAVE'}
            )
            
        if not hasattr(bpy.types.Scene, "active_role_index"):
            bpy.types.Scene.active_role_index = bpy.props.IntProperty(
                options={'SKIP_SAVE'}
            )
            
        print("Propriedades da lista de shots registradas com sucesso")
        return True
        
    except Exception as e:
        print(f"Erro ao registrar propriedades da lista de shots: {str(e)}")
        raise

def unregister_shot_list():
    """Desregistra as propriedades da lista de shots"""
    try:
        # Remover propriedades
        if hasattr(bpy.types.Scene, "active_role_index"):
            del bpy.types.Scene.active_role_index
            
        if hasattr(bpy.types.Scene, "role_list"):
            del bpy.types.Scene.role_list
            
        if hasattr(bpy.types.Scene, "active_shot_index"):
            del bpy.types.Scene.active_shot_index
            
        if hasattr(bpy.types.Scene, "shot_list"):
            del bpy.types.Scene.shot_list
            
        # Desregistrar classe
        bpy.utils.unregister_class(ShotListItem)
        
        print("Propriedades da lista de shots desregistradas com sucesso")
        return True
        
    except Exception as e:
        print(f"Erro ao desregistrar propriedades da lista de shots: {str(e)}")
        raise

def register():
    register_shot_list()

def unregister():
    unregister_shot_list() 