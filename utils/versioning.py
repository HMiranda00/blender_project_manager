import bpy
import os
import re
import shutil
from datetime import datetime, timedelta
from ..utils import get_project_info, get_publish_path
from .cache import DirectoryCache

def get_version_number(filepath):
    """Extrai o número da versão do nome do arquivo"""
    match = re.search(r'_(\d{3})\.blend$', filepath)
    return int(match.group(1)) if match else 0

def get_last_publish_info(context):
    """Retorna informação sobre a última publicação"""
    try:
        # Se temos um timestamp salvo, usar ele
        if hasattr(context.scene, "last_publish_time") and context.scene.last_publish_time:
            # Converter string para datetime
            publish_time = datetime.strptime(context.scene.last_publish_time, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            diff = now - publish_time
            
            # Formatar diferença de tempo
            if diff.days > 0:
                return f"há {diff.days} dias"
            elif diff.seconds >= 3600:
                hours = diff.seconds // 3600
                return f"há {hours} horas"
            elif diff.seconds >= 60:
                minutes = diff.seconds // 60
                return f"há {minutes} min"
            else:
                return f"há {diff.seconds} seg"
                
        # Se não temos timestamp, tentar obter do arquivo
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        project_path = context.scene.current_project
        shot_name = context.scene.current_shot
        role_name = context.scene.current_role
        
        project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        
        # Encontrar configurações do cargo
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
            asset_name=''
        )
        
        publish_file = f"{project_prefix}_{shot_name}_{role_name}.blend"
        publish_filepath = os.path.join(publish_path, publish_file)
        
        if os.path.exists(publish_filepath):
            mtime = os.path.getmtime(publish_filepath)
            last_modified = datetime.fromtimestamp(mtime)
            now = datetime.now()
            delta = now - last_modified
            
            if delta < timedelta(hours=1):
                minutes = int(delta.total_seconds() / 60)
                return f"há {minutes} minutos"
            elif delta < timedelta(days=1):
                hours = int(delta.total_seconds() / 3600)
                return f"há {hours} horas"
            elif delta < timedelta(days=5):
                days = delta.days
                return f"há {days} dias"
            else:
                return last_modified.strftime("%d/%m/%Y")
        return None
    except Exception as e:
        print(f"Erro ao obter info da publicação: {str(e)}")
        return None

def get_next_version_path(context):
    """Retorna o caminho para a próxima versão do arquivo"""
    try:
        if not context.scene.current_project or not context.scene.current_shot or not context.scene.current_role:
            return None
            
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        project_path = context.scene.current_project
        shot_name = context.scene.current_shot
        role_name = context.scene.current_role
        
        project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        
        # Encontrar configurações do cargo
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
            asset_name=''
        )
        
        # Criar pasta _WIP
        wip_path = os.path.join(os.path.dirname(publish_path), "_WIP")
        os.makedirs(wip_path, exist_ok=True)
        
        # Base do nome do arquivo
        base_name = f"{project_prefix}_{shot_name}_{role_name}"
        
        # Encontrar última versão
        files = DirectoryCache.get_files(wip_path)
        version_files = [f for f in files if f.startswith(f"{base_name}_WIP_") and f.endswith(".blend")]
        
        if not version_files:
            # Primeira versão
            version = 1
        else:
            # Próxima versão
            version = max(get_version_number(f) for f in version_files) + 1
            
        new_filename = f"{base_name}_WIP_{version:03d}.blend"
        return os.path.join(wip_path, new_filename)
        
    except Exception as e:
        print(f"Erro ao gerar próxima versão: {str(e)}")
        return None

