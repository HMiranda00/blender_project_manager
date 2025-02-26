import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

# Configurações
ADDON_NAME = "blender_project_manager"
BLENDER_ADDONS_PATH = r"C:\Users\HenriqueMiranda\AppData\Roaming\Blender Foundation\Blender\4.3\scripts\addons"
BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"

def kill_blender():
    """Fecha todas as instâncias do Blender"""
    try:
        # No Windows, usa taskkill para forçar o fechamento
        subprocess.run(['taskkill', '/F', '/IM', 'blender.exe'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        print("Blender closed successfully")
        # Aguarda um momento para garantir que o processo foi finalizado
        time.sleep(2)
    except Exception as e:
        print(f"Error closing Blender: {str(e)}")

def clean_pycache(directory):
    """Remove all __pycache__ and .pyc files"""
    for root, dirs, files in os.walk(directory):
        # Remove __pycache__ directories
        if '__pycache__' in dirs:
            shutil.rmtree(os.path.join(root, '__pycache__'))
            dirs.remove('__pycache__')
        
        # Remove .pyc files
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def update_addon():
    """Update addon in Blender directory"""
    try:
        # Current directory (where this script is)
        current_dir = Path(__file__).parent.absolute()
        
        # Source addon folder (from temp_release)
        source_dir = current_dir / "temp_release" / ADDON_NAME
        if not source_dir.exists():
            raise Exception(f"Source addon folder not found: {source_dir}")
        
        # Addon path in Blender
        addon_path = Path(BLENDER_ADDONS_PATH) / ADDON_NAME
        
        print(f"\nStarting addon update...")
        print(f"Source: {source_dir}")
        print(f"Destination: {addon_path}")
        
        # 1. Close Blender
        print("\n1. Closing Blender...")
        kill_blender()
        
        # 2. Remove old addon folder
        print("\n2. Removing old addon version...")
        if addon_path.exists():
            shutil.rmtree(addon_path)
            print("Old folder removed successfully")
        
        # 3. Create new addon folder
        print("\n3. Creating new addon folder...")
        os.makedirs(addon_path, exist_ok=True)
        
        # 4. Copy files
        print("\n4. Copying files...")
        for item in source_dir.iterdir():
            if item.name not in ['.git', '__pycache__']:
                if item.is_file():
                    print(f"Copying file: {item.name}")
                    shutil.copy2(item, addon_path)
                else:
                    print(f"Copying folder: {item.name}")
                    shutil.copytree(item, addon_path / item.name)
        
        # 5. Clean cache
        print("\n5. Cleaning cache...")
        clean_pycache(addon_path)
        
        # 6. Open Blender
        print("\n6. Opening Blender...")
        subprocess.Popen([BLENDER_EXE])
        
        print("\nUpdate completed successfully!")
        
    except Exception as e:
        print(f"\nERROR during update: {str(e)}")
        return False
        
    return True

if __name__ == "__main__":
    update_addon() 