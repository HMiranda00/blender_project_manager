import bpy
import os
import re
from bpy.types import Operator
from bpy.props import StringProperty
from ..utils import get_project_info, create_project_structure, save_current_file

class CreateProjectOperator(Operator):
    bl_idname = "project.create_project"
    bl_label = "Create New Project"

    project_name: StringProperty(
        name="Project Name",
        description="Name of the new project",
        default=""
    )
    
    project_path: StringProperty(
        name="Project Folder",
        description="Select the project folder",
        subtype='DIR_PATH',
        default=""
    )
    
    def check_preferences(self, context):
        prefs = context.preferences.addons['blender_project_manager'].preferences
        missing = []
        
        if prefs.use_fixed_root:
            if not prefs.fixed_root_path:
                missing.append("Fixed Root Path")
        return missing

    def execute(self, context):
        try:
            prefs = context.preferences.addons['blender_project_manager'].preferences
            
            if prefs.use_fixed_root:
                if not self.project_name:
                    self.report({'ERROR'}, "Project name cannot be empty")
                    return {'CANCELLED'}
                
                root_path = bpy.path.abspath(prefs.fixed_root_path)
                
                # Find next project number
                existing_projects = [
                    d for d in os.listdir(root_path) 
                    if os.path.isdir(os.path.join(root_path, d))
                ]
                project_numbers = []
                for d in existing_projects:
                    match = re.match(r'^(\d+)\s*-\s*', d)
                    if match:
                        project_numbers.append(int(match.group(1)))
                next_number = max(project_numbers, default=0) + 1
                
                # Create project folder name: "003 - Project Name"
                project_folder_name = f"{next_number:03d} - {self.project_name}"
                project_path = os.path.join(root_path, project_folder_name)
                
                # Create project folder
                os.makedirs(project_path, exist_ok=True)
                
                # Create workspace folder: always "03 - 3D"
                workspace_folder = "03 - 3D"
                workspace_path = os.path.join(project_path, workspace_folder)
                
                # Create project structure directly in 03 - 3D folder
                os.makedirs(workspace_path, exist_ok=True)
                create_project_structure(workspace_path)
                
            else:
                if not self.project_path:
                    self.report({'ERROR'}, "Select a valid project folder")
                    return {'CANCELLED'}
                project_path = bpy.path.abspath(self.project_path)
                
                if not os.path.exists(os.path.dirname(project_path)):
                    self.report({'ERROR'}, "Project path does not exist")
                    return {'CANCELLED'}
                
                workspace_path = os.path.join(project_path, "3D")
                os.makedirs(workspace_path, exist_ok=True)
                create_project_structure(workspace_path)
            
            # Define current project
            context.scene.current_project = project_path

            # Configure Asset Browser automatically
            try:
                bpy.ops.project.setup_asset_browser()
            except Exception as e:
                self.report({'WARNING'}, f"Project created, but there was an error configuring the Asset Browser: {str(e)}")
                return {'FINISHED'}

            self.report({'INFO'}, f"Project created: {os.path.basename(project_path)}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error creating project: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        save_current_file()
        
        missing_prefs = self.check_preferences(context)
        if missing_prefs:
            self.report({'ERROR'}, f"Configure the following preferences first: {', '.join(missing_prefs)}")
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
            return {'CANCELLED'}
            
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons['blender_project_manager'].preferences
        
        if prefs.use_fixed_root:
            layout.prop(self, "project_name")
            layout.label(text=f"Fixed Root Path: {prefs.fixed_root_path}")
        else:
            layout.prop(self, "project_path")

def register():
    bpy.utils.register_class(CreateProjectOperator)

def unregister():
    bpy.utils.unregister_class(CreateProjectOperator)