import bpy
import os
from bpy.types import Operator
from bpy.props import EnumProperty
from ..utils import get_project_info, save_current_file
from ..utils.version_control import get_latest_wip, create_first_wip

class OpenShotOperator(Operator):
    bl_idname = "project.open_shot"
    bl_label = "Open Shot"
    bl_description = "Open an existing shot from the project"

    def get_shots(self, context):
        items = []
        
        if not context.scene.current_project:
            return items

        try:
            project_path = context.scene.current_project
            prefs = context.preferences.addons['blender_project_manager'].preferences
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Path to SHOTS folder
            shots_path = os.path.join(workspace_path, "SHOTS")
            if not os.path.exists(shots_path):
                return items

            # List all shots
            shot_folders = [d for d in os.listdir(shots_path) if os.path.isdir(os.path.join(shots_path, d))]
            shot_folders.sort()

            for shot in shot_folders:
                items.append((shot, shot, f"Open {shot}"))

        except Exception as e:
            print(f"[DEBUG] Error listing shots: {str(e)}")

        return items

    def get_roles(self, context):
        prefs = context.preferences.addons['blender_project_manager'].preferences
        return [(rm.role_name, rm.role_name, rm.description, rm.icon, i)
                for i, rm in enumerate(prefs.role_mappings)]

    selected_shot: EnumProperty(
        name="Shot",
        description="Select shot to open",
        items=get_shots
    )

    selected_role: EnumProperty(
        name="Role",
        description="Select role to open",
        items=get_roles
    )

    def execute(self, context):
        try:
            save_current_file()
            
            # Set current shot and role
            context.scene.current_shot = self.selected_shot
            context.scene.current_role = self.selected_role
            
            print(f"\n[DEBUG] Opening shot {self.selected_shot} with role {self.selected_role}")
            print(f"Project: {context.scene.current_project}")
            
            # Try to get latest WIP
            wip_file, version = get_latest_wip(context, self.selected_role)
            
            if not wip_file:
                print("[DEBUG] No existing WIP found, creating first one")
                # If no WIP exists, create first one
                wip_file = create_first_wip(context, self.selected_role)
                if not wip_file:
                    self.report({'ERROR'}, f"Error creating WIP file for {self.selected_role}")
                    return {'CANCELLED'}
            else:
                print(f"[DEBUG] Found existing WIP v{version:03d}: {wip_file}")
            
            # Open the WIP file
            print(f"[DEBUG] Opening file: {wip_file}")
            bpy.ops.wm.open_mainfile(filepath=wip_file)
            
            # Restore context
            context.scene.current_project = context.scene.current_project
            context.scene.current_shot = self.selected_shot
            context.scene.current_role = self.selected_role
            
            self.report({'INFO'}, f"Opened {self.selected_role} for shot {self.selected_shot} (WIP v{version:03d})")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Error opening shot: {str(e)}")
            print(f"[DEBUG] Error details: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        if not context.scene.current_project:
            self.report({'ERROR'}, "Select a project first")
            return {'CANCELLED'}
            
        # Check if there are any roles configured
        prefs = context.preferences.addons['blender_project_manager'].preferences
        if not prefs.role_mappings:
            self.report({'ERROR'}, "Configure at least one role in addon preferences")
            return {'CANCELLED'}
            
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "selected_shot")
        layout.prop(self, "selected_role")

def register():
    bpy.utils.register_class(OpenShotOperator)

def unregister():
    bpy.utils.unregister_class(OpenShotOperator)