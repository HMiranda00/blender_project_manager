import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from ..utils import get_project_info, get_publish_path, save_current_file

def get_wip_path(context, role_name):
    """Get the WIP path for the current role/shot"""
    try:
        if not (context.scene.current_project and context.scene.current_shot):
            return None
            
        project_path = context.scene.current_project
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot
        
        role_settings = None
        for role_mapping in prefs.role_mappings:
            if role_mapping.role_name == role_name:
                role_settings = role_mapping
                break
                
        if not role_settings:
            return None
            
        # Get WIP path
        wip_path = os.path.join(workspace_path, "SHOTS", shot_name, role_name, "WIP")
        os.makedirs(wip_path, exist_ok=True)
        
        return wip_path
        
    except Exception as e:
        print(f"Error getting WIP path: {str(e)}")
        return None

def get_latest_wip(context, role_name):
    """Get the latest WIP version"""
    try:
        wip_path = get_wip_path(context, role_name)
        if not wip_path:
            return None, 0
            
        project_path = context.scene.current_project
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot
        
        # Find latest version
        latest_version = 0
        latest_file = None
        
        for file in os.listdir(wip_path):
            if file.endswith(".blend"):
                try:
                    # Extract version number from filename
                    version = int(file.split("_v")[-1].split(".")[0])
                    if version > latest_version:
                        latest_version = version
                        latest_file = file
                except ValueError:
                    continue
        
        if latest_file:
            return os.path.join(wip_path, latest_file), latest_version
        
        return None, 0
        
    except Exception as e:
        print(f"Error getting latest WIP: {str(e)}")
        return None, 0

def create_or_update_publish(context, role_name):
    """Create or update the publish file by copying the latest WIP"""
    try:
        if not (context.scene.current_project and context.scene.current_shot):
            return None
            
        # Get latest WIP
        latest_wip, version = get_latest_wip(context, role_name)
        if not latest_wip:
            return None
            
        # Get publish path
        project_path = context.scene.current_project
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot
        
        role_settings = None
        for role_mapping in prefs.role_mappings:
            if role_mapping.role_name == role_name:
                role_settings = role_mapping
                break
                
        if not role_settings:
            return None
            
        publish_path = get_publish_path(
            role_settings.publish_path_preset,
            role_settings,
            context,
            project_path,
            project_name,
            shot_name,
            asset_name=role_name
        )
        
        # Create publish file
        os.makedirs(publish_path, exist_ok=True)
        publish_file = os.path.join(publish_path, f"{project_prefix}_{shot_name}_{role_name}.blend")
        
        # Copy latest WIP to publish
        import shutil
        shutil.copy2(latest_wip, publish_file)
        
        return publish_file
        
    except Exception as e:
        print(f"Error creating/updating publish: {str(e)}")
        return None

class VERSION_OT_new_wip_version(Operator):
    """Create a new WIP version"""
    bl_idname = "project.new_wip_version"
    bl_label = "New WIP Version"
    bl_description = "Create a new WIP version of the current file"
    
    role_name: StringProperty()
    update_publish: BoolProperty(
        name="Update Publish",
        description="Update the publish file with this version",
        default=True
    )
    
    def execute(self, context):
        try:
            if not (context.scene.current_project and context.scene.current_shot and context.scene.current_role):
                self.report({'ERROR'}, "No project, shot or role selected")
                return {'CANCELLED'}
            
            role_name = context.scene.current_role
            
            # Get WIP path
            wip_path = get_wip_path(context, role_name)
            if not wip_path:
                self.report({'ERROR'}, "Could not get WIP path")
                return {'CANCELLED'}
            
            # Get project info
            project_path = context.scene.current_project
            prefs = context.preferences.addons['blender_project_manager'].preferences
            project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            shot_name = context.scene.current_shot
            
            # Get latest version
            _, latest_version = get_latest_wip(context, role_name)
            
            # Create new version
            new_version = latest_version + 1
            new_file = os.path.join(wip_path, f"{project_prefix}_{shot_name}_{role_name}_v{new_version:03d}.blend")
            
            # Save as new version
            bpy.ops.wm.save_as_mainfile(filepath=new_file)
            
            # Update publish
            publish_file = create_or_update_publish(context, role_name)
            if not publish_file:
                self.report({'WARNING'}, "Could not update publish file")
            
            self.report({'INFO'}, f"Created WIP version {new_version}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error creating new version: {str(e)}")
            return {'CANCELLED'}

class VERSION_OT_open_latest_wip(Operator):
    """Open the latest WIP version"""
    bl_idname = "project.open_latest_wip"
    bl_label = "Open Latest WIP"
    bl_description = "Open the latest WIP version of the current role"
    
    def execute(self, context):
        try:
            if not (context.scene.current_project and context.scene.current_shot and context.scene.current_role):
                self.report({'ERROR'}, "No project, shot or role selected")
                return {'CANCELLED'}
            
            role_name = context.scene.current_role
            
            # Get latest WIP
            latest_wip, version = get_latest_wip(context, role_name)
            if not latest_wip:
                # Create first version if none exists
                wip_path = get_wip_path(context, role_name)
                if not wip_path:
                    self.report({'ERROR'}, "Could not get WIP path")
                    return {'CANCELLED'}
                
                project_path = context.scene.current_project
                prefs = context.preferences.addons['blender_project_manager'].preferences
                project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
                shot_name = context.scene.current_shot
                
                latest_wip = os.path.join(wip_path, f"{project_prefix}_{shot_name}_{role_name}_v001.blend")
                bpy.ops.wm.save_as_mainfile(filepath=latest_wip)
                
                # Create initial publish
                publish_file = create_or_update_publish(context, role_name)
                if not publish_file:
                    self.report({'WARNING'}, "Could not create publish file")
                
                self.report({'INFO'}, "Created first WIP version")
            else:
                # Open latest version
                save_current_file()
                bpy.ops.wm.open_mainfile(filepath=latest_wip)
                self.report({'INFO'}, f"Opened WIP version {version}")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error opening latest WIP: {str(e)}")
            return {'CANCELLED'}

class VERSION_OT_publish(Operator):
    bl_idname = "project.publish_version"
    bl_label = "Publish Version"
    bl_description = "Create a publish version from the current WIP"
    
    def execute(self, context):
        try:
            if not (context.scene.current_project and context.scene.current_shot and context.scene.current_role):
                self.report({'ERROR'}, "No project, shot or role selected")
                return {'CANCELLED'}
            
            role_name = context.scene.current_role
            
            # Save current file first
            save_current_file()
            
            # Create publish
            publish_file = create_or_update_publish(context, role_name)
            if not publish_file:
                self.report({'ERROR'}, "Could not create publish file")
                return {'CANCELLED'}
            
            self.report({'INFO'}, f"Published file created: {os.path.basename(publish_file)}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error publishing version: {str(e)}")
            return {'CANCELLED'}

# Registration
classes = (
    VERSION_OT_new_wip_version,
    VERSION_OT_open_latest_wip,
    VERSION_OT_publish,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls) 