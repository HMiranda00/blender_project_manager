"""
Project panel for managing projects
"""
import bpy
import os
from bpy.types import Panel, UIList
from ..utils import (
    get_project_info, 
    get_publish_path, 
    save_current_file
)
from ..utils.cache import DirectoryCache
from ..utils.versioning import get_version_status, get_last_publish_info
from ..utils.project_utils import get_addon_prefs
from .. import i18n

class PROJECTMANAGER_UL_shots(UIList):
    """Lista personalizada para shots"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.label(text=item.name, icon='SEQUENCE')
            # Botão para abrir shot
            op = row.operator("project.open_shot", icon='FILE_FOLDER', text="")
            op.shot_to_open = item.name

class PROJECTMANAGER_UL_roles(UIList):
    """Lista personalizada para cargos"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            
            # Nome e ícone do cargo
            row.label(text=item.name, icon=item.icon if item.icon != 'NONE' else 'OUTLINER_COLLECTION')
            
            # Ícone de status (apenas para itens da lista de shots/cargos)
            if hasattr(item, "is_linked"):
                if item.is_linked:
                    row.label(text="", icon='CHECKMARK')
                else:
                    row.label(text="", icon='DOT')
            
            # Botões de ação
            sub = row.row(align=True)
            # Botão para abrir
            op = sub.operator("project.open_role_file", icon='FILE_FOLDER', text="")
            op.selected_role = item.name
            # Botão para linkar
            op = sub.operator("project.link_role", icon='LINKED', text="")
            op.selected_role = item.name

def draw_shot_management(layout, context):
    """Draw shot management section"""
    shot_box = layout.box()
    shot_box.label(text=i18n.translate("Shot Management"), icon='SEQUENCE')
    
    # Botões de ação
    row = shot_box.row(align=True)
    row.operator("project.create_shot", icon='ADD', text=i18n.translate("Create Shot"))
    
    # Lista de shots
    if hasattr(context.scene, "shot_list"):
        # Template list
        row = shot_box.row()
        row.template_list(
            "PROJECTMANAGER_UL_shots", "shot_list",
            context.scene, "shot_list",
            context.scene, "active_shot_index",
            rows=3
        )
    
    # Se tiver um shot selecionado
    if context.scene.current_shot:
        info = shot_box.box()
        
        # Shot info com botões
        row = info.row(align=True)
        row.label(text=i18n.translate("Current Shot:"))
        row.operator("project.open_shot_folder", icon='FILE_FOLDER', text="")
        if context.scene.project_settings.project_type == 'TEAM':
            row.operator("project.open_assembly", icon='COMMUNITY', text="")
        
        # Nome do shot
        info.label(text=context.scene.current_shot)
        
        # Lista de cargos do shot atual
        if context.scene.current_shot and hasattr(context.scene, "role_list"):
            role_box = shot_box.box()
            role_box.label(text=i18n.translate("Shot Roles"), icon='COMMUNITY')
            row = role_box.row()
            row.template_list(
                "PROJECTMANAGER_UL_roles", "role_list",
                context.scene, "role_list",
                context.scene, "active_role_index",
                rows=3
            )

def draw_scene_management(layout, context):
    """Draw scene management section"""
    scene_box = layout.box()
    scene_box.label(text=i18n.translate("Scene Management"), icon='SCENE_DATA')
    
    row = scene_box.row(align=True)
    row.operator("project.create_shot", icon='ADD', text=i18n.translate("Create Scene"))
    
    # Lista de cenas
    if hasattr(context.scene, "shot_list"):
        row = scene_box.row()
        row.template_list(
            "PROJECTMANAGER_UL_shots", "shot_list",
            context.scene, "shot_list",
            context.scene, "active_shot_index",
            rows=3
        )
    
    if context.scene.current_shot:
        info = scene_box.box()
        info.label(text=i18n.translate("Current Scene:"))
        info.label(text=context.scene.current_shot)

