import bpy
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty, BoolProperty
import os
import re
from ..utils import (
    get_project_info, 
    get_publish_path,
    save_current_file
)
from ..utils.versioning import (
    redirect_to_latest_wip,
    create_first_wip
)
from ..utils.cache import DirectoryCache
from ..utils.project_utils import get_addon_prefs
from .. import i18n

class SaveContextOperator(Operator):
    bl_idname = "project.save_context"
    bl_label = "Salvar Contexto"
    bl_description = "Salva o contexto do projeto atual"
    
    project_path: StringProperty(
        name="Project Path",
        description="Caminho do projeto",
        default=""
    )
    
    shot_name: StringProperty(
        name="Shot Name",
        description="Nome do shot",
        default=""
    )
    
    role_name: StringProperty(
        name="Role Name",
        description="Nome do cargo",
        default=""
    )
    
    def execute(self, context):
        context.scene.current_project = self.project_path
        context.scene.current_shot = self.shot_name
        context.scene.current_role = self.role_name
        return {'FINISHED'}

class SetContextOperator(Operator):
    bl_idname = "project.set_context"
    bl_label = "Set Context"
    bl_description = "Define o contexto do projeto"
    
    project_path: StringProperty(default="")
    shot_name: StringProperty(default="")
    role_name: StringProperty(default="")
    
    def execute(self, context):
        if self.project_path:
            context.scene.current_project = self.project_path
        if self.shot_name:
            context.scene.current_shot = self.shot_name
        if self.role_name:
            context.scene.current_role = self.role_name
        return {'FINISHED'}

class PROJECT_OT_open_shot(Operator):
    """Operador para abrir um shot existente"""
    bl_idname = "project.open_shot"
    bl_label = "Abrir Shot"
    bl_description = "Abre um shot existente do projeto"

    shot_to_open: StringProperty(
        name=i18n.translate("Shot"),
        description=i18n.translate("Shot to open"),
        default=""
    )

    def execute(self, context):
        try:
            if not self.shot_to_open:
                self.report({'ERROR'}, i18n.translate("Select a shot to open"))
                return {'CANCELLED'}
                
            if not context.scene.current_project:
                self.report({'ERROR'}, i18n.translate("No project loaded"))
                return {'CANCELLED'}

            # Get project info
            prefs = get_addon_prefs()
            project_path = context.scene.current_project
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Get shot path
            if context.scene.project_settings.project_type == 'TEAM':
                shot_path = os.path.join(workspace_path, "SHOTS", self.shot_to_open)
                role_path = os.path.join(shot_path, context.scene.current_role or "MAIN")
                publish_path = os.path.join(role_path, "PUBLISH")
            else:
                shot_path = os.path.join(workspace_path, "SCENES", self.shot_to_open)
                publish_path = os.path.join(shot_path, "PUBLISH")
            
            if not os.path.exists(shot_path):
                self.report({'ERROR'}, i18n.translate("Shot not found: {}").format(self.shot_to_open))
                return {'CANCELLED'}
            
            # Save current file if needed
            if not save_current_file():
                self.report({'WARNING'}, i18n.translate("Current file not saved"))
            
            # Get publish file path
            role_name = context.scene.current_role or "MAIN"
            publish_file = f"{project_prefix}_{self.shot_to_open}_{role_name}.blend"
            publish_filepath = os.path.join(publish_path, publish_file)
            
            if not os.path.exists(publish_filepath):
                self.report({'ERROR'}, i18n.translate("Shot file not found: {}").format(publish_file))
                return {'CANCELLED'}
            
            # Check for WIP version
            should_redirect, wip_path = redirect_to_latest_wip(context, publish_filepath)
            
            # Save current context
            current_project = context.scene.current_project
            current_shot = self.shot_to_open
            current_role = role_name
            
            if should_redirect and wip_path:
                # Open latest WIP
                bpy.ops.wm.open_mainfile(filepath=wip_path)
                self.report({'INFO'}, i18n.translate("Latest WIP opened: {}").format(os.path.basename(wip_path)))
            else:
                # Create first WIP if none exists
                wip_path = create_first_wip(context, publish_filepath)
                if wip_path:
                    bpy.ops.wm.open_mainfile(filepath=wip_path)
                    self.report({'INFO'}, i18n.translate("First WIP created and opened: {}").format(os.path.basename(wip_path)))
                else:
                    self.report({'ERROR'}, i18n.translate("Error creating WIP version"))
                    return {'CANCELLED'}
            
            # Restore context
            context.scene.current_project = current_project
            context.scene.current_shot = current_shot
            context.scene.current_role = current_role
            
            # Save context to file
            save_project_context()
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error opening shot: {}").format(str(e)))
            return {'CANCELLED'}

    def invoke(self, context, event):
        if not context.scene.current_project:
            self.report({'ERROR'}, "Selecione um projeto primeiro")
            return {'CANCELLED'}
            
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        
        # Mostrar projeto atual
        box = layout.box()
        box.label(text="Projeto Atual:", icon='FILE_FOLDER')
        prefs = (get_addon_prefs())
        project_name, _, _ = get_project_info(context.scene.current_project, prefs.use_fixed_root)
        box.label(text=project_name)
        
        # Seleção de shot
        layout.prop(self, "shot_to_open")

