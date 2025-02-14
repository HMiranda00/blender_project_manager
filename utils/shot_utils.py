"""
Shot utilities
"""
import bpy
import os
from .project_utils import get_project_roles, get_project_shots, get_addon_prefs
from .. import i18n

def get_existing_roles(shot_path):
    """Get list of roles that exist in a shot folder"""
    roles = []
    if os.path.exists(shot_path):
        for item in os.listdir(shot_path):
            item_path = os.path.join(shot_path, item)
            if os.path.isdir(item_path) and item not in {'ASSEMBLY', '!LOCAL', '_WIP', 'ASSETS 3D'}:
                roles.append(item)
    return sorted(roles)

def update_shot_list(context=None):
    """Update the shot and role lists"""
    if not context:
        context = bpy.context
    
    try:
        # Verificar contexto
        if not hasattr(context.scene, "shot_list") or not hasattr(context.scene, "role_list"):
            print("Listas não encontradas no contexto")
            return False
            
        if not hasattr(context.scene, "project_settings"):
            print("Configurações do projeto não encontradas")
            return False
            
        # Get project path
        project_path = context.scene.current_project
        if not project_path or not os.path.exists(project_path):
            print("Projeto não encontrado ou inválido")
            return False
            
        # Get project settings
        settings = context.scene.project_settings
        
        # Clear lists
        context.scene.shot_list.clear()
        context.scene.role_list.clear()
        
        # Get shots
        shots = get_project_shots(project_path)
        
        # Debug
        print(f"\nUpdate Shot List:")
        print(f"Project path: {project_path}")
        print(f"Shots encontrados: {shots}")
        print(f"Shot atual: {context.scene.current_shot}")
        
        # Add shots to list
        for shot in shots:
            if shot not in {'ASSEMBLY', '!LOCAL', '_WIP', 'ASSETS 3D'}:
                item = context.scene.shot_list.add()
                item.name = shot
                item.type = "SHOT"
                item.icon = "SEQUENCE"
        
        # Se estiver em modo TEAM e tiver um shot selecionado, mostrar todos os cargos
        if settings.project_type == 'TEAM' and context.scene.current_shot:
            # Get role info from preferences
            prefs = get_addon_prefs()
            if prefs and prefs.role_mappings:
                print("Adicionando cargos disponíveis:")
                for role in prefs.role_mappings:
                    if role.role_name != "ASSEMBLY":  # Não incluir o cargo ASSEMBLY
                        role_item = context.scene.role_list.add()
                        role_item.name = role.role_name
                        role_item.type = "ROLE"
                        role_item.icon = role.icon
                        role_item.is_linked = False
                        print(f"- {role.role_name}")
            
        # Save context to file
        from ..core.project_context import save_project_context
        save_project_context()
        
        return True
        
    except Exception as e:
        print(f"Erro atualizando listas: {str(e)}")
        import traceback
        traceback.print_exc()
        return False 