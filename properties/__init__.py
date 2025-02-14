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

def register():
    try:
        bpy.utils.register_class(ProjectSettings)
        if not hasattr(bpy.types.Scene, "project_settings"):
            bpy.types.Scene.project_settings = PointerProperty(type=ProjectSettings)
            
        # Add property for last publish timestamp
        if not hasattr(bpy.types.Scene, "last_publish_time"):
            bpy.types.Scene.last_publish_time = StringProperty(
                name=i18n.translate("Last Publish"),
                description=i18n.translate("Date and time of last publish"),
                default=""
            )
            
        # Add property for version status
        if not hasattr(bpy.types.Scene, "version_status"):
            bpy.types.Scene.version_status = StringProperty(
                name=i18n.translate("Version Status"),
                description=i18n.translate("Status of current file version"),
                default=""
            )
            
        # Add property for assembly status
        if not hasattr(bpy.types.Scene, "assembly_status"):
            bpy.types.Scene.assembly_status = StringProperty(
                name=i18n.translate("Assembly Status"),
                description=i18n.translate("Status of current assembly"),
                default=""
            )
            
        # Register shot list properties
        shot_list.register()
            
    except Exception as e:
        print(f"Error registering properties: {str(e)}")

def unregister():
    try:
        # Unregister shot list properties
        shot_list.unregister()
        
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
        print(f"Error unregistering properties: {str(e)}")

# Export class for other modules to import
__all__ = ['ProjectSettings', 'shot_list'] 
