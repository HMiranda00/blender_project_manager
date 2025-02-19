import os
import zipfile
import datetime
import shutil

# Configurações
ADDON_NAME = "blender_project_manager"  # Nome que o Blender espera (lowercase)
VERSION = "1.6.0.0"  # Extraído do README
IGNORE_PATTERNS = [
    '__pycache__',
    '.git',
    '.gitignore',
    'build.py',
    '*.pyc',
    '.vscode',
    '.idea',
    'README.md',
    'LICENSE',
    '*.zip'
]

def should_ignore(path):
    """Verifica se o arquivo/pasta deve ser ignorado"""
    for pattern in IGNORE_PATTERNS:
        if pattern in path:
            return True
    return False

def create_zip():
    """Cria o arquivo ZIP do addon"""
    # Cria pasta temporária com o nome do addon
    temp_dir = "temp_build"
    addon_dir = os.path.join(temp_dir, ADDON_NAME)
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(addon_dir)
    
    # Copia arquivos para pasta temporária
    for root, dirs, files in os.walk('.'):
        # Ignora diretórios da lista
        dirs[:] = [d for d in dirs if not should_ignore(d)]
        
        for file in files:
            if not should_ignore(file):
                src_path = os.path.join(root, file)
                # Remove './' do início do caminho
                rel_path = os.path.relpath(src_path, '.')
                dst_path = os.path.join(addon_dir, rel_path)
                
                # Cria diretório de destino se não existir
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)
    
    # Nome do arquivo ZIP
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"{ADDON_NAME}_v{VERSION}_{timestamp}.zip"
    
    # Cria o arquivo ZIP
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Define o nome dentro do arquivo zip relativo à pasta temp_build
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    # Remove pasta temporária
    shutil.rmtree(temp_dir)
    
    print(f"Addon zipado com sucesso: {zip_name}")
    return zip_name

if __name__ == "__main__":
    zip_file = create_zip() 