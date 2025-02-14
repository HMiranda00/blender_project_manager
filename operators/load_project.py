import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty
from ..utils import get_project_info
from ..core.project_context import ProjectContextManager
from ..i18n.translations import translate as i18n_translate

class PROJECTMANAGER_OT_load_project(Operator):
    bl_idname = "project.load_project"
    bl_label = i18n_translate("Load Project")
    bl_description = i18n_translate("Load selected project")
    
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
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            
            # Get project path
            project_path = self.selected_project or self.project_path
            if not project_path:
                self.report({'ERROR'}, i18n_translate("No project selected"))
                return {'CANCELLED'}
            
            # Get project info
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Load or create project context
            ctx_manager = ProjectContextManager()
            ctx = ctx_manager.load(project_path)
            ctx.project_name = project_name
            ctx.project_prefix = project_prefix
            ctx.project_path = project_path
            ctx_manager.save(ctx)
            
            # Update scene properties
            context.scene.current_project = project_path
            context.scene.current_shot = ctx.current_shot
            context.scene.current_role = ctx.current_role
            
            # Add to recent projects
            from ..operators.recent_projects import add_recent_project
            add_recent_project(context, project_path, project_name)
            
            self.report({'INFO'}, i18n_translate("Project loaded: {}").format(project_name))
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n_translate("Error loading project: {}").format(str(e)))
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(PROJECTMANAGER_OT_load_project)

def unregister():
    bpy.utils.unregister_class(PROJECTMANAGER_OT_load_project)