import os
import sys
import platform
import re
import subprocess
import shutil
from pathlib import Path

# Diretório base do addon (um nível acima deste script)
ADDON_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Lista de arquivos/diretórios relevantes para o addon
RELEVANT_FILES = [
    "__init__.py",
    "blender_manifest.toml",
    "preferences.py",
    "handlers.py"
]

# Lista de diretórios relevantes para o addon
RELEVANT_DIRS = [
    "operators",
    "panels",
    "utils"
]

# Lista de arquivos/diretórios a serem ignorados
IGNORED_PATTERNS = [
    ".git",
    ".vscode",
    ".idea",
    "__pycache__",
    "build_tools",
    "README.md",
    ".gitignore",
    "*.blend",
    "*.blend1",
    "*.pyc"
]

def get_blender_version_dir():
    """Encontra o diretório de configuração do Blender mais recente"""
    system = platform.system()
    
    if system == "Windows":
        appdata = os.getenv("APPDATA")
        base_path = os.path.join(appdata, "Blender Foundation", "Blender")
    elif system == "Darwin":  # macOS
        base_path = os.path.expanduser("~/Library/Application Support/Blender")
    else:  # Linux e outros
        base_path = os.path.expanduser("~/.config/blender")
    
    # Verifica primeiro Blender 4.x, depois 3.x
    versions = []
    if os.path.exists(base_path):
        for item in os.listdir(base_path):
            if re.match(r'^[34]\.\d+$', item):
                versions.append(item)
    
    if not versions:
        return None
    
    # Ordena versões em ordem decrescente (mais recente primeiro)
    versions.sort(key=lambda s: [int(u) for u in s.split('.')], reverse=True)
    return os.path.join(base_path, versions[0])

def should_ignore(item_name):
    """Verifica se um arquivo ou diretório deve ser ignorado"""
    for pattern in IGNORED_PATTERNS:
        if '*' in pattern:
            # Se o padrão contém *, usa correspondência de padrão
            regex = pattern.replace('.', '\.').replace('*', '.*')
            if re.match(regex, item_name):
                return True
        elif pattern == item_name:
            # Correspondência exata
            return True
    return False

def create_symlink(source, target, is_dir=False):
    """Cria um link simbólico com tratamento para diferentes sistemas operacionais"""
    try:
        if platform.system() == "Windows":
            if os.path.exists(target):
                if os.path.islink(target):
                    os.unlink(target)
                elif os.path.isdir(target):
                    shutil.rmtree(target)
                else:
                    os.remove(target)
            
            # No Windows, precisamos verificar permissões e usar diferentes abordagens
            admin_status = subprocess.run(['net', 'session'], capture_output=True, text=True).returncode == 0
            
            if admin_status or not is_dir:
                # Com privilégios admin ou para arquivos, podemos usar o método direto
                os.symlink(source, target, target_is_directory=is_dir)
                return True
            else:
                # Para diretórios, tentar o comando mklink se não tiver permissões
                cmd = ['mklink', '/D' if is_dir else '', target, source]
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.returncode == 0
        else:
            # Linux/macOS
            if os.path.exists(target):
                if os.path.islink(target):
                    os.unlink(target)
                elif os.path.isdir(target):
                    shutil.rmtree(target)
                else:
                    os.remove(target)
            
            os.symlink(source, target)
            return True
    except Exception as e:
        print(f"Erro ao criar link simbólico {source} -> {target}: {e}")
        return False

def copy_dir_with_symlinks(src_dir, dst_dir):
    """Copia um diretório, criando links simbólicos para os arquivos internos relevantes"""
    # Cria o diretório de destino se não existir
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    
    # Percorre todos os arquivos e subdiretórios
    for item in os.listdir(src_dir):
        src_item = os.path.join(src_dir, item)
        dst_item = os.path.join(dst_dir, item)
        
        # Verifica se deve ignorar
        if should_ignore(item):
            continue
            
        if os.path.isdir(src_item):
            # Para diretórios, continua recursivamente
            copy_dir_with_symlinks(src_item, dst_item)
        else:
            # Para arquivos, cria um link simbólico
            create_symlink(src_item, dst_item)

def create_symlinks():
    """Cria links simbólicos entre os arquivos do addon e a pasta de extensões"""
    # Obtém o diretório do Blender
    blender_dir = get_blender_version_dir()
    if not blender_dir:
        print("Não foi possível encontrar o diretório do Blender!")
        return False
    
    print(f"Diretório do Blender encontrado: {blender_dir}")
    
    # Define o caminho para a pasta de extensões
    extensions_dir = os.path.join(blender_dir, "extensions", "user_default")
    target_dir = os.path.join(extensions_dir, "blender_project_manager")
    
    # Verifica se a pasta de extensões existe
    if not os.path.exists(extensions_dir):
        os.makedirs(extensions_dir, exist_ok=True)
        print(f"Criado diretório: {extensions_dir}")
    
    # Remove a pasta alvo se existir
    if os.path.exists(target_dir):
        print(f"Removendo instalação anterior: {target_dir}")
        if os.path.islink(target_dir):
            os.unlink(target_dir)
        else:
            shutil.rmtree(target_dir)
    
    # Cria o diretório de destino
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"Criando links simbólicos em: {target_dir}")
    
    # Cria links para arquivos individuais na raiz
    for file in RELEVANT_FILES:
        source = os.path.join(ADDON_ROOT, file)
        target = os.path.join(target_dir, file)
        
        if os.path.exists(source):
            if create_symlink(source, target):
                print(f"Link criado: {file}")
            else:
                print(f"Falha ao criar link para: {file}")
    
    # Cria links para diretórios relevantes
    for dir_name in RELEVANT_DIRS:
        source_dir = os.path.join(ADDON_ROOT, dir_name)
        target_subdir = os.path.join(target_dir, dir_name)
        
        if os.path.exists(source_dir):
            # Cria a estrutura de diretórios e links
            if os.path.exists(target_subdir):
                if os.path.islink(target_subdir):
                    os.unlink(target_subdir)
                else:
                    shutil.rmtree(target_subdir)
            
            # Cria o diretório
            os.makedirs(target_subdir, exist_ok=True)
            print(f"Criando links para diretório: {dir_name}")
            
            # Cria links para os arquivos dentro do diretório
            copy_dir_with_symlinks(source_dir, target_subdir)
    
    print("\n===============================================================")
    print("Instalação via links simbólicos concluída!")
    print("Agora qualquer alteração nos arquivos será refletida no Blender")
    print("sem necessidade de reinstalar o addon. Basta reiniciar o Blender.")
    print("===============================================================\n")
    
    return True

if __name__ == "__main__":
    create_symlinks() 