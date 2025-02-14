import bpy
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, BoolProperty, PointerProperty

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
        # Primeiro remover propriedades antigas se existirem
        if hasattr(bpy.types.Scene, "project_settings"):
            del bpy.types.Scene.project_settings
            
        # Registrar a classe de propriedades
        bpy.utils.register_class(ProjectSettings)
        
        # Adicionar a propriedade à cena
        bpy.types.Scene.project_settings = PointerProperty(
            type=ProjectSettings,
            name="Project Settings",
            description="Configurações do projeto"
        )
        print("Propriedades registradas com sucesso")
    except Exception as e:
        print(f"Erro ao registrar propriedades: {str(e)}")
        raise  # Re-raise para garantir que o erro seja propagado

def unregister():
    try:
        # Primeiro remover a propriedade da cena
        if hasattr(bpy.types.Scene, "project_settings"):
            del bpy.types.Scene.project_settings
            
        # Depois desregistrar a classe
        bpy.utils.unregister_class(ProjectSettings)
        print("Propriedades desregistradas com sucesso")
    except Exception as e:
        print(f"Erro ao desregistrar propriedades: {str(e)}")
        raise  # Re-raise para garantir que o erro seja propagado 