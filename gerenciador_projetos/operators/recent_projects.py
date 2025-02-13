import bpy
import os
from bpy.types import Operator
from ..i18n.translations import translate as i18n_translate

class OpenRecentProjectOperator(Operator):
    bl_idname = "project.open_recent"
    bl_label = "Abrir Projeto Recente"
    
    project_path: bpy.props.StringProperty()
    
    def execute(self, context):
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        
        if prefs.use_fixed_root:
            bpy.ops.project.load_project(selected_project=self.project_path)
        else:
            bpy.ops.project.load_project(project_path=self.project_path)
            
        return {'FINISHED'}

class PROJECTMANAGER_OT_clear_recent(Operator):
    """Clear recent projects list"""
    bl_idname = "project.clear_recent"
    bl_label = i18n_translate("Clear Recent Projects")
    bl_description = i18n_translate("Clear the list of recent projects")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            prefs.recent_projects.clear()
            self.report({'INFO'}, i18n_translate("Recent projects list cleared"))
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

def add_recent_project(context, project_path: str, project_name: str = ""):
    """Add a project to the recent projects list"""
    try:
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        
        # Remove if already exists
        for i, recent in enumerate(prefs.recent_projects):
            if recent.path == project_path:
                prefs.recent_projects.remove(i)
                break
        
        # Add to start of list
        recent = prefs.recent_projects.add()
        recent.path = project_path
        recent.name = project_name or project_path
        
        # Keep only last 10
        while len(prefs.recent_projects) > 10:
            prefs.recent_projects.remove(len(prefs.recent_projects) - 1)
            
    except Exception as e:
        print(f"Error adding recent project: {str(e)}")

def register():
    bpy.utils.register_class(OpenRecentProjectOperator)
    bpy.utils.register_class(PROJECTMANAGER_OT_clear_recent)

def unregister():
    bpy.utils.unregister_class(OpenRecentProjectOperator)
    bpy.utils.unregister_class(PROJECTMANAGER_OT_clear_recent)