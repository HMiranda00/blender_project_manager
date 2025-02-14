"""
Asset Browser setup and configuration
"""
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
from bpy.props import StringProperty, EnumProperty
from ..utils import get_project_info
from ..utils.project_utils import get_addon_prefs
from .. import i18n

def cleanup_project_libraries(scene=None):
    """Remove temporary project libraries"""
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
            prefs = get_addon_prefs()
            if not prefs:
                print("Error: Addon preferences not found")
                return
                
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
        
        # Remove from last to first to not affect indices
        for i in reversed(to_remove):
            bpy.ops.preferences.asset_library_remove(index=i)
            
    except Exception as e:
        print(f"Error cleaning libraries: {str(e)}")

def on_file_change(dummy):
    """Handler for file changes"""
    cleanup_project_libraries()
    return None

def on_undo_redo(dummy):
    """Handler for undo/redo"""
    cleanup_project_libraries()
    return None

def setup_catalogs(assets_path):
    """Setup asset catalogs"""
    try:
        # Create catalog file path
        catalog_file = os.path.join(assets_path, "blender_assets.cats.txt")
        
        # Define default catalogs
        catalogs = {
            "PROPS": {
                "id": "d1f81597-d27d-42fd-8386-3a3def6c9200",
                "name": "Props",
                "description": "Props and small objects"
            },
            "CHR": {
                "id": "8bfeff41-7692-4f58-8238-a5c4d9dad2d0",
                "name": "Characters",
                "description": "Characters and rigs"
            },
            "ENV": {
                "id": "b741e8a3-5da8-4f5a-8f4c-e05dd1e4766c",
                "name": "Environment",
                "description": "Environment and sets"
            }
        }
        
        # Create catalog file content
        content = "VERSION 1\n\n"
        for cat_id, cat_info in catalogs.items():
            content += f"{cat_info['id']}:{cat_info['name']}:{cat_info['description']}\n"
        
        # Write catalog file
        with open(catalog_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        print(f"Error setting up catalogs: {str(e)}")

def setup_asset_browser(context, link_type='LINK'):
    """Configure Asset Browser with correct preferences"""
    try:
        # Get addon preferences
        prefs = get_addon_prefs()
        if not prefs:
            print("Erro: Preferências do addon não encontradas")
            return {'CANCELLED'}
        
        # Get project info
        project_path = context.scene.current_project
        if not project_path:
            print("Erro: Nenhum projeto selecionado")
            return {'CANCELLED'}
            
        project_name, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
        
        # Get assets path
        assets_path = os.path.join(workspace_path, "ASSETS 3D")
        if not os.path.exists(assets_path):
            os.makedirs(assets_path)
            
        # Setup catalogs first
        setup_catalogs(assets_path)
        
        # Remove existing library with same name
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
        
        # Configure linking options
        for asset_library in context.preferences.filepaths.asset_libraries:
            if asset_library.name == project_name:
                asset_library.import_method = 'APPEND' if link_type == 'APPEND' else 'LINK'
        
        # Save preferences
        bpy.ops.wm.save_userpref()
        
        return {'FINISHED'}
        
    except Exception as e:
        print(f"Erro configurando Asset Browser: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'CANCELLED'}

class SetupAssetBrowserOperator(Operator):
    bl_idname = "project.setup_asset_browser"
    bl_label = i18n.translate("Setup Asset Browser")
    bl_description = i18n.translate("Configure Asset Browser for current project")
    
    link_type: EnumProperty(
        name=i18n.translate("Link Type"),
        items=[
            ('LINK', i18n.translate("Link"), i18n.translate("Link assets (reference)")),
            ('APPEND', i18n.translate("Append"), i18n.translate("Append assets (copy)"))
        ],
        default='LINK'
    )
    
    def execute(self, context):
        return setup_asset_browser(context, self.link_type)

def register():
    bpy.utils.register_class(SetupAssetBrowserOperator)
    
    # Register handlers for automatic cleanup
    handlers = [
        (load_post, on_file_change),
        (load_factory_preferences_post, on_file_change),
        (load_factory_startup_post, on_file_change),
        (undo_post, on_undo_redo),
        (redo_post, on_undo_redo),
    ]
    
    for handler_list, func in handlers:
        if func not in handler_list:
            handler_list.append(func)

def unregister():
    bpy.utils.unregister_class(SetupAssetBrowserOperator)
    
    # Remove handlers
    handlers = [
        (load_post, on_file_change),
        (load_factory_preferences_post, on_file_change),
        (load_factory_startup_post, on_file_change),
        (undo_post, on_undo_redo),
        (redo_post, on_undo_redo),
    ]
    
    for handler_list, func in handlers:
        if func in handler_list:
            handler_list.remove(func)
    
    # Clean all libraries when deactivating
    cleanup_project_libraries()
