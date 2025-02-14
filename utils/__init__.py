import os
import bpy
import re
from .cache import DirectoryCache
from .project_utils import (
    get_project_info,
    get_next_project_number,
    create_project_structure,
    get_publish_path
)
from .versioning import get_next_version_number

ASSEMBLY_ROLE = "ASSEMBLY"

def is_assembly_role(role_name):
    """Verifica se o cargo Ã© do tipo assembly"""
    return role_name and role_name.upper() == ASSEMBLY_ROLE

def get_assembly_role():
    """Retorna o nome do cargo Assembly"""
    return ASSEMBLY_ROLE

def get_project_mode(context):
    """
    Retorna o modo atual do projeto
    Args:
        context: bpy.context
    Returns:
        str: 'TEAM' ou 'SOLO'
    """
    if hasattr(context.scene, "project_settings"):
        return context.scene.project_settings.project_type
    return 'SOLO'  # Fallback para modo solo

def save_current_file():
    """Save current file if it exists"""
    if bpy.data.is_saved:
        bpy.ops.wm.save_mainfile()

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

def detect_file_context(filepath, project_prefix):
    """Detecta o contexto (shot e cargo) a partir do nome do arquivo"""
    filename = os.path.basename(filepath)
    
    # PadrÃ£o esperado: PREFIX_SHOT_ROLE.blend
    pattern = rf"{project_prefix}_(.+?)_(.+?)\.blend"
    match = re.match(pattern, filename)
    
    if match:
        shot_name = match.group(1)
        role_name = match.group(2)
        return shot_name, role_name
    return None, None

def show_progress_status(context, message, progress=0):
    """
    Mostra mensagem de progresso no Info Panel
    Args:
        context: bpy.context
        message: Mensagem a ser exibida
        progress: Porcentagem de progresso (0-100)
    """
    try:
        # Tentar usar o workspace atual
        if context and context.workspace:
            if progress > 0:
                context.workspace.status_text_set(f"{message} ({progress:.0f}%)")
            else:
                context.workspace.status_text_set(message)
        # Fallback: usar o primeiro workspace disponÃ­vel
        else:
            for workspace in bpy.data.workspaces:
                if progress > 0:
                    workspace.status_text_set(f"{message} ({progress:.0f}%)")
                else:
                    workspace.status_text_set(message)
                break
    except:
        # Se tudo falhar, apenas ignorar silenciosamente
        pass
