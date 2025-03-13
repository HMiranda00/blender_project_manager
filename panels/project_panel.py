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

        # Verifica se o asset browser está configurado
        has_asset_browser = False
        if context.scene.current_project:
            project_name, _, _ = get_project_info(context.scene.current_project, prefs.use_fixed_root)
            for lib in context.preferences.filepaths.asset_libraries:
                if lib.name == project_name:
                    has_asset_browser = True
                    break

        # 1. HEADER - Projeto Atual ou Seleção de Projeto com Utilities integradas
        header = layout.row(align=True)
        if context.scene.current_project:
            project_name, _, _ = get_project_info(context.scene.current_project, prefs.use_fixed_root)
            header.label(text=project_name, icon='FILE_BLEND')
            
            # Botão de carregar projeto com ícone mais adequado
            header.operator("project.load_project", text="", icon='LOOP_BACK')
            
            # Pequeno espaçador para separar o botão de carregar projeto dos outros
            header.separator(factor=1.0)
            
            # Botões de utilities integrados ao header com ícones ajustados
            header.operator("project.open_current_directory", text="", icon='FILE_FOLDER')
            
            if has_asset_browser:
                header.operator("project.reload_links", text="", icon='FILE_REFRESH')
                
            # Assembly
            if context.scene.current_shot:
                is_assembly = bpy.data.is_saved and "_ASSEMBLY.blend" in os.path.basename(bpy.data.filepath)
                if is_assembly:
                    header.operator("project.rebuild_assembly", text="", icon='OUTLINER_OB_GROUP_INSTANCE')
                    header.operator("project.prepare_assembly_render", text="", icon='RENDER_STILL')
                else:
                    header.operator("project.open_assembly", text="", icon='OUTLINER_OB_GROUP_INSTANCE')
        else:
            header.operator("project.create_project", icon='FILE_NEW')
            header.operator("project.load_project", icon='LOOP_BACK')
            return

        # 2. SHOT MANAGEMENT
        layout.label(text="Shot Management:", icon='SEQUENCE')
        shot_box = layout.box()
        
        # Primeira linha: Criar/Abrir Shot
        shot_row = shot_box.row(align=True)
        shot_row.scale_y = 1.2
        if context.scene.current_shot:
            shot_row.label(text=context.scene.current_shot, icon='SEQUENCE')
            shot_row.operator("project.create_shot", text="New Shot", icon='ADD')
            shot_row.operator("project.duplicate_shot", text="", icon='DUPLICATE')
            shot_row.operator("project.open_shot", text="", icon='FILE_FOLDER')
        else:
            shot_row.operator("project.create_shot", text="New Shot", icon='ADD')
            shot_row.operator("project.open_shot", text="Open Shot", icon='FILE_FOLDER')

        # 3. ROLE MANAGEMENT
        if context.scene.current_shot:
            role_header = layout.row(align=True)
            role_header.label(text="Role Management:", icon='GROUP')
            # Link Role agora ao lado do título
            role_header.operator("project.link_role", icon='LINK_BLEND', text="Link Role")
            
            role_box = layout.box()
            
            # Grid de Roles com mais espaço
            grid = role_box.grid_flow(
                row_major=True,
                columns=4,
                even_columns=True,
                even_rows=True,
                align=True
            )
            
            for role_mapping in prefs.role_mappings:
                if role_mapping.show_status:
                    # Célula com padding
                    cell = grid.column(align=True)
                    cell.scale_y = 1.2  # Aumenta altura como o botão New Shot
                    
                    # Adiciona espaço entre células
                    cell.separator(factor=0.3)
                    
                    # Verificar se existe um arquivo WIP para este cargo
                    from ..operators.version_control import get_latest_wip
                    latest_wip, version = get_latest_wip(context, role_mapping.role_name)
                    
                    # Botão principal - agora sempre abre o último WIP se disponível
                    blend_path = self.verify_role_file(context, role_mapping.role_name)
                    if latest_wip:
                        # Se tiver WIP, usar o operador open_latest_wip
                        button = cell.operator(
                            "project.open_latest_wip",
                            text=role_mapping.role_name,
                            icon=role_mapping.icon,
                            depress=True
                        )
                        button.role_name = role_mapping.role_name
                    elif blend_path:
                        # Se não tiver WIP mas tiver arquivo publicado, criar primeiro WIP
                        button = cell.operator(
                            "project.open_latest_wip",
                            text=role_mapping.role_name,
                            icon=role_mapping.icon,
                            depress=True
                        )
                        button.role_name = role_mapping.role_name
                    else:
                        # Se não tiver nenhum arquivo, criar novo
                        button = cell.operator(
                            "project.create_shot",
                            text=role_mapping.role_name,
                            icon=role_mapping.icon,
                            depress=False
                        )
                        button.shot_name = context.scene.current_shot
                        button.role_name = role_mapping.role_name
                    
                    # Adiciona espaço após cada célula
                    cell.separator(factor=0.3)
            
            # Removido: Link Role button

        # 4. CURRENT ROLE TOOLS
        if context.scene.current_role:
            role_tools_header = layout.row(align=True)
            role_tools_header.label(text="Current Role:", icon='TOOL_SETTINGS')
            
            # Botões de versão secundários ao lado do título
            role_tools_header.operator("project.open_version_list", text="", icon='COLLAPSEMENU')
            role_tools_header.operator("project.open_latest_wip", text="", icon='FILE_TICK')
            
            tools_box = layout.box()
            
            # Version Control - reorganizado
            version_col = tools_box.column(align=True)
            
            # Botões de publish e new WIP - destacados
            publish_row = version_col.row(align=True)
            publish_row.scale_y = 1.5  # Botões maiores
            
            # New WIP - com texto e ícone
            new_wip_btn = publish_row.operator("project.new_wip_version", text="New WIP", icon='FILE_NEW')
            
            # Publish - maior, com texto e em destaque
            publish_btn = publish_row.operator("project.publish_version", text="Publish", icon='EXPORT')

        # 5. ASSETS - renomeado de Utilities
        layout.label(text="Assets:", icon='ASSET_MANAGER')
        assets_box = layout.box()
        
        # Asset Tools
        if context.scene.current_project:
            asset_row = assets_box.row(align=True)
            asset_row.scale_y = 1.1
            asset_row.operator("project.create_asset", icon='ADD', text="New Asset")
            if has_asset_browser:
                asset_row.operator("project.toggle_asset_browser", text="Asset Browser", icon='ASSET_MANAGER')

def tag_redraw_all_areas():
    """Force all areas to redraw"""
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()

def register():
    bpy.utils.register_class(PROJECT_PT_Panel)
    
def unregister():
    bpy.utils.unregister_class(PROJECT_PT_Panel)