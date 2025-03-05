"""
Seções de UI para o painel de projeto.
"""

import bpy
import os
from ...preferences import get_addon_preferences
from ...utils.path_utils import get_project_info, verify_role_file

def draw_header_section(layout, context):
    """Desenha a seção de cabeçalho do painel"""
    prefs = get_addon_preferences(context)
    
    header = layout.row(align=True)
    if context.scene.current_project:
        project_name, _, _ = get_project_info(context.scene.current_project, prefs.use_fixed_root)
        header.label(text=project_name, icon='FILE_BLEND')
        header.operator("project.load_project", text="", icon='FILE_FOLDER')
    else:
        header.operator("project.create_project", icon='FILE_NEW')
        header.operator("project.load_project", icon='FILE_FOLDER')

def draw_recent_projects_section(layout, context):
    """Desenha a seção de projetos recentes"""
    prefs = get_addon_preferences(context)
    
    if len(prefs.recent_projects) > 0:
        box = layout.box()
        row = box.row()
        row.prop(prefs, "show_all_recent", text="Recent Projects", 
                icon='DISCLOSURE_TRI_DOWN' if prefs.show_all_recent else 'DISCLOSURE_TRI_RIGHT', 
                emboss=False)
        search = row.row()
        search.alignment = 'RIGHT'
        search.prop(prefs, "recent_search", text="", icon='VIEWZOOM')
        
        if prefs.show_all_recent:
            # Filtrar projetos
            filtered_projects = [
                proj for proj in prefs.recent_projects 
                if prefs.recent_search.lower() in proj.name.lower()
            ]
            
            # Determinar quantos projetos mostrar
            display_count = len(filtered_projects) if prefs.show_all_recent else min(3, len(filtered_projects))
            
            # Área de conteúdo (só mostrar se expandido ou houver pesquisa)
            if prefs.show_all_recent or prefs.recent_search:
                content_box = box.column(align=True)
                
                for i, recent in enumerate(filtered_projects):
                    if i < display_count:
                        row = content_box.row(align=True)
                        
                        # Ícone e nome do projeto
                        sub = row.row(align=True)
                        sub.scale_x = 0.75
                        sub.label(text="", icon='FILE_FOLDER')
                        row.label(text=recent.name)
                        
                        # Botões de ação
                        buttons = row.row(align=True)
                        buttons.alignment = 'RIGHT'
                        
                        # Verificar se o modo corresponde
                        mode_matches = (prefs.use_fixed_root == recent.is_fixed_root)
                        
                        # Botão de abrir
                        op = buttons.operator(
                            "project.open_recent",
                            text="",
                            icon='RESTRICT_SELECT_OFF' if mode_matches else 'RESTRICT_SELECT_ON',
                            emboss=False,
                            depress=False
                        )
                        op.project_path = recent.path
                        op.is_fixed_root = recent.is_fixed_root
                        op.enabled = mode_matches
                        
                        # Indicador do modo do projeto
                        buttons.label(
                            text="",
                            icon='LOCKED' if recent.is_fixed_root else 'UNLOCKED'
                        )
                        
                        # Botão de remover
                        remove = buttons.operator(
                            "project.remove_recent",
                            text="",
                            icon='PANEL_CLOSE',
                            emboss=False
                        )
                        remove.project_path = recent.path
                # Mostrar contador se houver mais projetos
                remaining = len(filtered_projects) - display_count
                if remaining > 0 and not prefs.show_all_recent:
                    row = content_box.row()
                    row.alignment = 'CENTER'
                    row.scale_y = 0.5
                    row.label(text=f"... and {remaining} more project{'s' if remaining > 1 else ''}")
        else:
            box.label(text="No recent projects", icon='INFO')

def draw_shot_management_section(layout, context):
    """Desenha a seção de gerenciamento de shots"""
    layout.label(text="Shot Management:", icon='SEQUENCE')
    shot_box = layout.box()
    
    # Primeira linha: Criar/Abrir Shot
    shot_row = shot_box.row(align=True)
    shot_row.scale_y = 1.2
    if context.scene.current_shot:
        shot_row.label(text=context.scene.current_shot, icon='SEQUENCE')
        shot_row.operator("project.create_shot", text="New Shot", icon='ADD')
        shot_row.operator("project.open_shot", text="", icon='FILE_FOLDER')
    else:
        shot_row.operator("project.create_shot", text="New Shot", icon='ADD')
        shot_row.operator("project.open_shot", text="Open Shot", icon='FILE_FOLDER')

