import bpy
import os
from .core import get_project_info, get_publish_path

def get_wip_path(context, role_name):
    """Get the WIP path for the current role/shot"""
    try:
        if not (context.scene.current_project and context.scene.current_shot):
            return None
            
        project_path = context.scene.current_project
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot
        
        # Get WIP path
        wip_path = os.path.join(workspace_path, "SHOTS", shot_name, role_name, "WIP")
        os.makedirs(wip_path, exist_ok=True)
        
        return wip_path
        
    except Exception as e:
        print(f"Error getting WIP path: {str(e)}")
        return None

def get_latest_wip(context, role_name):
    """Get the latest WIP version for the current role"""
    try:
        wip_path = get_wip_path(context, role_name)
        if not wip_path:
            return None, 0
            
        project_path = context.scene.current_project
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot
        
        # Pattern: prefix_shot_role_v###.blend
        wip_pattern = f"{project_prefix}_{shot_name}_{role_name}_v"
        
        # Find all WIP files
        latest_version = 0
        latest_file = None
        
        print(f"\n[DEBUG] Searching for WIP files in: {wip_path}")
        print(f"Pattern: {wip_pattern}")
        
        for file in os.listdir(wip_path):
            if file.startswith(wip_pattern) and file.endswith(".blend"):
                try:
                    # Extract version number
                    version = int(file.split("_v")[-1].split(".")[0])
                    print(f"Found WIP: {file} (v{version:03d})")
                    
                    if version > latest_version:
                        latest_version = version
                        latest_file = os.path.join(wip_path, file)
                        
                except (ValueError, IndexError):
                    continue
        
        if latest_file:
            print(f"Latest WIP: v{latest_version:03d}")
            return latest_file, latest_version
            
        print("No WIP files found")
        return None, 0
        
    except Exception as e:
        print(f"Error getting latest WIP: {str(e)}")
        return None, 0

def create_first_wip(context, role_name):
    """Create the first WIP version and its PUBLISH"""
    try:
        if not (context.scene.current_project and context.scene.current_shot):
            return None
            
        project_path = context.scene.current_project
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot
        
        # Get WIP path
        wip_path = get_wip_path(context, role_name)
        if not wip_path:
            return None
            
        # Create first WIP version
        wip_file = os.path.join(wip_path, f"{project_prefix}_{shot_name}_{role_name}_v001.blend")
        bpy.ops.wm.save_as_mainfile(filepath=wip_file)
        
        # Get role settings
        role_settings = None
        for role_mapping in prefs.role_mappings:
            if role_mapping.role_name == role_name:
                role_settings = role_mapping
                break
                
        if not role_settings:
            return None
            
        # Create PUBLISH
        publish_path = get_publish_path(
            role_settings.publish_path_preset,
            role_settings,
            context,
            project_path,
            project_name,
            shot_name,
            asset_name=role_name
        )
        
        os.makedirs(publish_path, exist_ok=True)
        publish_file = os.path.join(publish_path, f"{project_prefix}_{shot_name}_{role_name}.blend")
        
        # Copy WIP to PUBLISH
        import shutil
        shutil.copy2(wip_file, publish_file)
        
        return wip_file
        
    except Exception as e:
        print(f"Error creating first WIP: {str(e)}")
        return None 