"""
Recent projects operators
"""
import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty, BoolProperty
from ..utils.project_utils import get_addon_prefs, save_current_file
from ..utils import get_project_info
from .. import i18n

def add_recent_project(context, project_path, project_name):
    """Add a project to the recent projects list"""
    try:
        prefs = get_addon_prefs()
        if not prefs:
            return
        
        # Remove if already exists
        for i, recent in enumerate(prefs.recent_projects):
            if recent.path == project_path:
                prefs.recent_projects.remove(i)
                break
        
        # Add to beginning
        recent = prefs.recent_projects.add()
        recent.name = project_name
        recent.path = project_path
        
        # Keep only last 10
        while len(prefs.recent_projects) > 10:
            prefs.recent_projects.remove(len(prefs.recent_projects) - 1)
            
    except Exception as e:
        print(f"Error adding recent project: {str(e)}")

class OpenRecentProjectOperator(Operator):
    bl_idname = "project.open_recent"
    bl_label = i18n.translate("Open Recent Project")
    
    def get_recent_projects(self, context):
        """List recent projects"""
        try:
            prefs = get_addon_prefs()
            if not prefs:
                return [('NONE', i18n.translate("No addon preferences"), "", 'ERROR', 0)]
                
            items = []
            for i, recent in enumerate(prefs.recent_projects):
                if os.path.exists(recent.path):
                    items.append((
                        recent.path,
                        recent.name,
                        recent.path,
                        'FILE_FOLDER',
                        i
                    ))
            
            if not items:
                return [('NONE', i18n.translate("No recent projects"), "", 'ERROR', 0)]
                
            return items
            
        except Exception as e:
            print(f"Error listing recent projects: {str(e)}")
            return [('NONE', i18n.translate("Error listing recent projects"), "", 'ERROR', 0)]
    
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
                self.report({'ERROR'}, i18n.translate("Addon preferences not found. Make sure the addon is enabled."))
                return {'CANCELLED'}
            
            # Validate project
            if not self.selected_project or self.selected_project == 'NONE':
                self.report({'ERROR'}, i18n.translate("Select a valid project"))
                return {'CANCELLED'}
            
            # Save current file if needed
            if not save_current_file():
                self.report({'WARNING'}, i18n.translate("Current file not saved"))
            
            # Load project
            project_path = self.selected_project
            if not os.path.exists(project_path):
                self.report({'ERROR'}, i18n.translate("Project path does not exist: {}").format(project_path))
                return {'CANCELLED'}
            
            # Get project info
            project_name, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
            
            # Set current project
            context.scene.current_project = project_path
            
            # Setup Asset Browser
            bpy.ops.project.setup_asset_browser(link_type='LINK')
            
            self.report({'INFO'}, i18n.translate("Project loaded: {}").format(project_name))
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

class ClearRecentProjectsOperator(Operator):
    bl_idname = "project.clear_recent"
    bl_label = i18n.translate("Clear Recent Projects")
    bl_description = i18n.translate("Clear the list of recent projects")
    
    def execute(self, context):
        try:
            # Get addon preferences
            prefs = get_addon_prefs()
            if not prefs:
                self.report({'ERROR'}, i18n.translate("Addon preferences not found. Make sure the addon is enabled."))
                return {'CANCELLED'}
            
            # Clear recent projects
            prefs.recent_projects.clear()
            
            self.report({'INFO'}, i18n.translate("Recent projects list cleared"))
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error clearing recent projects: {}").format(str(e)))
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(OpenRecentProjectOperator)
    bpy.utils.register_class(ClearRecentProjectsOperator)

def unregister():
    bpy.utils.unregister_class(ClearRecentProjectsOperator)
    bpy.utils.unregister_class(OpenRecentProjectOperator)
