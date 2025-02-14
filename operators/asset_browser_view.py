"""
Asset Browser view operator
"""
import bpy
import os
from bpy.types import Operator
from ..utils import get_project_info
from ..i18n.translations import translate as i18n_translate
from ..utils.project_utils import get_addon_prefs

class PROJECTMANAGER_OT_toggle_asset_browser(Operator):
    bl_idname = "project.toggle_asset_browser"
    bl_label = i18n_translate("Asset Browser")
    bl_description = i18n_translate("Toggle project Asset Browser")

    def execute(self, context):
        try:
            # Find Asset Browser area
            asset_area = None
            for area in context.screen.areas:
                if area.type == 'FILE_BROWSER' and area.ui_type == 'ASSETS':
                    asset_area = area
                    break

            if asset_area:
                # If exists, close Asset Browser area
                with context.temp_override(area=asset_area):
                    bpy.ops.screen.area_close()
                return {'FINISHED'}
                
            # If doesn't exist, split current 3D area
            view3d_area = None
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    view3d_area = area
                    break
                    
            if not view3d_area:
                self.report({'ERROR'}, i18n_translate("3D View area not found"))
                return {'CANCELLED'}
            
            # Setup Asset Browser first
            if context.scene.current_project:
                bpy.ops.project.setup_asset_browser()
                
            # Split area horizontally at the bottom (30% height)
            with context.temp_override(area=view3d_area):
                bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.7)
                
            # Configure new area as Asset Browser
            new_area = context.screen.areas[-1]
            new_area.type = 'FILE_BROWSER'
            new_area.ui_type = 'ASSETS'
            
            # Configure Asset Browser
            space = new_area.spaces.active
            if hasattr(space, "params"):
                space.params.asset_library_reference = 'LOCAL'
                
                # Configure project library
                if context.scene.current_project:
                    prefs = get_addon_prefs()
                    project_name, _, _ = get_project_info(context.scene.current_project, prefs.use_fixed_root)
                    
                    for library in context.preferences.filepaths.asset_libraries:
                        if library.name == project_name:
                            space.params.asset_library_reference = library.name
                            break
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(PROJECTMANAGER_OT_toggle_asset_browser)

def unregister():
    bpy.utils.unregister_class(PROJECTMANAGER_OT_toggle_asset_browser)
