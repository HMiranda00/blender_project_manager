import bpy
import os
from bpy.types import Operator
from ...utils import get_project_info, save_current_file
from .utils import get_assembly_path

class ASSEMBLY_OT_open(Operator):
    """Open the assembly file"""
    bl_idname = "project.open_assembly"
    bl_label = "Open Assembly"
    bl_description = "Open the assembly file for the current shot"
    
    def execute(self, context):
        try:
            if not (context.scene.current_project and context.scene.current_shot):
                self.report({'ERROR'}, "No project or shot selected")
                return {'CANCELLED'}
            
            # Get project info
            project_path = context.scene.current_project
            prefs = context.preferences.addons['blender_project_manager'].preferences
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            shot_name = context.scene.current_shot
            
            # Save current file path to return later
            if bpy.data.is_saved:
                context.scene.previous_file = bpy.data.filepath
            
            # Get assembly file path
            assembly_path = get_assembly_path(context, shot_name)
            
            # Save current file before opening assembly
            save_current_file()
            
            # Store current context
            current_project = context.scene.current_project
            current_shot = context.scene.current_shot
            current_role = context.scene.current_role
            
            # Create new file if assembly doesn't exist
            if not os.path.exists(assembly_path):
                bpy.ops.wm.read_homefile(app_template="")
                context.scene.name = shot_name
                bpy.ops.wm.save_as_mainfile(filepath=assembly_path)
            
            # Open assembly file
            bpy.ops.wm.open_mainfile(filepath=assembly_path)
            
            # Restore context
            context.scene.current_project = current_project
            context.scene.current_shot = current_shot
            context.scene.current_role = current_role
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error opening assembly: {str(e)}")
            return {'CANCELLED'}

class ASSEMBLY_OT_open_directory(Operator):
    """Open current file directory"""
    bl_idname = "project.open_current_directory"
    bl_label = "Open File Directory"
    bl_description = "Open the directory of the current file in system's file explorer"
    
    def execute(self, context):
        try:
            filepath = bpy.data.filepath
            if not filepath:
                self.report({'ERROR'}, "No file is currently open")
                return {'CANCELLED'}
                
            directory = os.path.dirname(filepath)
            if not os.path.exists(directory):
                self.report({'ERROR'}, "Directory not found")
                return {'CANCELLED'}
                
            if os.name == 'nt':
                os.startfile(directory)
            else:
                import subprocess
                subprocess.Popen(['xdg-open', directory])
                
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error opening directory: {str(e)}")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(ASSEMBLY_OT_open)
    bpy.utils.register_class(ASSEMBLY_OT_open_directory)

def unregister():
    bpy.utils.unregister_class(ASSEMBLY_OT_open_directory)
    bpy.utils.unregister_class(ASSEMBLY_OT_open) 