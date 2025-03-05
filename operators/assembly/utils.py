import bpy
import os
from ...utils import get_project_info, get_publish_path

def get_assembly_path(context, shot_name):
    """Get the assembly file path for a shot"""
    prefs = context.preferences.addons['blender_project_manager'].preferences
    project_path = context.scene.current_project
    project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
    
    # Assembly is always in SHOTS folder
    shots_path = os.path.join(workspace_path, "SHOTS", shot_name, "ASSEMBLY")
    os.makedirs(shots_path, exist_ok=True)
    
    assembly_file = f"{project_prefix}_{shot_name}_ASSEMBLY.blend"
    return os.path.join(shots_path, assembly_file)

def get_role_publish_file(context, role_name, shot_name):
    """Get the publish file path for a role"""
    prefs = context.preferences.addons['blender_project_manager'].preferences
    project_path = context.scene.current_project
    project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
    
    # Get role settings
    role_settings = None
    for role_mapping in prefs.role_mappings:
        if role_mapping.role_name == role_name:
            role_settings = role_mapping
            break
            
    if not role_settings or role_settings.skip_assembly:
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
    
    publish_file = f"{project_prefix}_{shot_name}_{role_name}.blend"
    return os.path.join(publish_path, publish_file) 