"""
Open role file operator
"""
import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty, BoolProperty
from ..utils.project_utils import get_addon_prefs, save_current_file
from ..utils import get_project_info
from ..utils.versioning import redirect_to_latest_wip, create_first_wip
from .. import i18n

class OpenRoleFileOperator(Operator):
    bl_idname = "project.open_role_file"
    bl_label = i18n.translate("Open Role File")
    bl_description = i18n.translate("Open role file for current shot")
    
    def get_roles(self, context):
        """List all configured roles"""
        try:
            prefs = get_addon_prefs()
            if not prefs:
                return [('NONE', i18n.translate("No addon preferences"), "", 'ERROR', 0)]
                
            return [(rm.role_name, rm.role_name, rm.description, rm.icon, i) 
                    for i, rm in enumerate(prefs.role_mappings)]
        except Exception as e:
            print(f"Error listing roles: {str(e)}")
            return [('NONE', i18n.translate("Error listing roles"), "", 'ERROR', 0)]
    
    selected_role: EnumProperty(
        name=i18n.translate("Role"),
        description=i18n.translate("Select role to open"),
        items=get_roles
    )
    
    def execute(self, context):
        try:
            # Get addon preferences
            prefs = get_addon_prefs()
            if not prefs:
                self.report({'ERROR'}, i18n.translate("Addon preferences not found"))
                return {'CANCELLED'}
            
            # Validate role
            if not self.selected_role or self.selected_role == 'NONE':
                self.report({'ERROR'}, i18n.translate("Select a valid role"))
                return {'CANCELLED'}
            
            # Get project info
            project_path = context.scene.current_project
            if not project_path:
                self.report({'ERROR'}, i18n.translate("No project loaded"))
                return {'CANCELLED'}
            
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Get current shot
            if not context.scene.current_shot:
                self.report({'ERROR'}, i18n.translate("No shot selected"))
                return {'CANCELLED'}
            
            # Get role path
            if context.scene.project_settings.project_type == 'TEAM':
                shot_path = os.path.join(workspace_path, "SHOTS", context.scene.current_shot)
                role_path = os.path.join(shot_path, self.selected_role)
                publish_path = os.path.join(role_path, "PUBLISH")
                wip_path = os.path.join(role_path, "_WIP")
            else:
                shot_path = os.path.join(workspace_path, "SCENES", context.scene.current_shot)
                publish_path = os.path.join(shot_path, "PUBLISH")
                wip_path = os.path.join(shot_path, "_WIP")
            
            # Get publish file path
            publish_file = f"{project_prefix}_{context.scene.current_shot}_{self.selected_role}.blend"
            publish_filepath = os.path.join(publish_path, publish_file)
            
            # Check if publish exists
            if not os.path.exists(publish_filepath):
                self.report({'ERROR'}, i18n.translate("Role file not found: {}").format(publish_filepath))
                return {'CANCELLED'}
            
            # Save current file if needed
            if not save_current_file():
                self.report({'WARNING'}, i18n.translate("Current file not saved"))
            
            # Check for WIP version
            should_redirect, wip_path = redirect_to_latest_wip(context, publish_filepath)
            
            if should_redirect and wip_path:
                # Open latest WIP
                bpy.ops.wm.open_mainfile(filepath=wip_path)
                context.scene.current_role = self.selected_role
                self.report({'INFO'}, i18n.translate("Latest WIP opened: {}").format(os.path.basename(wip_path)))
            else:
                # Create first WIP if none exists
                wip_path = create_first_wip(context, publish_filepath)
                if wip_path:
                    bpy.ops.wm.open_mainfile(filepath=wip_path)
                    context.scene.current_role = self.selected_role
                    self.report({'INFO'}, i18n.translate("First WIP created and opened: {}").format(os.path.basename(wip_path)))
                else:
                    self.report({'ERROR'}, i18n.translate("Error creating WIP version"))
                    return {'CANCELLED'}
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error opening role file: {}").format(str(e)))
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        if not context.scene.current_project:
            self.report({'ERROR'}, i18n.translate("Select a project first"))
            return {'CANCELLED'}
        
        if not context.scene.current_shot:
            self.report({'ERROR'}, i18n.translate("Select a shot first"))
            return {'CANCELLED'}
        
        prefs = get_addon_prefs()
        if not prefs or not prefs.role_mappings:
            self.report({'ERROR'}, i18n.translate("Configure at least one role in addon preferences"))
            return {'CANCELLED'}
        
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        # Show current project and shot
        box = layout.box()
        box.label(text=i18n.translate("Current Project:"), icon='FILE_FOLDER')
        prefs = get_addon_prefs()
        project_name, _, _ = get_project_info(context.scene.current_project, prefs.use_fixed_root)
        box.label(text=project_name)
        
        box = layout.box()
        box.label(text=i18n.translate("Current Shot:"), icon='SEQUENCE')
        box.label(text=context.scene.current_shot)
        
        # Role selection
        layout.prop(self, "selected_role")

def register():
    bpy.utils.register_class(OpenRoleFileOperator)

def unregister():
    bpy.utils.unregister_class(OpenRoleFileOperator)