def get_version_status(context):
    """Retorna o status da versão atual e um ícone apropriado"""
    try:
        if not bpy.data.is_saved:
            return 'NOT_SAVED', 'ERROR'
            
        current_file = bpy.data.filepath
        if "_WIP_" not in current_file:
            return 'NOT_WIP', 'ERROR'
            
        # Obter caminho do arquivo publicado
        publish_path = os.path.dirname(os.path.dirname(current_file))
        publish_file = os.path.basename(current_file).replace("_WIP_", "_").split("_", 4)[0:3]
        publish_file = "_".join(publish_file) + ".blend"
        publish_filepath = os.path.join(publish_path, "PUBLISH", publish_file)
        
        if not os.path.exists(publish_filepath):
            return 'NEVER_PUBLISHED', 'ERROR'  # Vermelho
            
        # Comparar datas de modificação
        wip_time = os.path.getmtime(current_file)
        pub_time = os.path.getmtime(publish_filepath)
        
        if wip_time > pub_time:
            return 'NEEDS_UPDATE', 'ERROR'  # Vermelho
        elif wip_time == pub_time:
            return 'UP_TO_DATE', 'CHECKMARK'  # Verde
        else:
            return 'OLDER_THAN_PUBLISH', 'QUESTION'  # Amarelo
            
    except:
        return 'UNKNOWN', 'QUESTION' 

def create_first_wip(context, publish_filepath):
    """
    Cria a primeira versão WIP a partir de um arquivo publicado
    Retorna o caminho do novo arquivo WIP
    """
    try:
        # Construir caminho para pasta WIP
        publish_dir = os.path.dirname(publish_filepath)
        base_dir = os.path.dirname(publish_dir)
        wip_path = os.path.join(base_dir, "_WIP")
        os.makedirs(wip_path, exist_ok=True)
        
        # Construir nome do arquivo WIP
        base_name = os.path.basename(publish_filepath)
        base_name = base_name.replace(".blend", "")  # Remove extensão
        wip_file = f"{base_name}_WIP_001.blend"
        wip_filepath = os.path.join(wip_path, wip_file)
        
        # Copiar arquivo publicado para WIP
        shutil.copy2(publish_filepath, wip_filepath)
        
        return wip_filepath
        
    except Exception as e:
        print(f"Erro ao criar primeiro WIP: {str(e)}")
        return None

def redirect_to_latest_wip(context, filepath):
    """
    Verifica se deve redirecionar para um arquivo WIP
    Retorna (should_redirect, wip_path)
    """
    try:
        # Construir caminho para pasta WIP
        publish_dir = os.path.dirname(filepath)
        base_dir = os.path.dirname(publish_dir)
        wip_path = os.path.join(base_dir, "_WIP")
        
        if not os.path.exists(wip_path):
            return False, None
            
        # Obter base do nome do arquivo
        base_name = os.path.basename(filepath)
        base_name = base_name.replace(".blend", "")  # Remove extensão
        
        # Procurar arquivos WIP existentes
        files = DirectoryCache.get_files(wip_path)
        wip_files = [f for f in files if f.startswith(f"{base_name}_WIP_") and f.endswith(".blend")]
        
        if wip_files:
            # Se existem versões WIP, usar a mais recente
            latest_wip = max(wip_files, key=lambda f: get_version_number(f))
            wip_filepath = os.path.join(wip_path, latest_wip)
            return True, wip_filepath
            
        return False, None
        
    except Exception as e:
        print(f"Erro ao verificar redirecionamento WIP: {str(e)}")
        return False, None 

def get_next_version_number(folder_path):
    """
    Retorna o próximo número de versão baseado nos arquivos existentes
    """
    try:
        if not os.path.exists(folder_path):
            return 1
            
        # Procurar por arquivos com padrão _v001.blend
        versions = []
        for file in os.listdir(folder_path):
            if file.endswith('.blend'):
                match = re.search(r'_v(\d{3})\.blend$', file)
                if match:
                    versions.append(int(match.group(1)))
        
        # Retornar próximo número
        return max(versions, default=0) + 1
        
    except Exception as e:
        print(f"Erro ao obter próximo número de versão: {str(e)}")
        return 1 