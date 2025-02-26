import bpy
import os
from bpy.types import Panel
from ..utils import get_project_info, get_publish_path, save_current_file
from ..utils.cache import DirectoryCache
from ..utils.version_control import get_folder_code

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
            
            # Get folder code for the role
            folder_code = get_folder_code(publish_path, role_settings)
            
            # Check new format first
            blend_filename = f"{project_prefix}_{folder_code}_{shot_name}_{role_name}.blend"
            blend_path = os.path.join(publish_path, blend_filename)
            
            # If not found, try old format
            if not os.path.exists(blend_path):
                blend_filename = f"{project_prefix}_{role_name}.blend"
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

        # 1. HEADER - Projeto Atual ou Seleção de Projeto
        header = layout.row(align=True)
        if context.scene.current_project:
            project_name, _, _ = get_project_info(context.scene.current_project, prefs.use_fixed_root)
            header.label(text=project_name, icon='FILE_BLEND')
            header.operator("project.load_project", text="", icon='FILE_FOLDER')
        else:
            header.operator("project.create_project", icon='FILE_NEW')
            header.operator("project.load_project", icon='FILE_FOLDER')
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
            shot_row.operator("project.open_shot", text="", icon='FILE_FOLDER')
        else:
            shot_row.operator("project.create_shot", text="New Shot", icon='ADD')
            shot_row.operator("project.open_shot", text="Open Shot", icon='FILE_FOLDER')

        # 3. ROLE MANAGEMENT
        if context.scene.current_shot:
            layout.label(text="Role Management:", icon='GROUP')
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
                    
                    # Botão principal
                    blend_path = self.verify_role_file(context, role_mapping.role_name)
                    button = cell.operator(
                        "project.open_role_file" if blend_path else "project.create_shot",
                        text=role_mapping.role_name,  # Mostra o nome do role no botão
                        icon=role_mapping.icon,
                        depress=blend_path is not None
                    )
                    if blend_path:
                        button.role_name = role_mapping.role_name
                    else:
                        button.shot_name = context.scene.current_shot
                        button.role_name = role_mapping.role_name
                    
                    # Adiciona espaço após cada célula
                    cell.separator(factor=0.3)
            
            # Link Role button
            role_box.separator(factor=0.5)
            role_box.operator("project.link_role", icon='LINK_BLEND', text="Link Role")

        # 4. CURRENT ROLE TOOLS
        if context.scene.current_role:
            layout.label(text="Current Role:", icon='TOOL_SETTINGS')
            tools_box = layout.box()
            
            # Version Control
            version_col = tools_box.column(align=True)
            version_col.scale_y = 1.1
            
            # WIP Row
            wip_row = version_col.row(align=True)
            wip_row.operator("project.new_wip_version", text="New WIP", icon='FILE_NEW')
            wip_row.operator("project.open_latest_wip", text="Latest WIP", icon='FILE_TICK')
            
            # Publish
            version_col.operator("project.publish_version", text="Publish Version", icon='EXPORT')

        # 5. ASSET TOOLS (Moved outside of current_role check)
        if context.scene.current_project:
            layout.label(text="Asset Tools:", icon='ASSET_MANAGER')
            asset_box = layout.box()
            asset_row = asset_box.row(align=True)
            asset_row.scale_y = 1.1
            asset_row.operator("project.create_asset", icon='ADD', text="New Asset")
            asset_row.operator("project.toggle_asset_browser", text="Asset Browser", icon='ASSET_MANAGER')

        # 6. ASSEMBLY TOOLS
        if context.scene.current_shot:
            layout.label(text="Assembly:", icon='SCENE_DATA')
            assembly_box = layout.box()
            assembly_row = assembly_box.row(align=True)
            assembly_row.scale_y = 1.1
            is_assembly = bpy.data.is_saved and "_ASSEMBLY.blend" in os.path.basename(bpy.data.filepath)
            
            if is_assembly:
                assembly_row.operator("project.rebuild_assembly", text="Rebuild", icon='FILE_REFRESH')
                assembly_row.operator("project.prepare_assembly_render", text="Prepare Render", icon='RENDER_STILL')
            else:
                assembly_row.operator("project.open_assembly", text="Open Assembly", icon='SCENE_DATA')

        # 7. UTILITIES
        layout.label(text="Utilities:", icon='TOOL_SETTINGS')
        utils_box = layout.box()
        utils_row = utils_box.row(align=True)
        utils_row.scale_y = 0.9
        utils_row.operator("project.open_current_directory", text="Open Directory", icon='FILE_FOLDER')
        if has_asset_browser:
            utils_row.operator("project.reload_links", text="Reload Links", icon='FILE_REFRESH')

def tag_redraw_all_areas():
    """Force all areas to redraw"""
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()

def register():
    bpy.utils.register_class(PROJECT_PT_Panel)
    
def unregister():
    bpy.utils.unregister_class(PROJECT_PT_Panel)