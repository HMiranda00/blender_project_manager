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
            for i, lib in enumerate(asset_libs):
                print(f"Checking library {i}: {lib.name} - {lib.path}")
                if lib.name == project_name:
                    try:
                        print(f"Removing existing library: {lib.name}")
                        index = asset_libs.find(lib.name)
                        if index >= 0:
                            asset_libs.remove(index)
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
                    # Get area dimensions before closing
                    area_dims = area.width, area.height
                    
                    # Find adjacent areas that might need resizing
                    adjacent_areas = []
                    for other_area in context.screen.areas:
                        if other_area != area:
                            # Check if areas are adjacent (share x or y coordinates)
                            if (abs(other_area.x + other_area.width - area.x) < 1 or
                                abs(other_area.x - (area.x + area.width)) < 1 or
                                abs(other_area.y + other_area.height - area.y) < 1 or
                                abs(other_area.y - (area.y + area.height)) < 1):
                                adjacent_areas.append(other_area)
                    
                    # Close the area
                    override = {"area": area}
                    bpy.ops.screen.area_close(override)
                    
                    # Resize adjacent areas to fill the space
                    for adj_area in adjacent_areas:
                        if abs(adj_area.x - area.x) < 1 or abs(adj_area.x - (area.x + area.width)) < 1:
                            adj_area.width += area_dims[0]
                        if abs(adj_area.y - area.y) < 1 or abs(adj_area.y - (area.y + area.height)) < 1:
                            adj_area.height += area_dims[1]
                
                context.scene.show_asset_manager = False
            else:
                # Find the largest 3D View area
                view3d_area = None
                max_size = 0
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        size = area.width * area.height
                        if size > max_size:
                            max_size = size
                            view3d_area = area
                
                if view3d_area:
                    # Store original dimensions
                    original_width = view3d_area.width
                    
                    # Split the area vertically
                    override = {"area": view3d_area}
                    bpy.ops.screen.area_split(override, direction='VERTICAL', factor=0.7)
                    
                    # Get the new area and set it as asset browser
                    new_area = context.screen.areas[-1]
                    new_area.type = 'FILE_BROWSER'
                    new_area.ui_type = 'ASSETS'
                    
                    # Ensure the split maintains proper proportions
                    view3d_area.width = int(original_width * 0.7)
                    new_area.width = original_width - view3d_area.width
                    
                    context.scene.show_asset_manager = True
            
            # Force redraw of all areas
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()
            
            return {'FINISHED'}
            
        except Exception as e:
            print(f"Error toggling asset browser: {str(e)}")
            self.report({'ERROR'}, f"Error toggling asset browser: {str(e)}")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(ASSETBROWSER_OT_setup)
    bpy.utils.register_class(ASSETBROWSER_OT_toggle)
    
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
    bpy.utils.unregister_class(ASSETBROWSER_OT_toggle)
    bpy.utils.unregister_class(ASSETBROWSER_OT_setup)
    
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
    
    # Clear all libraries when deactivating
    cleanup_project_libraries()