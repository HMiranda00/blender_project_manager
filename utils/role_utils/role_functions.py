"""
Funções para manipulação de papéis (roles) no Blender Project Manager.
"""

import bpy
import os
from ...preferences import get_addon_preferences
from ..path_utils import verify_role_file, get_project_info

def get_roles(context, exclude_current=False):
    """
    Obtém a lista de papéis disponíveis.
    
    Args:
        context: Contexto do Blender
        exclude_current (bool): Se deve excluir o papel atual da lista
        
    Returns:
        list: Lista de tuplas (id, nome, descrição, ícone, índice) para uso em EnumProperty
    """
    prefs = get_addon_preferences(context)
    current_role = context.scene.current_role if exclude_current else None
    
    items = []
    for i, role_mapping in enumerate(prefs.role_mappings):
        if role_mapping.role_name != current_role:
            items.append((
                role_mapping.role_name,
                role_mapping.role_name,
                role_mapping.description,
                role_mapping.icon,
                i
            ))
    return items

def get_role_settings(context, role_name):
    """
    Obtém as configurações para um papel específico.
    
    Args:
        context: Contexto do Blender
        role_name (str): Nome do papel
        
    Returns:
        object: Configurações do papel ou None se não encontrado
    """
    prefs = get_addon_preferences(context)
    
    for role_mapping in prefs.role_mappings:
        if role_mapping.role_name == role_name:
            return role_mapping
            
    return None

def open_role_file(context, role_name):
    """
    Abre o arquivo para o papel especificado.
    
    Args:
        context: Contexto do Blender
        role_name (str): Nome do papel
        
    Returns:
        bool: True se o arquivo foi aberto com sucesso, False caso contrário
    """
    try:
        from ..core import save_current_file
        
        blend_path = verify_role_file(context, role_name)
        if blend_path and os.path.exists(blend_path):
            save_current_file()
            bpy.ops.wm.open_mainfile(filepath=blend_path)
            return True
        return False
    except Exception as e:
        print(f"Erro ao abrir arquivo de papel {role_name}: {str(e)}")
        return False

def setup_collection_settings(collection, role_settings):
    """
    Configura as configurações de coleção com base nas configurações do papel.
    
    Args:
        collection: Coleção do Blender
        role_settings: Configurações do papel
    """
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
    """
    Configura o mundo se o papel for proprietário dele.
    
    Args:
        role_settings: Configurações do papel
    """
    if role_settings.owns_world:
        for scene in bpy.data.scenes:
            if not scene.world:
                scene.world = bpy.data.worlds.new(name=f"{role_settings.role_name}_World") 