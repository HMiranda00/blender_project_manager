import bpy
import os
from .core import get_project_info, get_publish_path

def get_folder_code(path, role_settings=None):
    """Get two letter code based on publish path preset"""
    try:
        if not role_settings:
            return 'UN'  # Unknown/undefined
            
        if not role_settings.publish_path_preset:
            return 'UN'  # Unknown/undefined
            
        # Map preset to folder code
        preset_codes = {
            'SHOTS': 'SH',
            'CHARACTERS': 'CH',
            'PROPS': 'PR'
        }
        
        # Se for CUSTOM, pegar as duas primeiras letras do caminho personalizado
        if role_settings.publish_path_preset == 'CUSTOM':
            if not role_settings.custom_publish_path:
                return 'UN'  # Custom sem path definido
                
            # Remover placeholders do caminho
            clean_path = role_settings.custom_publish_path
            for placeholder in ['{root}', '{projectCode}', '{shot}', '{role}', '{assetName}']:
                clean_path = clean_path.replace(placeholder, '')
            
            # Normalizar separadores de caminho e dividir
            parts = [p for p in clean_path.replace('\\', '/').split('/') if p and p not in ['PUBLISH', 'WIP']]
            
            # Pegar o primeiro diretório não vazio
            if parts:
                # Garantir que temos pelo menos 2 caracteres
                folder_name = parts[0][:2].upper()
                if len(folder_name) < 2:
                    folder_name = folder_name.ljust(2, 'X')
                return folder_name
                
        # Para presets padrão
        return preset_codes.get(role_settings.publish_path_preset, 'UN')
        
    except Exception as e:
        print(f"Error getting folder code: {str(e)}")
        return 'UN'  # Unknown/undefined

def get_wip_path(context, role_name):
    """Get the WIP path for the current role/shot"""
    try:
        if not (context.scene.current_project and context.scene.current_shot):
            return None
            
        project_path = context.scene.current_project
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot
        
        # Get role settings
        role_settings = None
        for role_mapping in prefs.role_mappings:
            if role_mapping.role_name == role_name:
                role_settings = role_mapping
                break
                
        if not role_settings:
            return None
            
        # Get base path from publish path
        publish_path = get_publish_path(
            role_settings.publish_path_preset,
            role_settings,
            context,
            project_path,
            project_name,
            shot_name,
            asset_name=role_name
        )
        
        # Replace PUBLISH with WIP in the path
        wip_path = publish_path.replace('PUBLISH', 'WIP')
        os.makedirs(wip_path, exist_ok=True)
        
        return wip_path
        
    except Exception as e:
        print(f"Error getting WIP path: {str(e)}")
        return None

def create_first_wip(context, role_name):
    """Create the first WIP version and its PUBLISH"""
    try:
        if not (context.scene.current_project and context.scene.current_shot):
            return None
            
        # Store current context
        current_project = context.scene.current_project
        current_shot = context.scene.current_shot
        current_role = context.scene.current_role
            
        project_path = context.scene.current_project
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot
        
        # Get role settings
        role_settings = None
        for role_mapping in prefs.role_mappings:
            if role_mapping.role_name == role_name:
                role_settings = role_mapping
                break
                
        if not role_settings:
            print(f"Role settings not found for {role_name}")
            return None
            
        # Get WIP path
        wip_path = get_wip_path(context, role_name)
        if not wip_path:
            print(f"Could not get WIP path for {role_name}")
            return None
            
        # Get publish path
        publish_path = get_publish_path(
            role_settings.publish_path_preset,
            role_settings,
            context,
            project_path,
            project_name,
            shot_name,
            asset_name=role_name
        )
        
        print(f"Creating first WIP in {wip_path}")
        print(f"Publish path will be {publish_path}")
        
        # Check if there are any files in old format
        use_old_format = False
        old_pattern = f"{project_prefix}_{role_name}"
        
        # Check WIP folder
        if os.path.exists(wip_path):
            for file in os.listdir(wip_path):
                if file.startswith(old_pattern) and file.endswith(".blend"):
                    use_old_format = True
                    break
                    
        # Check publish folder
        if os.path.exists(publish_path):
            for file in os.listdir(publish_path):
                if file.startswith(old_pattern) and file.endswith(".blend"):
                    use_old_format = True
                    break
        
        if use_old_format:
            print(f"Using old format for {role_name}")
            # Use old format
            wip_file = os.path.join(wip_path, f"{project_prefix}_{role_name}_v001.blend")
            publish_file = os.path.join(publish_path, f"{project_prefix}_{role_name}.blend")
        else:
            print(f"Using new format for {role_name}")
            # Use new format with folder code
            folder_code = get_folder_code(wip_path, role_settings)
            wip_file = os.path.join(wip_path, f"{project_prefix}_{folder_code}_{shot_name}_{role_name}_v001.blend")
            publish_file = os.path.join(publish_path, f"{project_prefix}_{folder_code}_{shot_name}_{role_name}.blend")
        
        # Create directories
        os.makedirs(os.path.dirname(wip_file), exist_ok=True)
        os.makedirs(os.path.dirname(publish_file), exist_ok=True)
        
        print(f"Saving WIP file: {wip_file}")
        # Save WIP
        bpy.ops.wm.save_as_mainfile(filepath=wip_file)
        
        print(f"Creating publish file: {publish_file}")
        # Copy WIP to PUBLISH
        import shutil
        shutil.copy2(wip_file, publish_file)
        
        # Restore context
        context.scene.current_project = current_project
        context.scene.current_shot = current_shot
        context.scene.current_role = current_role
        
        return wip_file
        
    except Exception as e:
        print(f"Error creating first WIP: {str(e)}")
        return None

def get_latest_wip(context, role_name):
    """Get the latest WIP version for the current role"""
    try:
        wip_path = get_wip_path(context, role_name)
        if not wip_path:
            print("Could not get WIP path")
            return None
            
        project_path = context.scene.current_project
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot
        
        # Get role settings for folder code
        role_settings = None
        for role_mapping in prefs.role_mappings:
            if role_mapping.role_name == role_name:
                role_settings = role_mapping
                break
                
        if not role_settings:
            print("Role settings not found")
            return None
            
        # Try both old and new format
        latest_version = 0
        latest_file = None
        
        # Check old format first (for compatibility)
        old_pattern = f"{project_prefix}_{role_name}_v"
        if os.path.exists(wip_path):
            for file in os.listdir(wip_path):
                if file.startswith(old_pattern) and file.endswith(".blend"):
                    try:
                        version = int(file.split("_v")[-1].split(".")[0])
                        if version > latest_version:
                            latest_version = version
                            latest_file = os.path.join(wip_path, file)
                    except ValueError:
                        continue
        
        # Check new format
        folder_code = get_folder_code(wip_path, role_settings)
        new_pattern = f"{project_prefix}_{folder_code}_{shot_name}_{role_name}_v"
        if os.path.exists(wip_path):
            for file in os.listdir(wip_path):
                if file.startswith(new_pattern) and file.endswith(".blend"):
                    try:
                        version = int(file.split("_v")[-1].split(".")[0])
                        if version > latest_version:
                            latest_version = version
                            latest_file = os.path.join(wip_path, file)
                    except ValueError:
                        continue
        
        if not latest_file:
            print("No WIP files found")
            # Se não encontrou nenhum arquivo WIP, criar o primeiro
            latest_file = create_first_wip(context, role_name)
            
        return latest_file
        
    except Exception as e:
        print(f"Error getting latest WIP: {str(e)}")
        return None 