"""
Properties module initialization
"""
import bpy
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, BoolProperty, PointerProperty, StringProperty
from .. import i18n
from . import shot_list

class ProjectSettings(PropertyGroup):
    project_type: EnumProperty(
        name=i18n.translate("Project Type"),
        items=[
            ('TEAM', i18n.translate("Team"), i18n.translate("Project with multiple roles and assembly"), 'COMMUNITY', 0),
            ('SOLO', i18n.translate("Solo"), i18n.translate("Simplified individual project"), 'PERSON', 1)
        ],
        default='TEAM'
    )
    
    asset_linking: EnumProperty(
        name=i18n.translate("Asset Reference"),
        items=[
            ('LINK', i18n.translate("Link"), i18n.translate("Assets will be linked"), 'LINKED', 0),
            ('APPEND', i18n.translate("Append"), i18n.translate("Assets will be appended"), 'APPEND_BLEND', 1)
        ],
        default='LINK'
    )
    
    use_versioning: BoolProperty(
        name=i18n.translate("Use Versioning"),
        default=True
    )
    
    show_settings: BoolProperty(
        name=i18n.translate("Show Settings"),
        description=i18n.translate("Show or hide project settings"),
        default=False,
        options={'SKIP_SAVE'}  # Não salvar esta propriedade no arquivo .blend
    )

def register():
    """Registra as propriedades do addon"""
    print("Iniciando registro de propriedades...")
    
    try:
        # Primeiro tentar desregistrar propriedades antigas
        properties_to_remove = [
            "project_settings",
            "current_project",
            "current_shot",
            "current_role",
            "current_project_name",
            "show_asset_manager",
            "show_role_status",
            "active_shot_index",
            "shot_list",
            "role_list",
            "active_role_index",
            "assembly_status",
            "version_status",
            "last_publish_time"
        ]
        
        for prop in properties_to_remove:
            if hasattr(bpy.types.Scene, prop):
                try:
                    delattr(bpy.types.Scene, prop)
                    print(f"Propriedade {prop} removida com sucesso")
                except:
                    print(f"Erro ao remover propriedade {prop}")
        
        # Registrar classes
        bpy.utils.register_class(ProjectSettings)
        print("Classe ProjectSettings registrada")
        
        # Registrar propriedades da cena
        bpy.types.Scene.project_settings = PointerProperty(
            type=ProjectSettings,
            name="Project Settings",
            description="Configurações do projeto",
            options={'SKIP_SAVE'}
        )
        
        bpy.types.Scene.current_project = bpy.props.StringProperty(
            name="Current Project",
            description="Current project path",
            default="",
            options={'SKIP_SAVE'}
        )
        
        bpy.types.Scene.current_shot = bpy.props.StringProperty(
            name="Current Shot",
            description="Current shot name",
            default="",
            options={'SKIP_SAVE'}
        )
        
        bpy.types.Scene.current_role = bpy.props.StringProperty(
            name="Current Role",
            description="Current role name",
            default="",
            options={'SKIP_SAVE'}
        )
        
        bpy.types.Scene.current_project_name = bpy.props.StringProperty(
            name="Project Name",
            description="Current project name",
            default="",
            options={'SKIP_SAVE'}
        )
        
        bpy.types.Scene.show_asset_manager = bpy.props.BoolProperty(
            name="Show Asset Manager",
            default=False,
            options={'SKIP_SAVE'}
        )
        
        bpy.types.Scene.show_role_status = bpy.props.BoolProperty(
            name="Show Role Status",
            default=True,
            options={'SKIP_SAVE'}
        )
        
        bpy.types.Scene.last_publish_time = bpy.props.StringProperty(
            name="Last Publish",
            description="Date and time of last publish",
            default="",
            options={'SKIP_SAVE'}
        )
        
        bpy.types.Scene.version_status = bpy.props.StringProperty(
            name="Version Status",
            description="Status of current file version",
            default="",
            options={'SKIP_SAVE'}
        )
        
        bpy.types.Scene.assembly_status = bpy.props.StringProperty(
            name="Assembly Status",
            description="Status of current assembly",
            default="",
            options={'SKIP_SAVE'}
        )
        
        # Registrar shot_list
        from .shot_list import register_shot_list
        register_shot_list()
        
        print("Propriedades registradas com sucesso")
        return True
        
    except Exception as e:
        print(f"Erro ao registrar propriedades: {str(e)}")
        raise

def unregister():
    """Desregistra as propriedades do addon"""
    print("Iniciando desregistro de propriedades...")
    
    try:
        # Desregistrar shot_list
        from .shot_list import unregister_shot_list
        unregister_shot_list()
        
        # Remover propriedades da cena
        properties_to_remove = [
            "project_settings",
            "current_project",
            "current_shot",
            "current_role",
            "current_project_name",
            "show_asset_manager",
            "show_role_status",
            "active_shot_index",
            "shot_list",
            "role_list",
            "active_role_index",
            "assembly_status",
            "version_status",
            "last_publish_time"
        ]
        
        for prop in properties_to_remove:
            if hasattr(bpy.types.Scene, prop):
                try:
                    delattr(bpy.types.Scene, prop)
                    print(f"Propriedade {prop} removida com sucesso")
                except:
                    print(f"Erro ao remover propriedade {prop}")
        
        # Desregistrar classes
        bpy.utils.unregister_class(ProjectSettings)
        print("Classe ProjectSettings desregistrada")
        
        print("Propriedades desregistradas com sucesso")
        return True
        
    except Exception as e:
        print(f"Erro ao desregistrar propriedades: {str(e)}")
        raise

# Export class for other modules to import
__all__ = ['ProjectSettings', 'shot_list'] 
