import bpy
import os
import json
from bpy.types import Operator
from bpy.app.handlers import (
    load_post,
    load_factory_preferences_post,
    load_factory_startup_post,
    undo_post,
    redo_post,
)
from ..utils import get_project_info

def cleanup_project_libraries(scene=None):
    """Remove project temporary libraries"""
    try:
        ctx = bpy.context
        
        # Check if we still have project context
        has_project_context = (
            hasattr(ctx.scene, "current_project") and 
            ctx.scene.current_project and 
            os.path.exists(ctx.scene.current_project)
        )
        
        current_project_name = None
        if has_project_context:
            prefs = ctx.preferences.addons['blender_project_manager'].preferences
            project_path = ctx.scene.current_project
            project_name, _, _ = get_project_info(project_path, prefs.use_fixed_root)
            current_project_name = project_name
        
        # Remove old libraries
        asset_libs = ctx.preferences.filepaths.asset_libraries
        to_remove = []
        
        for i, lib in enumerate(asset_libs):
            lib_path = bpy.path.abspath(lib.path)
            if "ASSETS 3D" in lib_path:
                if not has_project_context or lib.name != current_project_name:
                    to_remove.append(i)
        
        # Remove from last to first to avoid index changes
        for i in reversed(to_remove):
            try:
                bpy.ops.preferences.asset_library_remove(index=i)
            except Exception as e:
                print(f"Error removing library at index {i}: {str(e)}")
            
    except Exception as e:
        print(f"Error cleaning up libraries: {str(e)}")

def on_file_change(dummy):
    """Handler for file changes"""
    cleanup_project_libraries()
    return None

def on_undo_redo(dummy):
    """Handler for undo/redo"""
    cleanup_project_libraries()
    return None

class ASSETBROWSER_OT_setup(Operator):
    """Setup Asset Browser for the current project"""
    bl_idname = "project.setup_asset_browser"
    bl_label = "Setup Asset Browser"
    bl_description = "Configure Asset Browser paths for this project"
    
    link_type: bpy.props.EnumProperty(
        name="Link Type",
        items=[
            ('LINK', "Link", "Assets will be linked"),
            ('APPEND', "Append", "Assets will be appended")
        ],
        default='LINK'
    )
    
    @classmethod
    def poll(cls, context):
        return context.scene.current_project is not None
    
    def setup_catalogs(self, library_path):
        """Create default catalogs"""
        catalog_path = os.path.join(library_path, "blender_assets.cats.txt")
        
        catalogs_data = """# This is an Asset Catalog Definition file for Blender.
#
# Empty lines and lines starting with `#` will be ignored.
# The first non-ignored line should be the version indicator.
# Other lines are of the format "UUID:catalog/path/for/assets:simple catalog name"
VERSION 1
d1f81597-d27d-42fd-8386-3a3def6c9200:PROPS:PROPS
8bfeff41-7692-4f58-8238-a5c4d9dad2d0:CHR:CHR
b741e8a3-5da8-4f5a-8f4c-e05dd1e4766c:ENV:ENV
f5780a5c-74a4-4dd9-9e3d-c3654cf91f5c:MATERIALS:MATERIALS"""
        
        with open(catalog_path, 'w', encoding='utf-8') as f:
            f.write(catalogs_data)
    
    def execute(self, context):
        try:
            # Clean up other project libraries first
            cleanup_project_libraries(context.scene)
            
            # Get project info
            prefs = context.preferences.addons['blender_project_manager'].preferences
            project_path = context.scene.current_project
            project_name, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
            
            # Setup assets folder
            assets_path = os.path.join(workspace_path, "ASSETS 3D")
            if not os.path.exists(assets_path):
                os.makedirs(assets_path)
            
            # Create catalogs first
            self.setup_catalogs(assets_path)
            
            # Remove existing library with same name if any
            asset_libs = context.preferences.filepaths.asset_libraries
            for i, lib in enumerate(asset_libs):
                if lib.name == project_name:
                    bpy.ops.preferences.asset_library_remove(index=i)
                    break
            
            # Add new library
            bpy.ops.preferences.asset_library_add()
            new_lib = context.preferences.filepaths.asset_libraries[-1]
            new_lib.name = project_name
            new_lib.path = assets_path
            
            # Configure asset browser
            for asset_library in bpy.context.preferences.filepaths.asset_libraries:
                if asset_library.name == project_name:
                    # Configure link options based on project settings
                    asset_library.import_method = 'APPEND' if self.link_type == 'APPEND' else 'LINK'
            
            self.report({'INFO'}, f"Asset Library '{project_name}' configured with catalogs")
            return {'FINISHED'}
            
        except Exception as e:
            print(f"Error configuring Asset Browser: {str(e)}")
            self.report({'ERROR'}, f"Error configuring Asset Browser: {str(e)}")
            return {'CANCELLED'}

