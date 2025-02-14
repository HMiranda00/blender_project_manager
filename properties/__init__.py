import bpy
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, BoolProperty, PointerProperty, StringProperty

class ProjectSettings(PropertyGroup):
    project_type: EnumProperty(
        name="Tipo de Projeto",
        items=[
            ('TEAM', "Equipe", "Projeto com múltiplos cargos e assembly", 'COMMUNITY', 0),
            ('SOLO', "Solo", "Projeto individual simplificado", 'PERSON', 1)
        ],
        default='TEAM'
    )
    
    asset_linking: EnumProperty(
        name="Referência de Assets",
        items=[
            ('LINK', "Link", "Assets serão linkados", 'LINKED', 0),
            ('APPEND', "Append", "Assets serão anexados", 'APPEND_BLEND', 1)
        ],
        default='LINK'
    )
    
    use_versioning: BoolProperty(
        name="Usar Versionamento",
        default=True
    )

def register():
    try:
        bpy.utils.register_class(ProjectSettings)
        if not hasattr(bpy.types.Scene, "project_settings"):
            bpy.types.Scene.project_settings = PointerProperty(type=ProjectSettings)
            
        # Adicionar propriedade para timestamp do último publish
        if not hasattr(bpy.types.Scene, "last_publish_time"):
            bpy.types.Scene.last_publish_time = StringProperty(
                name="Último Publish",
                description="Data e hora do último publish",
                default=""
            )
            
        # Adicionar propriedade para status da versão
        if not hasattr(bpy.types.Scene, "version_status"):
            bpy.types.Scene.version_status = StringProperty(
                name="Status da Versão",
                description="Status da versão atual do arquivo",
                default=""
            )
            
        # Adicionar propriedade para status do assembly
        if not hasattr(bpy.types.Scene, "assembly_status"):
            bpy.types.Scene.assembly_status = StringProperty(
                name="Status do Assembly",
                description="Status do assembly atual",
                default=""
            )
            
    except Exception as e:
        print(f"Erro ao registrar propriedades: {str(e)}")

def unregister():
    try:
        if hasattr(bpy.types.Scene, "assembly_status"):
            del bpy.types.Scene.assembly_status
            
        if hasattr(bpy.types.Scene, "version_status"):
            del bpy.types.Scene.version_status
            
        if hasattr(bpy.types.Scene, "last_publish_time"):
            del bpy.types.Scene.last_publish_time
            
        if hasattr(bpy.types.Scene, "project_settings"):
            del bpy.types.Scene.project_settings
            
        bpy.utils.unregister_class(ProjectSettings)
    except Exception as e:
        print(f"Erro ao desregistrar propriedades: {str(e)}")

# Exportar a classe para que outros módulos possam importá-la
__all__ = ['ProjectSettings'] 