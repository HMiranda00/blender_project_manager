"""
Project creation operator
"""
import bpy
import os
import re
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from ..utils.project_utils import get_addon_prefs, create_project_structure
from ..utils import get_project_info
from ..utils.project_context import save_project_context
from .. import i18n

class CreateProjectOperator(Operator, ImportHelper):
    """Create a new project"""
    bl_idname = "project.create_project"
    bl_label = i18n.translate("Create Project")
    bl_description = i18n.translate("Create a new project")
    
    filename_ext = ""
    use_filter_folder = True
    
    project_type: EnumProperty(
        name=i18n.translate("Project Type"),
        items=[
            ('TEAM', i18n.translate("Team"), i18n.translate("Project with multiple roles and assembly"), 'COMMUNITY', 0),
            ('SOLO', i18n.translate("Solo"), i18n.translate("Simplified individual project"), 'PERSON', 1)
        ],
        default='TEAM'
    )
    
    def execute(self, context):
        try:
            # Get addon preferences
            prefs = get_addon_prefs()
            if not prefs:
                self.report({'ERROR'}, i18n.translate("Addon preferences not found"))
                return {'CANCELLED'}
            
            # Get absolute path
            project_path = os.path.dirname(bpy.path.abspath(self.filepath))
            
            # Create project folder
            os.makedirs(project_path, exist_ok=True)
            
            # Create workspace path
            workspace_path = os.path.join(project_path, "3D")
            os.makedirs(workspace_path, exist_ok=True)
            
            # Get project info
            project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Create project structure
            create_project_structure(workspace_path, project_prefix, self.project_type)
            
            # Set project settings
            context.scene.current_project = project_path
            context.scene.project_settings.project_type = self.project_type
            context.scene.project_settings.asset_linking = 'LINK'
            context.scene.project_settings.use_versioning = True
            
            # Save context
            if save_project_context():
                self.report({'INFO'}, i18n.translate("Project created and context saved"))
            else:
                self.report({'WARNING'}, i18n.translate("Project created but context not saved"))
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error creating project: {}").format(str(e)))
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        # Get addon preferences
        prefs = get_addon_prefs()
        if not prefs:
            self.report({'ERROR'}, i18n.translate("Addon preferences not found"))
            return {'CANCELLED'}
        
        if prefs.use_fixed_root:
            if not prefs.fixed_root_path:
                self.report({'ERROR'}, i18n.translate("Fixed root path not configured"))
                return {'CANCELLED'}
            
            # Get next project number
            root_path = bpy.path.abspath(prefs.fixed_root_path)
            project_numbers = []
            for d in os.listdir(root_path):
                if os.path.isdir(os.path.join(root_path, d)):
                    match = re.match(r'^(\d+)\s*-\s*', d)
                    if match:
                        project_numbers.append(int(match.group(1)))
            next_number = max(project_numbers, default=0) + 1
            
            # Show dialog to get project name
            return context.window_manager.invoke_props_dialog(self)
        else:
            # Show file browser
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
    
    def draw(self, context):
        layout = self.layout
        
        prefs = get_addon_prefs()
        if prefs and prefs.use_fixed_root:
            # Show fixed root path
            box = layout.box()
            box.label(text=i18n.translate("Root Folder:"))
            box.label(text=prefs.fixed_root_path)
            
            # Project name input
            layout.prop(self, "project_name")
        
        # Project type
        box = layout.box()
        box.label(text=i18n.translate("Project Settings:"), icon='SETTINGS')
        box.prop(self, "project_type", expand=True)

def register():
    bpy.utils.register_class(CreateProjectOperator)

def unregister():
    bpy.utils.unregister_class(CreateProjectOperator)
