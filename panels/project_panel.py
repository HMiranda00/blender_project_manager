import bpy
import os
from bpy.types import Panel
from ..utils import get_project_info, get_publish_path, save_current_file
from ..utils.cache import DirectoryCache

class PROJECT_PT_Panel(Panel):
    bl_label = "Blender Project Manager"
    bl_idname = "VIEW3D_PT_project_management"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Project'
    
    def verify_role_file(self, context, role_name):
        """Verifies if there is a file for the specified role"""
        try:
            if not (context.scene.current_project and context.scene.current_shot):
                return None
                
            project_path = context.scene.current_project
            prefs = context.preferences.addons['blender_project_manager'].preferences
            project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            shot_name = context.scene.current_shot
            
            role_settings = None
            for role_mapping in prefs.role_mappings:
                if role_mapping.role_name == role_name:
                    role_settings = role_mapping
                    break
                    
            if not role_settings:
                return None
                
            publish_path = get_publish_path(
                role_settings.publish_path_preset,
                role_settings,
                context,
                project_path,
                project_name,
                shot_name,
                asset_name=role_name
            )
            
            blend_filename = f"{project_prefix}_{shot_name}_{role_name}.blend"
            blend_path = os.path.join(publish_path, blend_filename)
            
            return blend_path if os.path.exists(blend_path) else None
            
        except Exception as e:
            print(f"Error verifying role file {role_name}: {str(e)}")
            return None
    
    def open_role_file(self, context, role_name):
        """Opens the specified role file"""
        try:
            blend_path = self.verify_role_file(context, role_name)
            if blend_path and os.path.exists(blend_path):
                save_current_file()
                bpy.ops.wm.open_mainfile(filepath=blend_path)
                return True
            return False
        except Exception as e:
            print(f"Error opening role file {role_name}: {str(e)}")
            return False
    
    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons['blender_project_manager'].preferences
        
        # Projetos Recentes
        if not context.scene.current_project:
            # Cabeçalho expansível
            box = layout.box()
            header = box.row(align=True)
            header.alignment = 'LEFT'
            
            # Triângulo de expansão
            icon = 'DISCLOSURE_TRI_DOWN' if prefs.show_all_recent else 'DISCLOSURE_TRI_RIGHT'
            header.prop(
                prefs,
                "show_all_recent",
                text="",
                icon=icon,
                emboss=False
            )
            
            # Título e botões do cabeçalho
            header.label(text="Recent Projects")
            header_buttons = header.row(align=True)
            header_buttons.alignment = 'RIGHT'
            header_buttons.prop(prefs, "recent_search", text="", icon='VIEWZOOM')
            header_buttons.operator("project.clear_recent_list", text="", icon='X', emboss=False)
            
            if len(prefs.recent_projects) > 0:
                # Filtrar projetos
                filtered_projects = [
                    proj for proj in prefs.recent_projects 
                    if prefs.recent_search.lower() in proj.name.lower()
                ]
                
                # Determinar quantos projetos mostrar
                display_count = len(filtered_projects) if prefs.show_all_recent else min(3, len(filtered_projects))
                
                # Área de conteúdo (só mostrar se expandido ou houver pesquisa)
                if prefs.show_all_recent or prefs.recent_search:
                    content_box = box.column(align=True)
                    
                    for i, recent in enumerate(filtered_projects):
                        if i < display_count:
                            row = content_box.row(align=True)
                            
                            # Ícone e nome do projeto
                            sub = row.row(align=True)
                            sub.scale_x = 0.75
                            sub.label(text="", icon='FILE_FOLDER')
                            row.label(text=recent.name)
                            
                            # Botões de ação
                            buttons = row.row(align=True)
                            buttons.alignment = 'RIGHT'
                            
                            # Verificar se o modo corresponde
                            mode_matches = (prefs.use_fixed_root == recent.is_fixed_root)
                            
                            # Botão de abrir
                            op = buttons.operator(
                                "project.open_recent",
                                text="",
                                icon='RESTRICT_SELECT_OFF' if mode_matches else 'RESTRICT_SELECT_ON',
                                emboss=False,
                                depress=False
                            )
                            op.project_path = recent.path
                            op.is_fixed_root = recent.is_fixed_root
                            op.enabled = mode_matches
                            
                            # Indicador do modo do projeto
                            buttons.label(
                                text="",
                                icon='LOCKED' if recent.is_fixed_root else 'UNLOCKED'
                            )
                            
                            # Botão de remover
                            remove = buttons.operator(
                                "project.remove_recent",
                                text="",
                                icon='PANEL_CLOSE',
                                emboss=False
                            )
                            remove.project_path = recent.path
                    
                    # Mostrar contador se houver mais projetos
                    remaining = len(filtered_projects) - display_count
                    if remaining > 0 and not prefs.show_all_recent:
                        row = content_box.row()
                        row.alignment = 'CENTER'
                        row.scale_y = 0.5
                        row.label(text=f"... and {remaining} more project{'s' if remaining > 1 else ''}")
            else:
                box.label(text="No recent projects", icon='INFO')
        
        # Current Project
        box = layout.box()
        box.label(text="Current Project:")
        
        if context.scene.current_project:
            project_path = context.scene.current_project
            
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            box.label(text=f"Project: {project_name}")
            box.label(text=f"Workspace: {workspace_path}")
            box.label(text=f"Shot: {context.scene.current_shot or 'None'}")
            box.label(text=f"Role: {context.scene.current_role or 'None'}")
            
            # Role Status
            if context.scene.current_shot:
                status_box = layout.box()
                status_box.label(text="Role Status", icon='INFO')
                
                grid = status_box.grid_flow(
                    row_major=True,
                    columns=4,
                    even_columns=True,
                    even_rows=True
                )
                
                for role_mapping in prefs.role_mappings:
                    if role_mapping.show_status:
                        blend_path = self.verify_role_file(context, role_mapping.role_name)
                        
                        col = grid.column()
                        box = col.box()
                        
                        if blend_path:
                            # Role exists, open it
                            button = box.operator(
                                "project.open_role_file",
                                text="",
                                icon=role_mapping.icon,
                                depress=True
                            )
                            button.role_name = role_mapping.role_name
                        else:
                            # Role doesn't exist, create it
                            button = box.operator(
                                "project.create_shot",
                                text="",
                                icon=role_mapping.icon,
                                depress=False
                            )
                            button.shot_name = context.scene.current_shot
                            button.role_name = role_mapping.role_name

        # Main buttons
        box = layout.box()
        if not context.scene.current_project:
            if prefs.use_fixed_root:
                box.operator("project.create_project", icon='FILE_NEW', text="Create New Project (Fixed Root)")
            else:
                box.operator("project.create_project", icon='FILE_NEW', text="Create New Project")
        box.operator("project.load_project", icon='FILE_FOLDER')

        # Add button to open current file directory
        dir_box = layout.box()
        dir_box.operator("project.open_current_directory", icon='FILE_FOLDER')
        
        # Shot Management
        if context.scene.current_project:
            shot_box = layout.box()
            shot_box.label(text="Shot:", icon='SEQUENCE')
            row = shot_box.row(align=True)
            row.operator("project.create_shot", icon='ADD')
            row.operator("project.open_shot", icon='FILE_FOLDER')
            
            if context.scene.current_shot:
                shot_box.operator("project.link_role", icon='LINK_BLEND')
                
                # Version Control
                if context.scene.current_role:
                    version_box = layout.box()
                    version_box.label(text="Version Control:", icon='RECOVER_LAST')
                    
                    # WIP Controls
                    wip_row = version_box.row(align=True)
                    wip_row.operator("project.new_wip_version", icon='FILE_NEW')
                    wip_row.operator("project.open_latest_wip", icon='FILE_TICK')
                    
                    # Publish Control
                    version_box.operator("project.publish_version", icon='EXPORT')
                
                # Assembly Management
                assembly_box = layout.box()
                assembly_box.label(text="Assembly:", icon='SCENE_DATA')

                # Check if we're in an assembly file
                is_assembly = False
                if bpy.data.is_saved:
                    current_file = os.path.basename(bpy.data.filepath)
                    is_assembly = "_ASSEMBLY.blend" in current_file

                # Assembly controls
                row = assembly_box.row(align=True)
                row.operator("project.open_assembly", icon='FILE_BLEND')

                if is_assembly:
                    # Assembly file controls
                    row = assembly_box.row(align=True)
                    row.operator("project.rebuild_assembly", icon='FILE_REFRESH')
                    row.operator("project.prepare_assembly_render", icon='RENDER_STILL')
            
        # Asset Browser controls
        asset_box = layout.box()
        asset_box.label(text="Asset Browser:", icon='ASSET_MANAGER')
        
        # Check if asset browser is configured and visible
        has_asset_browser = False
        is_visible = False
        if context.scene.current_project:
            project_name, _, _ = get_project_info(context.scene.current_project, prefs.use_fixed_root)
            for lib in context.preferences.filepaths.asset_libraries:
                if lib.name == project_name:
                    has_asset_browser = True
                    break
            
            # Check if asset browser is visible
            asset_areas = [area for area in context.screen.areas if area.type == 'FILE_BROWSER' and area.ui_type == 'ASSETS']
            is_visible = len(asset_areas) > 0
        
        # First row: Create Asset and Browser
        row1 = asset_box.row(align=True)
        row1.scale_y = 1.2
        row1.operator("project.create_asset", icon='ADD', text="Create Asset")
        row1.operator("project.toggle_asset_browser", text="", icon='HIDE_OFF' if not is_visible else 'HIDE_ON')
        
        # Separator
        asset_box.separator(factor=0.7)
        
        # Second row: Asset Browser Management
        row2 = asset_box.row(align=True)
        row2.scale_y = 0.9

        # Setup/Reload button
        if has_asset_browser:
            row2.operator("project.reload_links", icon='FILE_REFRESH', text="Reload Assets")
        else:
            row2.operator("project.setup_asset_browser", icon='FILE_FOLDER', text="Setup Asset Browser")

        

def tag_redraw_all_areas():
    """Force all areas to redraw"""
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()

def register():
    bpy.utils.register_class(PROJECT_PT_Panel)
    
def unregister():
    bpy.utils.unregister_class(PROJECT_PT_Panel)