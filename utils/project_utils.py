import os
import re
import bpy
from .cache import DirectoryCache

def get_addon_prefs():
    """Returns the addon preferences in a centralized way"""
    try:
        return bpy.context.preferences.addons['blender_project_manager'].preferences
    except (KeyError, AttributeError) as e:
        print(f"Error getting addon preferences: {str(e)}")
        print("Make sure the addon is enabled in Blender preferences")
        return None
    except Exception as e:
        print(f"Unexpected error getting addon preferences: {str(e)}")
        return None

def save_current_file():
    """Salva o arquivo atual se necessário"""
    try:
        if bpy.data.is_dirty:
            if bpy.data.filepath:
                bpy.ops.wm.save_mainfile()
            else:
                return False
        return True
    except Exception as e:
        print(f"Erro ao salvar arquivo: {str(e)}")
        return False

def get_project_info(path, is_fixed_root=False):
    """Extract project info from a path"""
    try:
        if not path:
            return "", "", ""
            
        project_folder = os.path.basename(path.rstrip(os.path.sep))
        
        # Debug
        print(f"\nget_project_info debug:")
        print(f"Input path: {path}")
        print(f"Project folder: {project_folder}")
        print(f"Is fixed root: {is_fixed_root}")
        
        project_prefix = ""
        workspace_path = ""
        
        if is_fixed_root:
            # Formato: "001 - Nome do Projeto"
            prefix_match = re.match(r'^(\d+)\s*-\s*', project_folder)
            if prefix_match:
                project_prefix = prefix_match.group(1)
                workspace_path = os.path.join(path, "3D")
        else:
            # Formato livre
            prefix_match = re.match(r'^([A-Z]+\d+)', project_folder)
            project_prefix = prefix_match.group(1) if prefix_match else project_folder
            workspace_path = os.path.join(path, "3D")
        
        # Debug
        print(f"Project prefix: {project_prefix}")
        print(f"Workspace path: {workspace_path}")
        
        return project_folder, workspace_path, project_prefix
        
    except Exception as e:
        print(f"Erro em get_project_info: {str(e)}")
        import traceback
        traceback.print_exc()
        return "", "", ""

def get_next_project_number(root_path):
    """Get the next available project number in fixed root mode"""
    try:
        project_numbers = []
        for folder in os.listdir(root_path):
            if os.path.isdir(os.path.join(root_path, folder)):
                match = re.match(r'^(\d+)\s*-\s*', folder)
                if match:
                    project_numbers.append(int(match.group(1)))
        return max(project_numbers, default=0) + 1
    except Exception:
        return 1

def create_project_structure(workspace_path, project_prefix=None, project_type='TEAM'):
    """Create standard project folder structure"""
    # Pastas comuns para todos os tipos
    os.makedirs(os.path.join(workspace_path, 'ASSETS 3D', 'PROPS'), exist_ok=True)
    os.makedirs(os.path.join(workspace_path, 'ASSETS 3D', 'CHR'), exist_ok=True)
    os.makedirs(os.path.join(workspace_path, 'ASSETS 3D', 'ENV'), exist_ok=True)
    os.makedirs(os.path.join(workspace_path, 'ASSETS 3D', 'MATERIALS'), exist_ok=True)
    
    if project_type == 'TEAM':
        # Estrutura para projetos em equipe
        os.makedirs(os.path.join(workspace_path, 'SHOTS'), exist_ok=True)
        os.makedirs(os.path.join(workspace_path, 'SHOTS', 'ASSEMBLY'), exist_ok=True)
    else:
        # Estrutura para projetos solo
        os.makedirs(os.path.join(workspace_path, 'SCENES'), exist_ok=True)

def get_publish_path(preset, role_settings, context, project_path, project_name, shot_name, asset_name):
    """Get the publish path based on settings"""
    prefs = get_addon_prefs()
    _, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
    
    placeholders = {
        'root': workspace_path,
        'projectCode': project_name,
        'shot': shot_name,
        'role': role_settings.role_name,
        'assetName': asset_name
    }
    
    if preset == 'SHOTS':
        path_template = "{root}/SHOTS/{shot}/{role}/PUBLISH"
    elif preset == 'CHARACTERS':
        path_template = "{root}/ASSETS 3D/CHR/{assetName}/PUBLISH"
    elif preset == 'PROPS':
        path_template = "{root}/ASSETS 3D/PROPS/{assetName}/PUBLISH"
    elif preset == 'CUSTOM':
        path_template = role_settings.custom_publish_path
    else:
        path_template = "{root}/SHOTS/{shot}/{role}/PUBLISH"
        
    return path_template.format(**placeholders) 

def get_project_shots(project_path):
    """Get list of shots in the project"""
    shots = []
    workspace_path = os.path.join(project_path, "3D")
    shots_path = os.path.join(workspace_path, "SHOTS")
    
    if os.path.exists(shots_path):
        for shot in os.listdir(shots_path):
            if os.path.isdir(os.path.join(shots_path, shot)):
                shots.append(shot)
    
    return sorted(shots)

def get_project_roles(project_path):
    """Get list of roles from addon preferences"""
    roles = []
    prefs = get_addon_prefs()
    
    if prefs and prefs.role_mappings:
        for rm in prefs.role_mappings:
            if rm.role_name != "ASSEMBLY":  # Não incluir o cargo ASSEMBLY
                roles.append({
                    'name': rm.role_name,
                    'icon': rm.icon if rm.icon != 'NONE' else 'OUTLINER_COLLECTION'
                })
    
    return roles 
