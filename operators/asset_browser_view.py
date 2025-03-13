import bpy
import os
from bpy.types import Operator
from ..utils import get_project_info

class PROJECTMANAGER_OT_toggle_asset_browser(Operator):
    bl_idname = "project.toggle_asset_browser"
    bl_label = "Asset Browser"
    bl_description = "Open/Close the project Asset Browser"

    def execute(self, context):
        try:
            # Find Asset Browser area
            asset_area = None
            for area in context.screen.areas:
                if area.type == 'FILE_BROWSER' and area.ui_type == 'ASSETS':
                    asset_area = area
                    break

            if asset_area:
                # If it exists, close the Asset Browser area
                with context.temp_override(area=asset_area):
                    bpy.ops.screen.area_close()
            else:
                # If it doesn't exist, split the current 3D area
                view3d_area = None
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        view3d_area = area
                        break

                if view3d_area:
                    # Capture areas before splitting
                    areas_before = context.screen.areas[:]

                    # Use temp_override to replace the context
                    with context.temp_override(area=view3d_area, region=view3d_area.regions[0]):
                        # Split horizontally with 15% height (smaller area at the bottom)
                        bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.15)

                    # Capture areas after splitting
                    areas_after = context.screen.areas[:]

                    # Find the newly created area
                    new_area = None
                    for area in areas_after:
                        if area not in areas_before:
                            new_area = area
                            break

                    if new_area is None:
                        self.report({'ERROR'}, "Could not find newly created area.")
                        return {'CANCELLED'}

                    # Set new area type to 'FILE_BROWSER' and ui_type to 'ASSETS'
                    new_area.type = 'FILE_BROWSER'
                    new_area.ui_type = 'ASSETS'

                    # Get the active space of the new area
                    space = new_area.spaces.active
                    
                    # Configure Asset Browser to use the current project library
                    prefs = context.preferences.addons['blender_project_manager'].preferences
                    project_path = context.scene.current_project
                    project_name, _, _ = get_project_info(project_path, prefs.use_fixed_root)
                    
                    # Wait a frame to ensure the space is updated
                    def set_library():
                        for library in context.preferences.filepaths.asset_libraries:
                            if library.name == project_name:
                                space = new_area.spaces.active
                                if hasattr(space, "params"):
                                    space.params.asset_library_reference = library.name
                                return None
                        return None
                    
                    bpy.app.timers.register(set_library, first_interval=0.1)

            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(PROJECTMANAGER_OT_toggle_asset_browser)

def unregister():
    bpy.utils.unregister_class(PROJECTMANAGER_OT_toggle_asset_browser)