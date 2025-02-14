import bpy
import os
import time
from bpy.types import Panel
from ..utils import (
    get_project_info, 
    get_publish_path, 
    save_current_file, 
    ASSEMBLY_ROLE,
    is_assembly_role
)
from ..utils.cache import DirectoryCache
from ..utils.versioning import get_version_status, get_last_publish_info, redirect_to_latest_wip
from ..i18n.translations import translate as i18n_translate
from ..core.project_context import get_project_context, save_project_context

class PROJECT_PT_Panel_N(Panel):
    """Panel in N-Panel"""
    bl_label = i18n_translate("Project Manager")
    bl_idname = "VIEW3D_PT_project_management_n"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return True  # Always show panel
    
    def draw(self, context):
        layout = self.layout
        
        try:
            if 'blender_project_manager' not in context.preferences.addons:
                layout.label(text=i18n_translate("Addon is not active"), icon='ERROR')
                return
                
            prefs = context.preferences.addons['blender_project_manager'].preferences
            
            if not hasattr(context.scene, "project_settings"):
                layout.label(text=i18n_translate("Settings not initialized"), icon='ERROR')
                return
            
            # Inicializa o contexto
            project_context = get_project_context()
            
            # Se não há projeto carregado, mostra interface inicial
            if not context.scene.current_project:
                row = layout.row(align=True)
                row.operator("project.create_project", text=i18n_translate("New"), icon='ADD')
                row.operator("project.load_project", text=i18n_translate("Open"), icon='FILE_FOLDER')
                
                # Recent Projects
                if len(prefs.recent_projects) > 0:
                    recent_box = layout.box()
                    recent_box.label(text=i18n_translate("Recent Projects:"), icon='RECOVER_LAST')
                    
                    # Recent projects list
                    row = recent_box.row()
                    col = row.column()
                    col.template_list(
                        "PROJECTMANAGER_UL_recent_projects", "recent_projects_list",
                        prefs, "recent_projects",
                        prefs, "active_recent_index",
                        rows=3
                    )
                    
                    col = row.column(align=True)
                    col.operator("project.clear_recent", icon='TRASH', text="")
                    recent_box.prop(prefs, "recent_search", text="", icon='VIEWZOOM')
                return
            
            # Atualiza o contexto se necessário
            if context.scene.current_project and not project_context.current_project:
                project_context.update_from_blender()
            elif project_context.current_project and not context.scene.current_project:
                project_context.update_blender_context()
            
            # Force update project info
            if context.scene.current_project:
                try:
                    project_info = get_project_info(context.scene.current_project)
                    print(f"Project info type: {type(project_info)}")
                    print(f"Project info value: {project_info}")
                    
                    # Apenas lê o tipo do projeto, não tenta modificá-lo
                    if hasattr(context.scene, "project_settings"):
                        settings = context.scene.project_settings
                        is_team_project = settings.project_type == 'TEAM'
                    else:
                        is_team_project = True  # Default para TEAM se as configurações não existirem
                except Exception as e:
                    print(f"Error processing project info: {str(e)}")
                    is_team_project = True  # Default para TEAM em caso de erro
            
            settings = context.scene.project_settings
            is_team_project = settings.project_type == 'TEAM'
            
            # Main box
            box = layout.box()
            
            # Current project
            if context.scene.current_project:
                project_box = box.box()
                project_box.label(text=i18n_translate("Project:"), icon='FILE_BLEND')
                row = project_box.row()
                row.label(text=os.path.basename(context.scene.current_project))
                
                # Asset Browser and Create Asset
                asset_box = layout.box()
                row = asset_box.row(align=True)
                row.operator("project.toggle_asset_browser", text=i18n_translate("Asset Browser"), icon='ASSET_MANAGER')
                row.operator("project.create_asset", text=i18n_translate("Create Asset"), icon='ADD')
                
                # Shot/Scene
                shot_box = layout.box()
                if is_team_project:
                    shot_box.label(text=i18n_translate("Shot:"), icon='SEQUENCE')
                else:
                    shot_box.label(text=i18n_translate("Scene:"), icon='SCENE_DATA')
                
                # Show current shot/scene name if exists
                if context.scene.current_shot:
                    row = shot_box.row()
                    row.label(text=context.scene.current_shot)
                
                # Management buttons always visible
                row = shot_box.row(align=True)
                if is_team_project:
                    row.operator("project.create_shot", text=i18n_translate("New Shot"), icon='ADD')
                    row.operator("project.open_shot", text=i18n_translate("Open Shot"), icon='FILE_FOLDER')
                else:
                    row.operator("project.create_shot", text=i18n_translate("New Scene"), icon='ADD')
                    row.operator("project.open_shot", text=i18n_translate("Open Scene"), icon='FILE_FOLDER')
                
                # Role Management (team mode only)
                if is_team_project:
                    print("\n=== Project Panel Debug ===")
                    print(f"Project Type: {settings.project_type}")
                    print(f"Is Team Project: {is_team_project}")
                    print(f"Current Project: {context.scene.current_project}")
                    print(f"Current Shot: {context.scene.current_shot}")
                    print(f"Current Role: {context.scene.current_role}")
                    
                    role_box = layout.box()
                    role_box.label(text=i18n_translate("Roles:"), icon='COMMUNITY')
                    
                    # Role management buttons
                    if context.scene.current_shot:
                        print("Condições para mostrar Link Role:")
                        print(f"- Tem shot: {bool(context.scene.current_shot)}")
                        print(f"- Não tem role: {not bool(context.scene.current_role)}")
                        
                        # Se tem shot, mostrar botões de gerenciamento
                        row = role_box.row(align=True)
                        row.operator("project.link_role", text=i18n_translate("Link Role"), icon='LINKED')
                        row.operator("project.open_role_file", text=i18n_translate("Open Role"), icon='FILE_FOLDER')
                        
                        # Assembly button
                        row = role_box.row()
                        if is_assembly_role(context.scene.current_role):
                            row.alert = True
                        row.operator("project.open_role_file", text=i18n_translate("Open Assembly"), icon='OUTLINER_COLLECTION').role_name = ASSEMBLY_ROLE
                        
                        # Se tem cargo, mostrar informações do cargo
                        if context.scene.current_role:
                            print("Mostrando informações do cargo atual")
                            row = role_box.row()
                            row.label(text=context.scene.current_role)
                            
                            # Version control box
                            version_box = layout.box()
                            version_box.label(text=i18n_translate("Version Control:"), icon='RECOVER_LAST')
                            
                            # Version control buttons
                            row = version_box.row(align=True)
                            row.operator("project.create_version", text=i18n_translate("New Version"), icon='ADD')
                            row.operator("project.publish_version", text=i18n_translate("Publish"), icon='EXPORT')
                            
                            # Salva o contexto após qualquer mudança
                            save_project_context()
                            
                            # Version info
                            if hasattr(context.scene, "last_publish_time") and context.scene.last_publish_time:
                                version_box.label(text=i18n_translate("Last publish: {}").format(context.scene.last_publish_time))
                            if hasattr(context.scene, "version_status") and context.scene.version_status:
                                version_box.label(text=context.scene.version_status)
                            
                            # Assembly management (only in Assembly role)
                            if is_assembly_role(context.scene.current_role):
                                print("Mostrando painel de assembly")
                                assembly_box = layout.box()
                                assembly_box.label(text=i18n_translate("Assembly:"), icon='OUTLINER_COLLECTION')
                                
                                # Update e Check Status
                                row = assembly_box.row(align=True)
                                row.operator("project.update_assembly", text=i18n_translate("Update Assembly"), icon='FILE_REFRESH')
                                row.operator("project.check_assembly", text=i18n_translate("Check Status"), icon='CHECKMARK')
                                
                                # Rebuild e Prepare
                                row = assembly_box.row(align=True)
                                row.operator("project.rebuild_assembly", text=i18n_translate("Rebuild Assembly"), icon='FILE_REFRESH')
                                row.operator("project.prepare_assembly_render", text=i18n_translate("Prepare Render"), icon='RENDER_STILL')
                                
                                # Show assembly status if available
                                if hasattr(context.scene, "assembly_status"):
                                    assembly_box.label(text=context.scene.assembly_status)
                                
                                # Status do assembly
                                status_box = assembly_box.box()
                                status_box.label(text=i18n_translate("Assembly Status"), icon='INFO')
                                if hasattr(context.scene, "assembly_status"):
                                    status_box.label(text=context.scene.assembly_status)
                    else:
                        print("Não mostrando botões de gerenciamento - Nenhum shot selecionado")
            else:
                row = box.row(align=True)
                row.operator("project.create_project", text=i18n_translate("New"), icon='ADD')
                row.operator("project.load_project", text=i18n_translate("Open"), icon='FILE_FOLDER')
                
                # Recent Projects with new list interface
                if len(prefs.recent_projects) > 0:
                    recent_box = layout.box()
                    recent_box.label(text=i18n_translate("Recent Projects:"), icon='RECOVER_LAST')
                    
                    # Recent projects list
                    row = recent_box.row()
                    
                    # Left side: List
                    col = row.column()
                    col.template_list(
                        "PROJECTMANAGER_UL_recent_projects", "recent_projects_list",
                        prefs, "recent_projects",
                        prefs, "active_recent_index",
                        rows=3
                    )
                    
                    # Right side: Management buttons
                    col = row.column(align=True)
                    col.operator("project.clear_recent", icon='TRASH', text="")
                    
                    # Search field
                    recent_box.prop(prefs, "recent_search", text="", icon='VIEWZOOM')
                    
        except Exception as e:
            print(f"Error drawing panel: {str(e)}")
            layout.label(text=i18n_translate("Error loading interface"))

class PROJECT_PT_Panel_Properties(Panel):
    """Panel in Properties"""
    bl_label = i18n_translate("Project Manager")
    bl_idname = "VIEW3D_PT_project_management_properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "tool"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        # Use same draw code as N-Panel
        PROJECT_PT_Panel_N.draw(self, context)

def register():
    try:
        bpy.utils.register_class(PROJECT_PT_Panel_N)
        bpy.utils.register_class(PROJECT_PT_Panel_Properties)
    except Exception as e:
        print(f"Erro ao registrar painéis: {str(e)}")

def unregister():
    try:
        bpy.utils.unregister_class(PROJECT_PT_Panel_Properties)
        bpy.utils.unregister_class(PROJECT_PT_Panel_N)
    except Exception as e:
        print(f"Erro ao desregistrar painéis: {str(e)}")