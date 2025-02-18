import bpy
import os
from bpy.types import Panel
from ..utils import get_project_info, get_publish_path, save_current_file
from ..utils.cache import DirectoryCache

class PROJECT_PT_Panel(Panel):
    bl_label = "Gerenciador de Projetos"
    bl_idname = "VIEW3D_PT_project_management"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Projeto'
    
    def verify_role_file(self, context, role_name):
        """Verifica se existe arquivo para o cargo especificado"""
        try:
            if not (context.scene.current_project and context.scene.current_shot):
                return None
                
            project_path = context.scene.current_project
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            shot_name = context.scene.current_shot
            
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
                asset_name=role_name
            )
            
            blend_filename = f"{project_prefix}_{shot_name}_{role_name}.blend"
            blend_path = os.path.join(publish_path, blend_filename)
            
            return blend_path if os.path.exists(blend_path) else None
            
        except Exception as e:
            print(f"Erro ao verificar arquivo do cargo {role_name}: {str(e)}")
            return None
    
    def open_role_file(self, context, role_name):
        """Abre o arquivo do cargo especificado"""
        try:
            blend_path = self.verify_role_file(context, role_name)
            if blend_path and os.path.exists(blend_path):
                save_current_file()
                bpy.ops.wm.open_mainfile(filepath=blend_path)
                return True
            return False
        except Exception as e:
            print(f"Erro ao abrir arquivo do cargo {role_name}: {str(e)}")
            return False
    
    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        
        # Projetos Recentes
        if not context.scene.current_project:
            # Cabeçalho expansível
            box = layout.box()
            header = box.row(align=True)
            header.alignment = 'LEFT'
            
            # Triângulo de expansão
            icon = 'DISCLOSURE_TRI_DOWN' if prefs.show_all_recent else 'DISCLOSURE_TRI_RIGHT'
            header.prop(
                prefs,
                "show_all_recent",
                text="",
                icon=icon,
                emboss=False
            )
            
            # Título e botões do cabeçalho
            header.label(text="Projetos Recentes")
            header_buttons = header.row(align=True)
            header_buttons.alignment = 'RIGHT'
            header_buttons.prop(prefs, "recent_search", text="", icon='VIEWZOOM')
            header_buttons.operator("project.clear_recent_list", text="", icon='X', emboss=False)
            
            if len(prefs.recent_projects) > 0:
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
                        row.label(text=f"... e mais {remaining} projeto{'s' if remaining > 1 else ''}")
            else:
                box.label(text="Nenhum projeto recente", icon='INFO')
        
        # Current Project
        box = layout.box()
        box.label(text="Projeto Atual:")
        
        if context.scene.current_project:
            project_path = context.scene.current_project
            
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            box.label(text=f"Projeto: {project_name}")
            box.label(text=f"Workspace: {workspace_path}")
            box.label(text=f"Shot: {context.scene.current_shot or 'Nenhum'}")
            box.label(text=f"Cargo: {context.scene.current_role or 'Nenhum'}")
            
            # Role Status
            if context.scene.current_shot:
                status_box = layout.box()
                status_box.label(text="Status dos Cargos", icon='INFO')
                
                grid = status_box.grid_flow(
                    row_major=True,
                    columns=4,
                    even_columns=True,
                    even_rows=True
                )
                
                for role_mapping in prefs.role_mappings:
                    if role_mapping.show_status:
                        blend_path = self.verify_role_file(context, role_mapping.role_name)
                        
                        col = grid.column()
                        box = col.box()
                        button = box.operator(
                            "project.open_role_file",
                            text="",
                            icon=role_mapping.icon,
                            depress=(blend_path is not None)
                        )
                        if button:
                            button.role_name = role_mapping.role_name

        # Main buttons
        box = layout.box()
        if not context.scene.current_project:
            if prefs.use_fixed_root:
                box.operator("project.create_project", icon='FILE_NEW', text="Criar Novo Projeto (Raiz Fixa)")
            else:
                box.operator("project.create_project", icon='FILE_NEW', text="Criar Novo Projeto")
        box.operator("project.load_project", icon='FILE_FOLDER')
        
        # Shot Management
        if context.scene.current_project:
            shot_box = layout.box()
            shot_box.label(text="Shot:", icon='SEQUENCE')
            row = shot_box.row(align=True)
            row.operator("project.create_shot", icon='ADD')
            row.operator("project.open_shot", icon='FILE_FOLDER')
            
            if context.scene.current_shot:
                shot_box.operator("project.link_role", icon='LINK_BLEND')
            
        # Asset Manager com layout melhorado
        asset_box = layout.box()
        header_row = asset_box.row()
        header_row.prop(
            context.scene,
            "show_asset_manager",
            icon='TRIA_DOWN' if context.scene.show_asset_manager else 'TRIA_RIGHT',
            icon_only=True,
            emboss=False
        )
        header_row.label(text="Gerenciador de Assets", icon='ASSET_MANAGER')

        if context.scene.show_asset_manager:
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            project_path = context.scene.current_project
            project_name, _, _ = get_project_info(project_path, prefs.use_fixed_root)
            
            # Verificar se existe Asset Browser configurado
            has_asset_browser = False
            for lib in context.preferences.filepaths.asset_libraries:
                if lib.name == project_name and "ASSETS 3D" in bpy.path.abspath(lib.path):
                    has_asset_browser = True
                    break
            
            if has_asset_browser:
                # Layout melhorado quando o Asset Browser está configurado
                col = asset_box.column(align=True)
                
                # Primeira linha: Criar Asset e Browser
                row1 = col.row(align=True)
                row1.scale_y = 1.2
                row1.operator("project.create_asset", icon='ADD', text="Criar Asset")
                row1.operator("project.toggle_asset_browser", icon='WINDOW', text="Abrir Browser")
                
                # Separador
                col.separator(factor=0.7)
                
                # Segunda linha: Gerenciamento
                row2 = col.row(align=True)
                row2.scale_y = 0.9
                row2.operator("project.reload_link", icon='FILE_REFRESH', text="Recarregar Links")
            else:
                # Layout quando não há Asset Browser configurado
                col = asset_box.column(align=True)
                
                # Mensagem informativa
                info_box = col.box()
                info_box.scale_y = 0.9
                info_box.label(text="Asset Browser não configurado", icon='INFO')
                
                # Botões
                row = col.row(align=True)
                row.scale_y = 1.2
                row.operator("project.setup_asset_browser", icon='ASSET_MANAGER', text="Configurar Browser")
                row.operator("project.reload_link", icon='FILE_REFRESH', text="Recarregar Links")

def register():
    bpy.utils.register_class(PROJECT_PT_Panel)
    
def unregister():
    bpy.utils.unregister_class(PROJECT_PT_Panel)