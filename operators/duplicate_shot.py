"""
Shot duplication operator
"""
import bpy
import os
import shutil
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty, BoolProperty
from ..utils.project_utils import get_addon_prefs, save_current_file
from ..utils import get_project_info
from .. import i18n

class DuplicateShotOperator(Operator):
    bl_idname = "project.duplicate_shot"
    bl_label = i18n.translate("Duplicate Shot")
    
    source_shot: StringProperty(
        name=i18n.translate("Source Shot"),
        description=i18n.translate("Shot to duplicate")
    )
    
    target_shot: StringProperty(
        name=i18n.translate("Target Shot"),
        description=i18n.translate("Name for the new shot")
    )
    
    def execute(self, context):
        try:
            # Get addon preferences
            prefs = get_addon_prefs()
            if not prefs:
                self.report({'ERROR'}, i18n.translate("Addon preferences not found. Make sure the addon is enabled."))
                return {'CANCELLED'}
            
            # Validate shots
            if not self.source_shot:
                self.report({'ERROR'}, i18n.translate("Source shot cannot be empty"))
                return {'CANCELLED'}
                
            if not self.target_shot:
                self.report({'ERROR'}, i18n.translate("Target shot cannot be empty"))
                return {'CANCELLED'}
            
            # Get project info
            project_path = context.scene.current_project
            if not project_path:
                self.report({'ERROR'}, i18n.translate("No project loaded"))
                return {'CANCELLED'}
            
            project_name, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
            
            # Get shot paths
            source_path = os.path.join(workspace_path, "SHOTS", self.source_shot)
            target_path = os.path.join(workspace_path, "SHOTS", self.target_shot)
            
            # Check if source exists
            if not os.path.exists(source_path):
                self.report({'ERROR'}, i18n.translate("Source shot not found: {}").format(self.source_shot))
                return {'CANCELLED'}
            
            # Check if target already exists
            if os.path.exists(target_path):
                self.report({'ERROR'}, i18n.translate("Target shot already exists: {}").format(self.target_shot))
                return {'CANCELLED'}
            
            # Copy shot folder
            shutil.copytree(source_path, target_path)
            
            # Rename files in WIP and PUBLISH folders
            for folder in ["WIP", "PUBLISH"]:
                folder_path = os.path.join(target_path, folder)
                if os.path.exists(folder_path):
                    for file in os.listdir(folder_path):
                        if file.startswith(self.source_shot):
                            old_path = os.path.join(folder_path, file)
                            new_path = os.path.join(folder_path, file.replace(self.source_shot, self.target_shot))
                            os.rename(old_path, new_path)
            
            self.report({'INFO'}, i18n.translate("Shot duplicated: {} -> {}").format(self.source_shot, self.target_shot))
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error duplicating shot: {}").format(str(e)))
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        if not context.scene.current_project:
            self.report({'ERROR'}, i18n.translate("Select a project first"))
            return {'CANCELLED'}
        
        # If called from a shot, use it as source
        if context.scene.current_shot:
            self.source_shot = context.scene.current_shot
        
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        # Show current project
        box = layout.box()
        box.label(text=i18n.translate("Current Project:"), icon='FILE_FOLDER')
        prefs = get_addon_prefs()
        project_name, _, _ = get_project_info(context.scene.current_project, prefs.use_fixed_root)
        box.label(text=project_name)
        
        # Shot selection
        layout.prop(self, "source_shot")
        layout.prop(self, "target_shot")

def register():
    bpy.utils.register_class(DuplicateShotOperator)

def unregister():
    bpy.utils.unregister_class(DuplicateShotOperator) 
