import os
import zipfile
import shutil
from pathlib import Path

def zip_addon():
    # Nome do arquivo zip final
    zip_name = "blender_project_manager.zip"
    
    # Pasta temporária onde vamos copiar os arquivos
    temp_dir = "temp_build"
    addon_dir = os.path.join(temp_dir, "blender_project_manager")
    
    # Criar pasta temporária
    os.makedirs(addon_dir, exist_ok=True)
    
    # Lista de arquivos/pastas para incluir
    items_to_include = [
        "__init__.py",
        "operators",
        "panels",
        "preferences.py",
        "utils"
    ]
    
    # Copiar arquivos para pasta temporária
    for item in items_to_include:
        src = item
        dst = os.path.join(addon_dir, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
    
    # Criar arquivo zip
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zf.write(file_path, arcname)
    
    # Limpar pasta temporária
    shutil.rmtree(temp_dir)
    
    print(f"Addon zipado com sucesso: {zip_name}")

if __name__ == "__main__":
    zip_addon() 