class ASSETBROWSER_OT_toggle(Operator):
    """Toggle Asset Browser visibility"""
    bl_idname = "project.toggle_asset_browser"
    bl_label = "Toggle Asset Browser"
    bl_description = "Show/Hide Asset Browser"
    
    def execute(self, context):
        try:
            # Find existing asset browser areas
            asset_areas = [area for area in context.screen.areas if area.type == 'FILE_BROWSER' and area.ui_type == 'ASSETS']
            
            if asset_areas:
                # Close asset browser areas
                for area in asset_areas:
                    # Close the area using temp_override
                    with context.temp_override(area=area):
                        bpy.ops.screen.area_close()
                
                context.scene.show_asset_manager = False
            else:
                # Find the first 3D View area
                view3d_area = None
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        view3d_area = area
                        break
                
                if view3d_area:
                    # Capture areas before splitting
                    areas_before = context.screen.areas[:]
                    
                    # Split the area horizontally (15% at bottom)
                    with context.temp_override(area=view3d_area, region=view3d_area.regions[0]):
                        bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.15)
                    
                    # Find the new area
                    new_area = None
                    for area in context.screen.areas:
                        if area not in areas_before:
                            new_area = area
                            break
                    
                    if new_area is None:
                        self.report({'ERROR'}, "Could not find newly created area")
                        return {'CANCELLED'}
                    
                    # Set the new area as asset browser
                    new_area.type = 'FILE_BROWSER'
                    new_area.ui_type = 'ASSETS'
                    
                    # Configure asset browser for current project
                    space = new_area.spaces.active
                    prefs = context.preferences.addons['blender_project_manager'].preferences
                    project_path = context.scene.current_project
                    project_name, _, _ = get_project_info(project_path, prefs.use_fixed_root)
                    
                    # Use timer to ensure space is updated
                    def set_library():
                        for library in context.preferences.filepaths.asset_libraries:
                            if library.name == project_name:
                                space = new_area.spaces.active
                                if hasattr(space, "params"):
                                    space.params.asset_library_reference = library.name
                                return None
                        return None
                    
                    bpy.app.timers.register(set_library, first_interval=0.1)
                    
                    context.scene.show_asset_manager = True
            
            # Force redraw
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()
                    
            return {'FINISHED'}
            
        except Exception as e:
            print(f"Error toggling asset browser: {str(e)}")
            self.report({'ERROR'}, f"Error toggling asset browser: {str(e)}")
            return {'CANCELLED'}

def register():
    # Registrar classes com segurança
    classes = [ASSETBROWSER_OT_setup, ASSETBROWSER_OT_toggle]
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Erro ao registrar {cls.__name__}: {str(e)}")
    
    # Register handlers for automatic cleanup
    handlers = [
        (load_post, on_file_change),
        (load_factory_preferences_post, on_file_change),
        (load_factory_startup_post, on_file_change),
        (undo_post, on_undo_redo),
        (redo_post, on_undo_redo),
    ]
    
    for handler_list, func in handlers:
        try:
            if func not in handler_list:
                handler_list.append(func)
        except Exception as e:
            print(f"Erro ao adicionar handler: {str(e)}")

def unregister():
    # Desregistrar as classes com segurança
    for cls_name in ['ASSETBROWSER_OT_setup', 'ASSETBROWSER_OT_toggle']:
        try:
            cls = getattr(bpy.types, cls_name, None)
            if cls is not None:
                bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Erro ao desregistrar {cls_name}: {str(e)}")
    
    # Remove handlers
    handlers = [
        (load_post, on_file_change),
        (load_factory_preferences_post, on_file_change),
        (load_factory_startup_post, on_file_change),
        (undo_post, on_undo_redo),
        (redo_post, on_undo_redo),
    ]
    
    for handler_list, func in handlers:
        try:
            if func in handler_list:
                handler_list.remove(func)
        except Exception as e:
            print(f"Erro ao remover handler: {str(e)}")
    
    # Clear all libraries when deactivating
    try:
        cleanup_project_libraries()
    except Exception as e:
        print(f"Erro ao limpar bibliotecas: {str(e)}")