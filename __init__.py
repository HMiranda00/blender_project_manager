import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty, IntProperty
from .core import registry

# Registrar propriedades da cena
registry.register_property_group("Scene", "current_project", StringProperty(
    name="Current Project",
    description="Path to the current project",
    default="",
    subtype='DIR_PATH'
))

registry.register_property_group("Scene", "current_shot", StringProperty(
    name="Current Shot",
    description="Name of the current shot",
    default=""
))

registry.register_property_group("Scene", "current_role", StringProperty(
    name="Current Role",
    description="Name of the current role",
    default=""
))

registry.register_property_group("Scene", "previous_file", StringProperty(
    name="Previous File",
    description="Path to the previous file before opening assembly",
    default=""
))

registry.register_property_group("Scene", "show_asset_manager", BoolProperty(
    name="Show Asset Manager"
))

registry.register_property_group("Scene", "show_role_status", BoolProperty(
    name="Show Role Status"
))

# Importar módulos conforme necessário
# Estes imports serão atualizados gradualmente conforme convertemos os módulos
from . import operators
from . import panels
from . import preferences

def register():
    """
    Função de registro principal da extensão
    """
    # As operações de registro estão centralizadas no módulo registry
    registry.register_all()
    
    # Chamadas de registro legado - serão removidas gradualmente
    preferences.register()
    operators.register()
    panels.register()

def unregister():
    """
    Função de desregistro principal da extensão
    """
    # Chamadas de desregistro legado - serão removidas gradualmente
    panels.unregister()
    operators.unregister()
    preferences.unregister()
    
    # As operações de desregistro estão centralizadas no módulo registry
    registry.unregister_all()