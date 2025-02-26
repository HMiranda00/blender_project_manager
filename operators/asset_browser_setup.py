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
        
        asset_libs = ctx.preferences.filepaths.asset_libraries
        to_remove = []
        
        # Primeiro, identificar todas as bibliotecas para remover
        for lib in asset_libs:
            # Check if it's a library managed by our addon
            lib_path = bpy.path.abspath(lib.path)
            if "ASSETS 3D" in lib_path or not os.path.exists(lib_path):
                # Se não há projeto atual ou se é uma biblioteca de outro projeto
                if not has_project_context or lib.name != current_project_name:
                    to_remove.append(lib)
        
        # Depois, remover as bibliotecas identificadas
        for lib in to_remove:
            try:
                # Tentar remover diretamente
                asset_libs.remove(lib)
            except Exception as e:
                print(f"Error removing library {lib.name}: {str(e)}")
                # Se falhar, tentar remover pelo índice
                try:
                    index = asset_libs.find(lib.name)
                    if index >= 0:
                        asset_libs.remove(index)
                except:
                    pass
                    
        # Forçar atualização da UI
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'FILE_BROWSER' and area.ui_type == 'ASSETS':
                    area.tag_redraw()
                    
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
    
    def execute(self, context):
        try:
            if not context.scene.current_project:
                self.report({'ERROR'}, "No project selected")
                return {'CANCELLED'}
            
            print("Starting Asset Browser setup...")
            
            # Get project info
            prefs = context.preferences.addons['blender_project_manager'].preferences
            project_path = context.scene.current_project
            project_name, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
            
            print(f"Project path: {project_path}")
            print(f"Workspace path: {workspace_path}")
            
            # Get asset library preferences
            asset_libs = context.preferences.filepaths.asset_libraries
            print(f"Current asset libraries count: {len(asset_libs)}")
            
            # Remove existing library for this project if exists
            for lib in asset_libs:
                print(f"Checking library: {lib.name} - {lib.path}")
                if lib.name == project_name:
                    try:
                        print(f"Removing existing library: {lib.name}")
                        asset_libs.remove(lib)
                    except Exception as e:
                        print(f"Error removing library: {str(e)}")
                        self.report({'WARNING'}, f"Error removing existing library: {str(e)}")
            
            # Add new library using operator
            try:
                print(f"Adding new library using operator")
                bpy.ops.preferences.asset_library_add()
                
                # Get the newly added library
                new_lib = asset_libs[-1]
                print(f"Configuring new library: {project_name} - {workspace_path}")
                new_lib.name = project_name
                new_lib.path = workspace_path
                print("Library added and configured successfully")
            except Exception as e:
                print(f"Error adding library: {str(e)}")
                self.report({'ERROR'}, f"Error adding library: {str(e)}")
                return {'CANCELLED'}
            
            self.report({'INFO'}, "Asset Browser configured successfully")
            return {'FINISHED'}
            
        except Exception as e:
            print(f"Error configuring Asset Browser: {str(e)}")
            self.report({'ERROR'}, f"Error configuring Asset Browser: {str(e)}")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(ASSETBROWSER_OT_setup)
    
    # Register handlers for automatic cleanup
    handlers = [
        (load_post, on_file_change),
        (load_factory_preferences_post, on_file_change),
        (load_factory_startup_post, on_file_change),
        (undo_post, on_undo_redo),
        (redo_post, on_undo_redo),
        (bpy.app.handlers.save_pre, cleanup_project_libraries),
        (bpy.app.handlers.load_post, cleanup_project_libraries)
    ]
    
    for handler_list, func in handlers:
        if func not in handler_list:
            handler_list.append(func)

def unregister():
    bpy.utils.unregister_class(ASSETBROWSER_OT_setup)
    
    # Remove handlers
    handlers = [
        (load_post, on_file_change),
        (load_factory_preferences_post, on_file_change),
        (load_factory_startup_post, on_file_change),
        (undo_post, on_undo_redo),
        (redo_post, on_undo_redo),
        (bpy.app.handlers.save_pre, cleanup_project_libraries),
        (bpy.app.handlers.load_post, cleanup_project_libraries)
    ]
    
    for handler_list, func in handlers:
        if func in handler_list:
            handler_list.remove(func)
    
    # Clear all libraries when deactivating
    cleanup_project_libraries()