def draw_role_management_section(layout, context, panel_instance):
    """Desenha a seção de gerenciamento de papéis"""
    if not context.scene.current_shot:
        return
        
    prefs = get_addon_preferences(context)
    
    layout.label(text="Role Management:", icon='GROUP')
    role_box = layout.box()
    
    # Grid de Roles com mais espaço
    grid = role_box.grid_flow(
        row_major=True,
        columns=4,
        even_columns=True,
        even_rows=True,
        align=True
    )
    
    for role_mapping in prefs.role_mappings:
        if role_mapping.show_status:
            # Célula com padding
            cell = grid.column(align=True)
            cell.scale_y = 1.2  # Aumenta altura como o botão New Shot
            
            # Adiciona espaço entre células
            cell.separator(factor=0.3)
            
            # Botão principal
            blend_path = verify_role_file(context, role_mapping.role_name)
            if blend_path:
                button = cell.operator(
                    "project.open_role_file",
                    text=role_mapping.role_name,
                    icon=role_mapping.icon,
                    depress=True
                )
                button.role_name = role_mapping.role_name
            else:
                # Dois botões quando o arquivo não existe
                row = cell.row(align=True)
                
                # Botão para criar um novo arquivo diretamente
                create_button = row.operator(
                    "project.create_role_file",
                    text=role_mapping.role_name,
                    icon=role_mapping.icon
                )
                create_button.role_name = role_mapping.role_name
                create_button.file_name = f"{context.scene.current_project.split(os.sep)[-1]}_{context.scene.current_shot}_{role_mapping.role_name}"
                
                # Botão para criar shot (como antes)
                shot_button = row.operator(
                    "project.create_shot",
                    text="",
                    icon='ADD'
                )
                shot_button.shot_name = context.scene.current_shot
                shot_button.role_name = role_mapping.role_name
            
            # Adiciona espaço após cada célula
            cell.separator(factor=0.3)
    
    # Link Role button
    role_box.separator(factor=0.5)
    role_box.operator("project.link_role", icon='LINK_BLEND', text="Link Role")

def draw_current_role_tools_section(layout, context):
    """Desenha a seção de ferramentas do papel atual"""
    if not context.scene.current_role:
        return
        
    layout.label(text="Current Role:", icon='TOOL_SETTINGS')
    tools_box = layout.box()
    
    # Version Control
    version_col = tools_box.column(align=True)
    version_col.scale_y = 1.1
    
    # WIP Row
    wip_row = version_col.row(align=True)
    wip_row.operator("project.new_wip_version", text="New WIP", icon='FILE_NEW')
    wip_row.operator("project.open_latest_wip", text="Latest WIP", icon='FILE_TICK')
    
    # Publish
    version_col.operator("project.publish_version", text="Publish Version", icon='EXPORT')
    
    # Asset Tools
    asset_row = tools_box.row(align=True)
    asset_row.scale_y = 1.1
    asset_row.operator("project.create_asset", icon='ADD', text="New Asset")
    asset_row.operator("project.toggle_asset_browser", text="Asset Browser", icon='ASSET_MANAGER')

def draw_assembly_tools_section(layout, context):
    """Desenha a seção de ferramentas de montagem"""
    if not context.scene.current_shot:
        return
        
    layout.label(text="Assembly:", icon='SCENE_DATA')
    assembly_box = layout.box()
    assembly_row = assembly_box.row(align=True)
    assembly_row.scale_y = 1.1
    is_assembly = bpy.data.is_saved and "_ASSEMBLY.blend" in os.path.basename(bpy.data.filepath)
    
    if is_assembly:
        assembly_row.operator("project.rebuild_assembly", text="Rebuild", icon='FILE_REFRESH')
        assembly_row.operator("project.prepare_assembly_render", text="Prepare Render", icon='RENDER_STILL')
    else:
        assembly_row.operator("project.open_assembly", text="Open Assembly", icon='SCENE_DATA')

def draw_utilities_section(layout, context):
    """Desenha a seção de utilitários"""
    prefs = get_addon_preferences(context)
    
    # Verifica se o asset browser está configurado
    has_asset_browser = False
    if context.scene.current_project:
        project_name, _, _ = get_project_info(context.scene.current_project, prefs.use_fixed_root)
        for lib in context.preferences.filepaths.asset_libraries:
            if lib.name == project_name:
                has_asset_browser = True
                break
    
    layout.label(text="Utilities:", icon='TOOL_SETTINGS')
    utils_box = layout.box()
    utils_row = utils_box.row(align=True)
    utils_row.scale_y = 0.9
    utils_row.operator("project.open_current_directory", text="Open Directory", icon='FILE_FOLDER')
    if has_asset_browser:
        utils_row.operator("project.reload_links", text="Reload Links", icon='FILE_REFRESH') 