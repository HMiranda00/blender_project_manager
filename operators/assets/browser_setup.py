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
from ...utils import get_project_info

def cleanup_project_libraries(scene=None):
    """Remove project temporary libraries"""
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
    
    asset_libs = ctx.preferences.filepaths.asset_libraries
    to_remove = []
    
    for lib in asset_libs:
        # Check if it's a library managed by our addon
        lib_path = bpy.path.abspath(lib.path)
        if "ASSETS 3D" in lib_path:
            # If there's no current project or if it's a library from another project
            if not has_project_context or lib.name != current_project_name:
                to_remove.append(lib)
    
    # Remove collected libraries
    for lib in to_remove:
        try:
            asset_libs.remove(lib)
        except Exception as e:
            print(f"Error removing library {lib.name}: {str(e)}")

def on_file_change(dummy):
    """Handler for file load events"""
    cleanup_project_libraries()

def on_undo_redo(dummy):
    """Handler for undo/redo events"""
    cleanup_project_libraries()

class ASSETBROWSER_OT_setup(Operator):
    """Setup Asset Browser for the current project"""
    bl_idname = "project.setup_asset_browser"
    bl_label = "Setup Asset Browser"
    bl_description = "Configure Asset Browser paths for this project"

    def execute(self, context):
        try:
            if not context.scene.current_project:
                self.report({'ERROR'}, "No project selected")
                return {'CANCELLED'}
                
            # Get project info
            prefs = context.preferences.addons['blender_project_manager'].preferences
            project_path = context.scene.current_project
            project_name, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
            
            # Clean up existing libraries for this project
            cleanup_project_libraries()
            
            # Get asset library collection
            asset_libs = context.preferences.filepaths.asset_libraries
            
            # Check if library already exists
            lib_exists = False
            for lib in asset_libs:
                if lib.name == project_name:
                    lib_exists = True
                    # Update path if needed
                    assets_path = os.path.join(workspace_path, "ASSETS 3D")
                    if os.path.normpath(bpy.path.abspath(lib.path)) != os.path.normpath(assets_path):
                        lib.path = assets_path
                    break
            
            # Create library if it doesn't exist
            if not lib_exists:
                assets_path = os.path.join(workspace_path, "ASSETS 3D")
                os.makedirs(assets_path, exist_ok=True)
                
                new_lib = asset_libs.add()
                new_lib.name = project_name
                new_lib.path = assets_path
            
            # Create asset catalogs if they don't exist
            catalogs_path = os.path.join(workspace_path, "ASSETS 3D", "blender_assets.cats.txt")
            
            if not os.path.exists(catalogs_path):
                # Create default catalogs
                catalogs = {
                    "VERSION": 1,
                    "CATEGORIES": [
                        {
                            "UUID": "d1f81597-d27d-42fd-8386-3a3def6c9200",
                            "NAME": "Props",
                            "COLOR": "#FF5733",
                            "PARENT": None
                        },
                        {
                            "UUID": "8bfeff41-7692-4f58-8238-a5c4d9dad2d0",
                            "NAME": "Characters",
                            "COLOR": "#33FF57",
                            "PARENT": None
                        },
                        {
                            "UUID": "b741e8a3-5da8-4f5a-8f4c-e05dd1e4766c",
                            "NAME": "Environments",
                            "COLOR": "#3357FF",
                            "PARENT": None
                        }
                    ]
                }
                
                # Save catalog file
                with open(catalogs_path, 'w') as f:
                    json.dump(catalogs, f, indent=2)
            
            self.report({'INFO'}, f"Asset Browser configured for project: {project_name}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error setting up Asset Browser: {str(e)}")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(ASSETBROWSER_OT_setup)
    
    # Register handlers
    if on_file_change not in load_post:
        load_post.append(on_file_change)
    if on_file_change not in load_factory_preferences_post:
        load_factory_preferences_post.append(on_file_change)
    if on_file_change not in load_factory_startup_post:
        load_factory_startup_post.append(on_file_change)
    if on_undo_redo not in undo_post:
        undo_post.append(on_undo_redo)
    if on_undo_redo not in redo_post:
        redo_post.append(on_undo_redo)

def unregister():
    # Unregister handlers
    if on_file_change in load_post:
        load_post.remove(on_file_change)
    if on_file_change in load_factory_preferences_post:
        load_factory_preferences_post.remove(on_file_change)
    if on_file_change in load_factory_startup_post:
        load_factory_startup_post.remove(on_file_change)
    if on_undo_redo in undo_post:
        undo_post.remove(on_undo_redo)
    if on_undo_redo in redo_post:
        redo_post.remove(on_undo_redo)
    
    bpy.utils.unregister_class(ASSETBROWSER_OT_setup) 