class ProjectManagerPanel(Panel):
    bl_label = "Project Manager"
    bl_idname = "VIEW3D_PT_project_manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Project'
    
    @classmethod
    def poll(cls, context):
        return True
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(icon='FILE_BLEND')
    
    def draw(self, context):
        layout = self.layout
        
        # Project creation/loading
        box = layout.box()
        box.label(text=i18n.translate("Project"), icon='FILE_FOLDER')
        
        row = box.row(align=True)
        row.operator("project.create_project", icon='ADD', text=i18n.translate("Create"))
        row.operator("project.load_project", icon='FILEBROWSER', text=i18n.translate("Load"))
        
        # Show current project info if any
        if context.scene.current_project:
            try:
                prefs = get_addon_prefs()
                if not prefs:
                    return
                
                # Get project info only once
                project_info = None
                if hasattr(context.scene, "current_project_name") and context.scene.current_project_name:
                    project_name = context.scene.current_project_name
                else:
                    project_name, workspace_path, project_prefix = get_project_info(
                        context.scene.current_project,
                        prefs.use_fixed_root
                    )
                    context.scene.current_project_name = project_name
                
                # Current Project
                row = box.row()
                row.label(text=project_name)
                
                # Current Shot (if any)
                if context.scene.current_shot:
                    row = box.row()
                    row.label(text=context.scene.current_shot)
                    row.operator("project.open_shot_folder", icon='FILE_FOLDER', text="")
                
                # Project Settings (collapsible)
                settings = context.scene.project_settings
                settings_box = layout.box()
                row = settings_box.row()
                row.prop(settings, "show_settings", icon='TRIA_DOWN' if settings.show_settings else 'TRIA_RIGHT', text="", emboss=False)
                row.label(text=i18n.translate("Project Settings"), icon='SETTINGS')
                
                if settings.show_settings:
                    # Project type
                    row = settings_box.row()
                    row.label(text=i18n.translate("Type:"))
                    row.label(text=i18n.translate("Team") if settings.project_type == 'TEAM' else i18n.translate("Solo"))
                    
                    # Asset linking
                    row = settings_box.row()
                    row.label(text=i18n.translate("Asset Linking:"))
                    row.label(text=i18n.translate("Link") if settings.asset_linking == 'LINK' else i18n.translate("Append"))
                    
                    # Version control
                    row = settings_box.row()
                    row.label(text=i18n.translate("Version Control:"))
                    row.label(text=i18n.translate("Enabled") if settings.use_versioning else i18n.translate("Disabled"))
                    
                    # Update settings button
                    settings_box.operator("project.update_settings", icon='FILE_REFRESH')
                
                # Asset Browser
                asset_box = layout.box()
                row = asset_box.row(align=True)
                row.operator("project.toggle_asset_browser", icon='ASSET_MANAGER', text=i18n.translate("Asset Browser"))
                row.operator("project.reload_link", icon='FILE_REFRESH', text="")
                
                # Shot/Scene management based on project type
                if settings.project_type == 'TEAM':
                    # Shot list
                    shot_box = layout.box()
                    shot_box.label(text=i18n.translate("Shot Management"), icon='SEQUENCE')
                    
                    # Create shot button
                    row = shot_box.row()
                    row.operator("project.create_shot", icon='ADD', text=i18n.translate("Create Shot"))
                    
                    # Shot list
                    if hasattr(context.scene, "shot_list"):
                        row = shot_box.row()
                        row.template_list(
                            "PROJECTMANAGER_UL_shots", "shot_list",
                            context.scene, "shot_list",
                            context.scene, "active_shot_index",
                            rows=3
                        )
                        
                        # Open shot button
                        if context.scene.active_shot_index >= 0 and context.scene.active_shot_index < len(context.scene.shot_list):
                            row = shot_box.row()
                            row.operator("project.open_shot", icon='FILE_FOLDER', text=i18n.translate("Open Shot"))
                    
                    # Assembly
                    if context.scene.current_shot:
                        assembly_box = layout.box()
                        assembly_box.label(text=i18n.translate("Assembly"), icon='COMMUNITY')
                        
                        # Open assembly button (red)
                        row = assembly_box.row()
                        row.alert = True  # Makes the button red in a safer way
                        row.operator("project.open_assembly", icon='COMMUNITY', text=i18n.translate("Open Assembly"))
                        row.alert = False
                else:
                    # Scene list
                    scene_box = layout.box()
                    scene_box.label(text=i18n.translate("Scene Management"), icon='SCENE_DATA')
                    
                    row = scene_box.row()
                    row.operator("project.create_shot", icon='ADD', text=i18n.translate("Create Scene"))
                    
                    # Scene list
                    if hasattr(context.scene, "shot_list"):
                        row = scene_box.row()
                        row.template_list(
                            "PROJECTMANAGER_UL_shots", "shot_list",
                            context.scene, "shot_list",
                            context.scene, "active_shot_index",
                            rows=3
                        )
                        
                        # Open scene button
                        if context.scene.active_shot_index >= 0 and context.scene.active_shot_index < len(context.scene.shot_list):
                            row = scene_box.row()
                            row.operator("project.open_shot", icon='FILE_FOLDER', text=i18n.translate("Open Scene"))
                
                # Version control
                if context.scene.current_shot and settings.use_versioning:
                    version_box = layout.box()
                    version_box.label(text=i18n.translate("Version Control"), icon='RECOVER_LAST')
                    
                    row = version_box.row(align=True)
                    row.operator("project.save_version", icon='FILE_NEW', text=i18n.translate("Save Version"))
                    row.operator("project.publish_version", icon='EXPORT', text=i18n.translate("Publish"))
                
            except Exception as e:
                box.label(text=str(e), icon='ERROR')

def update_active_shot(self, context):
    """Callback para atualizar listas quando o shot ativo muda"""
    try:
        # Verificar se temos um projeto
        if not context.scene.current_project:
            return None
            
        # Verificar se temos uma lista de shots
        if not hasattr(context.scene, "shot_list"):
            return None
            
        # Verificar se o índice é válido
        if context.scene.active_shot_index < 0 or context.scene.active_shot_index >= len(context.scene.shot_list):
            return None
            
        # Atualizar shot atual
        shot_item = context.scene.shot_list[context.scene.active_shot_index]
        if shot_item:
            # Atualizar contexto
            context.scene.current_shot = shot_item.name
            # Atualizar listas
            bpy.ops.project.update_shot_list()
            
            # Salvar contexto
            from ..core.project_context import save_project_context
            save_project_context()
    except Exception as e:
        print(f"Erro no callback do shot ativo: {str(e)}")
        import traceback
        traceback.print_exc()
    return None

def register():
    """Registra os painéis e suas classes"""
    bpy.utils.register_class(PROJECTMANAGER_UL_shots)
    bpy.utils.register_class(PROJECTMANAGER_UL_roles)
    bpy.utils.register_class(ProjectManagerPanel)

def unregister():
    """Desregistra os painéis e suas classes"""
    bpy.utils.unregister_class(ProjectManagerPanel)
    bpy.utils.unregister_class(PROJECTMANAGER_UL_roles)
    bpy.utils.unregister_class(PROJECTMANAGER_UL_shots)
