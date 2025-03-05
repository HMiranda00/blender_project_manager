"""
Funções para manipulação de caminhos e informações de projeto.
"""

import os
import re
import bpy
from ...preferences import get_addon_preferences

def get_project_info(path, is_fixed_root=False):
    """
    Extrai informações do projeto a partir de um caminho.
    
    Args:
        path (str): Caminho do projeto
        is_fixed_root (bool): Se está usando o modo de raiz fixa
        
    Returns:
        tuple: (nome_do_projeto, caminho_do_workspace, prefixo_do_projeto)
    """
    project_folder = os.path.basename(path.rstrip(os.path.sep))
    
    # Extrair o número do projeto (ex: 001, 002, etc)
    project_prefix = ""
    if is_fixed_root:
        prefix_match = re.match(r'^(\d+)\s*-\s*', project_folder)
        if prefix_match:
            project_prefix = prefix_match.group(1)
            # No modo raiz fixa, sempre usar "03 - 3D"
            workspace_folder = "03 - 3D"
            workspace_path = os.path.join(path, workspace_folder)
    else:
        prefix_match = re.match(r'^([A-Z]+\d+)', project_folder)
        project_prefix = prefix_match.group(1) if prefix_match else ""
        workspace_path = os.path.join(path, "3D")
        if not os.path.exists(workspace_path):
            os.makedirs(workspace_path)
    
    return project_folder, workspace_path, project_prefix

def get_next_project_number(root_path):
    """
    Obtém o próximo número de projeto disponível no modo de raiz fixa.
    
    Args:
        root_path (str): Caminho raiz onde os projetos estão armazenados
        
    Returns:
        int: Próximo número de projeto disponível
    """
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

def get_publish_path(preset, role_settings, context, project_path, project_name, shot_name, asset_name):
    """
    Obtém o caminho de publicação com base nas configurações.
    
    Args:
        preset (str): Preset de caminho ('SHOTS', 'CHARACTERS', 'PROPS', 'CUSTOM')
        role_settings: Configurações do papel
        context: Contexto do Blender
        project_path (str): Caminho do projeto
        project_name (str): Nome do projeto
        shot_name (str): Nome do shot
        asset_name (str): Nome do asset
        
    Returns:
        str: Caminho de publicação formatado
    """
    prefs = get_addon_preferences(context)
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

def get_role_path(context, role_name, shot_name=None):
    """
    Obtém o caminho base para um papel específico.
    
    Args:
        context: Contexto do Blender
        role_name (str): Nome do papel
        shot_name (str, optional): Nome do shot. Se None, usa o shot atual.
        
    Returns:
        tuple: (caminho_do_papel, prefixo_do_projeto, nome_do_shot)
    """
    try:
        if not context.scene.current_project:
            return None, "", ""
            
        if shot_name is None:
            shot_name = context.scene.current_shot
            
        if not shot_name:
            return None, "", ""
            
        project_path = context.scene.current_project
        prefs = get_addon_preferences(context)
        project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        
        # Encontrar as configurações do papel
        role_settings = None
        for role_mapping in prefs.role_mappings:
            if role_mapping.role_name == role_name:
                role_settings = role_mapping
                break
                
        if not role_settings:
            return None, project_prefix, shot_name
            
        # Obter caminho do papel
        role_path = os.path.join(workspace_path, "SHOTS", shot_name, role_name)
        os.makedirs(role_path, exist_ok=True)
        
        return role_path, project_prefix, shot_name
        
    except Exception as e:
        print(f"Erro ao obter caminho do papel: {str(e)}")
        return None, "", ""

def get_wip_path(context, role_name, shot_name=None):
    """
    Obtém o caminho WIP para o papel/shot atual.
    
    Args:
        context: Contexto do Blender
        role_name (str): Nome do papel
        shot_name (str, optional): Nome do shot. Se None, usa o shot atual.
        
    Returns:
        str: Caminho WIP ou None se não for possível obter
    """
    try:
        role_path, _, _ = get_role_path(context, role_name, shot_name)
        if not role_path:
            return None
            
        # Obter caminho WIP
        wip_path = os.path.join(role_path, "WIP")
        os.makedirs(wip_path, exist_ok=True)
        
        return wip_path
        
    except Exception as e:
        print(f"Erro ao obter caminho WIP: {str(e)}")
        return None

def get_latest_wip(context, role_name, shot_name=None):
    """
    Obtém a versão WIP mais recente para o papel atual.
    
    Args:
        context: Contexto do Blender
        role_name (str): Nome do papel
        shot_name (str, optional): Nome do shot. Se None, usa o shot atual.
        
    Returns:
        tuple: (caminho_do_arquivo, número_da_versão) ou (None, 0) se não encontrado
    """
    try:
        wip_path = get_wip_path(context, role_name, shot_name)
        if not wip_path:
            return None, 0
            
        role_path, project_prefix, shot = get_role_path(context, role_name, shot_name)
        if not role_path:
            return None, 0
            
        # Padrão: prefix_shot_role_v###.blend
        wip_pattern = f"{project_prefix}_{shot}_{role_name}_v"
        
        # Encontrar todos os arquivos WIP
        latest_version = 0
        latest_file = None
        
        for file in os.listdir(wip_path):
            if file.endswith(".blend"):
                try:
                    # Extrair número da versão do nome do arquivo
                    if wip_pattern in file:
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
        print(f"Erro ao obter WIP mais recente: {str(e)}")
        return None, 0

def verify_role_file(context, role_name, shot_name=None):
    """
    Verifica se existe um arquivo para o papel especificado.
    
    Args:
        context: Contexto do Blender
        role_name (str): Nome do papel
        shot_name (str, optional): Nome do shot. Se None, usa o shot atual.
        
    Returns:
        str: Caminho do arquivo ou None se não existir
    """
    try:
        if shot_name is None:
            shot_name = context.scene.current_shot
            
        if not (context.scene.current_project and shot_name):
            return None
            
        project_path = context.scene.current_project
        prefs = get_addon_preferences(context)
        project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        
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
        
        blend_filename = f"{project_prefix}_{shot_name}_{role_name}.blend"
        blend_path = os.path.join(publish_path, blend_filename)
        
        return blend_path if os.path.exists(blend_path) else None
        
    except Exception as e:
        print(f"Erro ao verificar arquivo de papel {role_name}: {str(e)}")
        return None

def get_assembly_path(context, shot_name=None):
    """
    Obtém o caminho do arquivo de montagem para um shot.
    
    Args:
        context: Contexto do Blender
        shot_name (str, optional): Nome do shot. Se None, usa o shot atual.
        
    Returns:
        str: Caminho do arquivo de montagem ou None se não for possível obter
    """
    try:
        if shot_name is None:
            shot_name = context.scene.current_shot
            
        if not (context.scene.current_project and shot_name):
            return None
            
        project_path = context.scene.current_project
        prefs = get_addon_preferences(context)
        project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        
        # Caminho para a pasta do shot
        shot_path = os.path.join(workspace_path, "SHOTS", shot_name)
        os.makedirs(shot_path, exist_ok=True)
        
        # Nome do arquivo de montagem
        assembly_filename = f"{project_prefix}_{shot_name}_ASSEMBLY.blend"
        assembly_path = os.path.join(shot_path, assembly_filename)
        
        return assembly_path
        
    except Exception as e:
        print(f"Erro ao obter caminho de montagem: {str(e)}")
        return None 