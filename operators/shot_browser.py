"""
Shot browser operators for managing shots in the project
"""
import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty, BoolProperty
from ..utils.project_utils import get_addon_prefs, save_current_file
from ..utils import get_project_info
from ..utils.versioning import redirect_to_latest_wip, create_first_wip
from .. import i18n

class ShotBrowserOperator(Operator):
    bl_idname = "project.shot_browser"
    bl_label = i18n.translate("Shot Browser")
    
    def execute(self, context):
        try:
            # Get addon preferences
            prefs = get_addon_prefs()
            if not prefs:
                self.report({'ERROR'}, i18n.translate("Addon preferences not found. Make sure the addon is enabled."))
                return {'CANCELLED'}
            
            # Get project info
            project_path = context.scene.current_project
            if not project_path:
                self.report({'ERROR'}, i18n.translate("No project loaded"))
                return {'CANCELLED'}
            
            project_name, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
            
            # Get shots path
            shots_path = os.path.join(workspace_path, "SHOTS")
            if not os.path.exists(shots_path):
                self.report({'ERROR'}, i18n.translate("No shots folder found"))
                return {'CANCELLED'}
            
            # Get list of shots
            shots = []
            for shot in os.listdir(shots_path):
                shot_path = os.path.join(shots_path, shot)
                if os.path.isdir(shot_path) and shot != "ASSEMBLY":
                    shots.append(shot)
            
            # Store shots in window manager
            context.window_manager.shot_list = shots
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error loading shots: {}").format(str(e)))
            return {'CANCELLED'}

class OpenShotOperator(Operator):
    bl_idname = "project.open_shot"
    bl_label = i18n.translate("Open Shot")
    
    shot_name: StringProperty(
        name=i18n.translate("Shot Name"),
        description=i18n.translate("Name of the shot to open")
    )
    
    def execute(self, context):
        try:
            # Get addon preferences
            prefs = get_addon_prefs()
            if not prefs:
                self.report({'ERROR'}, i18n.translate("Addon preferences not found"))
                return {'CANCELLED'}
            
            # Get project info
            project_path = context.scene.current_project
            if not project_path:
                self.report({'ERROR'}, i18n.translate("No project loaded"))
                return {'CANCELLED'}
            
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Get shot path
            if context.scene.project_settings.project_type == 'TEAM':
                shot_path = os.path.join(workspace_path, "SHOTS", self.shot_name)
                role_path = os.path.join(shot_path, context.scene.current_role or "MAIN")
                publish_path = os.path.join(role_path, "PUBLISH")
            else:
                shot_path = os.path.join(workspace_path, "SCENES", self.shot_name)
                publish_path = os.path.join(shot_path, "PUBLISH")
            
            if not os.path.exists(shot_path):
                self.report({'ERROR'}, i18n.translate("Shot not found: {}").format(self.shot_name))
                return {'CANCELLED'}
            
            # Save current file if needed
            if not save_current_file():
                self.report({'WARNING'}, i18n.translate("Current file not saved"))
            
            # Get publish file path
            role_name = context.scene.current_role or "MAIN"
            publish_file = f"{project_prefix}_{self.shot_name}_{role_name}.blend"
            publish_filepath = os.path.join(publish_path, publish_file)
            
            if not os.path.exists(publish_filepath):
                self.report({'ERROR'}, i18n.translate("Shot file not found: {}").format(publish_file))
                return {'CANCELLED'}
            
            # Check for WIP version
            should_redirect, wip_path = redirect_to_latest_wip(context, publish_filepath)
            
            if should_redirect and wip_path:
                # Open latest WIP
                bpy.ops.wm.open_mainfile(filepath=wip_path)
                context.scene.current_shot = self.shot_name
                self.report({'INFO'}, i18n.translate("Latest WIP opened: {}").format(os.path.basename(wip_path)))
            else:
                # Create first WIP if none exists
                wip_path = create_first_wip(context, publish_filepath)
                if wip_path:
                    bpy.ops.wm.open_mainfile(filepath=wip_path)
                    context.scene.current_shot = self.shot_name
                    self.report({'INFO'}, i18n.translate("First WIP created and opened: {}").format(os.path.basename(wip_path)))
                else:
                    self.report({'ERROR'}, i18n.translate("Error creating WIP version"))
                    return {'CANCELLED'}
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error opening shot: {}").format(str(e)))
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(ShotBrowserOperator)
    bpy.utils.register_class(OpenShotOperator)

def unregister():
    bpy.utils.unregister_class(OpenShotOperator)
    bpy.utils.unregister_class(ShotBrowserOperator)
