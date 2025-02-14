"""
Project loading operator
"""
import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty
from ..utils.project_utils import get_addon_prefs
from ..utils import get_project_info
from ..utils.project_context import load_project_context
from .. import i18n

class LoadProjectOperator(Operator):
    """Load an existing project"""
    bl_idname = "project.load_project"
    bl_label = i18n.translate("Load Project")
    bl_description = i18n.translate("Load an existing project")
    
    filepath: StringProperty(
        name=i18n.translate("Project Path"),
        description=i18n.translate("Path to project folder"),
        subtype='DIR_PATH'
    )
    
    def execute(self, context):
        try:
            if not self.filepath:
                self.report({'ERROR'}, i18n.translate("No project path selected"))
                return {'CANCELLED'}
                
            # Normalize path
            project_path = os.path.normpath(self.filepath)
            
            # Load project context
            if load_project_context(project_path):
                self.report({'INFO'}, i18n.translate("Project loaded successfully"))
                return {'FINISHED'}
            else:
                # If no context file, just set the project path
                context.scene.current_project = project_path
                self.report({'INFO'}, i18n.translate("Project loaded (no context found)"))
                return {'FINISHED'}
                
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error loading project: {}").format(str(e)))
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(LoadProjectOperator)

def unregister():
    bpy.utils.unregister_class(LoadProjectOperator)
