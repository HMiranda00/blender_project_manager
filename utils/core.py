import os
import bpy
from ..preferences import get_addon_preferences
import re

def get_project_info(path, is_fixed_root=False):
    """Extract project info from a path"""
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

def get_publish_path(preset, role_settings, context, project_path, project_name, shot_name, asset_name):
    """Get the publish path based on settings"""
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

def save_current_file():
    """Save current file if it exists"""
    if bpy.data.is_saved:
        bpy.ops.wm.save_mainfile()

def create_project_structure(workspace_path):
    """Create standard project folder structure"""
    os.makedirs(os.path.join(workspace_path, 'SHOTS'), exist_ok=True)
    os.makedirs(os.path.join(workspace_path, 'ASSETS 3D', 'PROPS'), exist_ok=True)
    os.makedirs(os.path.join(workspace_path, 'ASSETS 3D', 'CHR'), exist_ok=True)
    os.makedirs(os.path.join(workspace_path, 'ASSETS 3D', 'ENV'), exist_ok=True)

def setup_collection_settings(collection, role_settings):
    """Setup collection color and other settings"""
    if collection:
        # Definir cor da collection
        if role_settings.collection_color != 'NONE':
            collection.color_tag = role_settings.collection_color
            
        # Configurar visibilidade
        viewlayer = bpy.context.view_layer
        layer_collection = viewlayer.layer_collection.children.get(collection.name)
        if layer_collection:
            layer_collection.hide_viewport = role_settings.hide_viewport_default
            layer_collection.exclude = role_settings.exclude_from_view_layer

def setup_role_world(role_settings):
    """Setup world if role owns it"""
    if role_settings.owns_world:
        for scene in bpy.data.scenes:
            if not scene.world:
                scene.world = bpy.data.worlds.new(name=f"{role_settings.role_name}_World")

def force_ui_update():
    """Force UI update in all areas"""
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw() 

# Classe para representar configurações do projeto
class ProjectSettings:
    """Representa as configurações do projeto atual"""
    
    def __init__(self):
        """Inicializa as configurações do projeto com base no contexto atual"""
        self.context = bpy.context
        self.prefs = get_addon_preferences(self.context)
        
        # Obtém informações do projeto atual
        self.project_path = self.context.scene.current_project if hasattr(self.context.scene, 'current_project') else ""
        self.shot_name = self.context.scene.current_shot if hasattr(self.context.scene, 'current_shot') else ""
        self.role_name = self.context.scene.current_role if hasattr(self.context.scene, 'current_role') else ""
        
        # Calcula as informações do projeto
        if self.project_path:
            self.project_name, self.workspace_path, self.project_prefix = get_project_info(
                self.project_path, 
                self.prefs.use_fixed_root if hasattr(self.prefs, 'use_fixed_root') else False
            )
        else:
            self.project_name = ""
            self.workspace_path = ""
            self.project_prefix = ""
    
    def get_role_dir(self, role_name):
        """Retorna o diretório para o role especificado"""
        if not (self.project_path and self.shot_name):
            return None
            
        # Encontra as configurações para o role
        role_settings = None
        for role_mapping in self.prefs.role_mappings:
            if role_mapping.role_name == role_name:
                role_settings = role_mapping
                break
                
        if not role_settings:
            return None
            
        # Obtém o caminho de publicação
        publish_path = get_publish_path(
            role_settings.publish_path_preset,
            role_settings,
            self.context,
            self.project_path,
            self.project_name,
            self.shot_name,
            asset_name=role_name
        )
        
        # Cria o diretório se não existir
        os.makedirs(publish_path, exist_ok=True)
        
        return publish_path
    
    def get_role_file_path(self, role_name, create_dir=True):
        """Retorna o caminho completo para o arquivo de role"""
        role_dir = self.get_role_dir(role_name)
        if not role_dir:
            return None
            
        if create_dir:
            os.makedirs(role_dir, exist_ok=True)
            
        blend_filename = f"{self.project_prefix}_{self.shot_name}_{role_name}.blend"
        return os.path.join(role_dir, blend_filename)

def get_project_settings():
    """Retorna as configurações do projeto atual"""
    try:
        return ProjectSettings()
    except Exception as e:
        print(f"Erro ao obter configurações do projeto: {str(e)}")
        return None

def verify_role_file(context, role_name):
    """Verifica se existe um arquivo para o role especificado"""
    try:
        project_settings = get_project_settings()
        if not project_settings:
            return None
            
        file_path = project_settings.get_role_file_path(role_name, create_dir=False)
        
        return file_path if file_path and os.path.exists(file_path) else None
            
    except Exception as e:
        print(f"Erro ao verificar arquivo de role {role_name}: {str(e)}")
        return None 