class UpdateProjectTypeOperator(Operator):
    bl_idname = "project.update_project_type"
    bl_label = i18n.translate("Update Project Type")
    
    def execute(self, context):
        try:
            # Get addon preferences
            prefs = get_addon_prefs()
            if not prefs:
                self.report({'ERROR'}, i18n.translate("Addon preferences not found. Make sure the addon is enabled."))
                return {'CANCELLED'}
            
            # Get project info
            project_path = context.scene.current_project
            if not project_path:
                self.report({'ERROR'}, i18n.translate("No project loaded"))
                return {'CANCELLED'}
            
            project_name, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
            
            # Update project type based on folder structure
            if os.path.exists(os.path.join(workspace_path, "SHOTS")):
                context.scene.project_settings.project_type = 'TEAM'
            else:
                context.scene.project_settings.project_type = 'SOLO'
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error updating project type: {}").format(str(e)))
            return {'CANCELLED'}

class UpdateProjectSettingsOperator(Operator):
    bl_idname = "project.update_settings"
    bl_label = i18n.translate("Update Project Settings")
    
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
        description=i18n.translate("Enable WIP/Publish version control system"),
        default=True
    )
    
    def execute(self, context):
        try:
            # Get addon preferences
            prefs = get_addon_prefs()
            if not prefs:
                self.report({'ERROR'}, i18n.translate("Addon preferences not found. Make sure the addon is enabled."))
                return {'CANCELLED'}
            
            # Update project settings
            context.scene.project_settings.project_type = self.project_type
            context.scene.project_settings.asset_linking = self.asset_linking
            context.scene.project_settings.use_versioning = self.use_versioning
            
            # Update Asset Browser settings
            bpy.ops.project.setup_asset_browser(
                link_type='LINK' if self.asset_linking == 'LINK' else 'APPEND'
            )
            
            self.report({'INFO'}, i18n.translate("Project settings updated"))
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error updating project settings: {}").format(str(e)))
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        # Load current settings
        self.project_type = context.scene.project_settings.project_type
        self.asset_linking = context.scene.project_settings.asset_linking
        self.use_versioning = context.scene.project_settings.use_versioning
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        # Project type
        box = layout.box()
        box.label(text=i18n.translate("Project Settings:"), icon='SETTINGS')
        box.prop(self, "project_type", expand=True)
        
        # Asset settings
        asset_box = layout.box()
        asset_box.label(text=i18n.translate("Asset Settings:"), icon='ASSET_MANAGER')
        asset_box.prop(self, "asset_linking")
        
        # Version control
        version_box = layout.box()
        version_box.label(text=i18n.translate("Version Control:"), icon='RECOVER_LAST')
        version_box.prop(self, "use_versioning")

def register():
    bpy.utils.register_class(SaveContextOperator)
    bpy.utils.register_class(SetContextOperator)
    bpy.utils.register_class(PROJECT_OT_open_shot)
    bpy.utils.register_class(UpdateProjectTypeOperator)
    bpy.utils.register_class(UpdateProjectSettingsOperator)

def unregister():
    bpy.utils.unregister_class(SaveContextOperator)
    bpy.utils.unregister_class(SetContextOperator)
    bpy.utils.unregister_class(PROJECT_OT_open_shot)
    bpy.utils.unregister_class(UpdateProjectTypeOperator)
    bpy.utils.unregister_class(UpdateProjectSettingsOperator) 
