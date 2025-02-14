"""
Open recent project operator
"""
import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty
from ..utils.project_utils import get_addon_prefs, save_current_file
from .. import i18n

class OpenRecentProjectOperator(Operator):
    bl_idname = "project.open_recent"
    bl_label = i18n.translate("Open Recent Project")
    bl_description = i18n.translate("Open a recent project")
    
    def get_recent_projects(self, context):
        """List recent projects"""
        try:
            prefs = get_addon_prefs()
            if not prefs:
                return [('NONE', i18n.translate("No addon preferences"), "", 'ERROR', 0)]
                
            items = []
            for i, project in enumerate(prefs.recent_projects):
                name = project.name if project.name else os.path.basename(os.path.dirname(project.path))
                items.append((project.path, name, project.path, 'FILE_FOLDER', i))
            return items or [('NONE', i18n.translate("No recent projects"), "", 'ERROR', 0)]
            
        except Exception as e:
            print(f"Error listing recent projects: {str(e)}")
            return [('NONE', i18n.translate("Error listing projects"), "", 'ERROR', 0)]
    
    selected_project: EnumProperty(
        name=i18n.translate("Recent Projects"),
        description=i18n.translate("Select a recent project to open"),
        items=get_recent_projects
    )
    
    def execute(self, context):
        try:
            # Get addon preferences
            prefs = get_addon_prefs()
            if not prefs:
                self.report({'ERROR'}, i18n.translate("Addon preferences not found"))
                return {'CANCELLED'}
            
            # Validate project
            if not self.selected_project or self.selected_project == 'NONE':
                self.report({'ERROR'}, i18n.translate("Select a valid project"))
                return {'CANCELLED'}
            
            # Check if project exists
            if not os.path.exists(self.selected_project):
                self.report({'ERROR'}, i18n.translate("Project not found: {}").format(self.selected_project))
                return {'CANCELLED'}
            
            # Save current file if needed
            if not save_current_file():
                self.report({'WARNING'}, i18n.translate("Current file not saved"))
            
            # Update context
            context.scene.current_project = self.selected_project
            
            self.report({'INFO'}, i18n.translate("Project loaded: {}").format(self.selected_project))
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error opening project: {}").format(str(e)))
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        prefs = get_addon_prefs()
        if not prefs or not prefs.recent_projects:
            self.report({'ERROR'}, i18n.translate("No recent projects found"))
            return {'CANCELLED'}
        
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "selected_project")

def register():
    bpy.utils.register_class(OpenRecentProjectOperator)

def unregister():
    bpy.utils.unregister_class(OpenRecentProjectOperator) 