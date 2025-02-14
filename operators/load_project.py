import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
import os
from ..utils import get_project_info
from ..core.project_context import ProjectContextManager
from ..i18n.translations import translate as i18n_translate

class PROJECT_OT_load_project(Operator, ImportHelper):
    """Load an existing project"""
    bl_idname = "project.load_project"
    bl_label = "Load Project"
    
    filename_ext = ""
    use_filter_folder = True
    
    project_path: StringProperty(
        name=i18n_translate("Project Path"),
        description=i18n_translate("Path to project folder"),
        default="",
        subtype='DIR_PATH'
    )
    
    selected_project: StringProperty(
        name=i18n_translate("Selected Project"),
        description=i18n_translate("Selected project from list"),
        default=""
    )
    
    def execute(self, context):
        try:
            filepath = self.filepath
            
            if not os.path.exists(filepath):
                self.report({'ERROR'}, "Selected path does not exist")
                return {'CANCELLED'}
            
            # Set current project
            context.scene.current_project = filepath
            
            # Update project type safely using the new operator
            bpy.ops.project.update_project_type()
            
            # Add to recent projects
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            prefs.add_recent_project(filepath)
            
            return {'FINISHED'}
            
        except Exception as e:
            print(f"Error loading project: {str(e)}")
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(PROJECT_OT_load_project)

def unregister():
    bpy.utils.unregister_class(PROJECT_OT_load_project)