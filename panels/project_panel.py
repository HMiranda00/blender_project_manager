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
    
    def draw_header(self, context):
        """Desenha o cabeçalho do painel"""
        layout = self.layout
        layout.label(icon='COMMUNITY')
    
    def draw_project_info(self, context, layout):
        """Desenha as informações do projeto atual"""
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        project_path = context.scene.current_project
        
        if project_path:
            project_name, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
            
            # Cabeçalho do projeto
            header = layout.row(align=True)
            header.scale_y = 1.2
            header.label(text=project_name, icon='FILE_BLEND')
            
            # Informações em colunas
            info_box = layout.box()
            col = info_box.column(align=True)
            col.scale_y = 0.9
            
            # Workspace
            row = col.row()
            row.label(text="", icon='FOLDER_REDIRECT')
            row.label(text=workspace_path)
            
            # Shot e Role
            if context.scene.current_shot:
                row = col.row()
                row.label(text="", icon='SEQUENCE')
                row.label(text=context.scene.current_shot)
            
            if context.scene.current_role:
                row = col.row()
                row.label(text="", icon='TOOL_SETTINGS')
                row.label(text=context.scene.current_role)
    
    def draw_recent_projects(self, context, layout):
        """Desenha a lista de projetos recentes"""
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        
        # Cabeçalho expansível
        header = layout.row(align=True)
        header.scale_y = 1.2
        header.prop(
            prefs,
            "show_all_recent",
            text="",
            icon='DISCLOSURE_TRI_DOWN' if prefs.show_all_recent else 'DISCLOSURE_TRI_RIGHT',
            emboss=False
        )
        header.label(text="Projetos Recentes", icon='FILE_FOLDER')
        
        # Barra de busca e botão limpar
        search_row = layout.row(align=True)
        search_row.scale_y = 0.9
        search_row.prop(prefs, "recent_search", text="", icon='VIEWZOOM')
        search_row.operator("project.clear_recent_list", text="", icon='X', emboss=False)
        
        if len(prefs.recent_projects) > 0:
            # Filtrar projetos
            filtered_projects = [
                proj for proj in prefs.recent_projects 
                if prefs.recent_search.lower() in proj.name.lower()
            ]
            
            # Determinar quantos projetos mostrar
            display_count = len(filtered_projects) if prefs.show_all_recent else min(3, len(filtered_projects))
            
            if prefs.show_all_recent or prefs.recent_search:
                box = layout.box()
                col = box.column(align=True)
                
                for i, recent in enumerate(filtered_projects):
                    if i < display_count:
                        row = col.row(align=True)
                        row.scale_y = 0.9
                        
                        # Nome do projeto
                        name_row = row.row()
                        name_row.label(text="", icon='FILE_FOLDER')
                        name_row.label(text=recent.name)
                        
                        # Botões
                        buttons = row.row(align=True)
                        buttons.alignment = 'RIGHT'
                        
                        # Verificar modo
                        mode_matches = (prefs.use_fixed_root == recent.is_fixed_root)
                        
                        # Botão abrir
                        op = buttons.operator(
                            "project.open_recent",
                            text="",
                            icon='RESTRICT_SELECT_OFF' if mode_matches else 'RESTRICT_SELECT_ON',
                            emboss=False
                        )
                        op.project_path = recent.path
                        op.is_fixed_root = recent.is_fixed_root
                        op.enabled = mode_matches
                        
                        # Indicador de modo
                        buttons.label(text="", icon='LOCKED' if recent.is_fixed_root else 'UNLOCKED')
                        
                        # Botão remover
                        remove = buttons.operator(
                            "project.remove_recent",
                            text="",
                            icon='PANEL_CLOSE',
                            emboss=False
                        )
                        remove.project_path = recent.path
                
                # Contador de restantes
                remaining = len(filtered_projects) - display_count
                if remaining > 0 and not prefs.show_all_recent:
                    row = col.row()
                    row.alignment = 'CENTER'
                    row.scale_y = 0.7
                    row.label(text=f"... e mais {remaining} projeto{'s' if remaining > 1 else ''}")
        else:
            info = layout.box()
            info.scale_y = 0.9
            info.label(text="Nenhum projeto recente", icon='INFO')
    
    def draw_role_status(self, context, layout):
        """Desenha o status dos cargos"""
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        
        # Cabeçalho
        header = layout.row()
        header.scale_y = 1.2
        header.prop(
            context.scene,
            "show_role_status",
            text="",
            icon='DISCLOSURE_TRI_DOWN' if context.scene.show_role_status else 'DISCLOSURE_TRI_RIGHT',
            emboss=False
        )
        header.label(text="Status dos Cargos", icon='TOOL_SETTINGS')
        
        if context.scene.show_role_status:
            box = layout.box()
            grid = box.grid_flow(
                row_major=True,
                columns=4,
                even_columns=True,
                even_rows=True
            )
            
            for role_mapping in prefs.role_mappings:
                if role_mapping.show_status:
                    blend_path = self.verify_role_file(context, role_mapping.role_name)
                    
                    col = grid.column()
                    role_box = col.box()
                    
                    # Botão do cargo
                    button = role_box.operator(
                        "project.open_role_file" if blend_path else "project.create_shot",
                        text="",
                        icon=role_mapping.icon,
                        depress=(blend_path is not None)
                    )
                    button.role_name = role_mapping.role_name
                    if not blend_path:
                        button.shot_name = context.scene.current_shot
    
    def draw_asset_manager(self, context, layout):
        """Desenha o gerenciador de assets"""
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        
        # Cabeçalho
        header = layout.row()
        header.scale_y = 1.2
        header.prop(
            context.scene,
            "show_asset_manager",
            text="",
            icon='DISCLOSURE_TRI_DOWN' if context.scene.show_asset_manager else 'DISCLOSURE_TRI_RIGHT',
            emboss=False
        )
        header.label(text="Gerenciador de Assets", icon='ASSET_MANAGER')
        
        if context.scene.show_asset_manager:
            box = layout.box()
            
            # Verificar configuração do Asset Browser
            has_asset_browser = False
            if context.scene.current_project:
                project_name, _, _ = get_project_info(context.scene.current_project, prefs.use_fixed_root)
                for lib in context.preferences.filepaths.asset_libraries:
                    if lib.name == project_name:
                        has_asset_browser = True
                        break
            
            if has_asset_browser:
                col = box.column(align=True)
                
                # Botões principais
                row = col.row(align=True)
                row.scale_y = 1.2
                row.operator("project.create_asset", icon='ADD', text="Criar Asset")
                row.operator("project.toggle_asset_browser", icon='WINDOW', text="Abrir Browser")
                
                # Separador
                col.separator(factor=0.5)
                
                # Botão de recarga
                row = col.row()
                row.scale_y = 0.9
                row.operator("project.reload_link", icon='FILE_REFRESH', text="Recarregar Links")
            else:
                col = box.column(align=True)
                
                # Mensagem
                info = col.box()
                info.scale_y = 0.9
                info.label(text="Asset Browser não configurado", icon='INFO')
                
                # Botões
                row = col.row(align=True)
                row.scale_y = 1.2
                row.operator("project.setup_asset_browser", icon='ASSET_MANAGER', text="Configurar Browser")
    
    def draw_shot_tools(self, context, layout):
        """Desenha as ferramentas de shot"""
        # Cabeçalho
        header = layout.row()
        header.scale_y = 1.2
        header.label(text="Ferramentas de Shot", icon='SEQUENCE')
        
        box = layout.box()
        col = box.column(align=True)
        
        # Botões principais
        row = col.row(align=True)
        row.scale_y = 1.2
        row.operator("project.create_shot", icon='ADD', text="Criar Shot")
        row.operator("project.open_shot", icon='FILE_FOLDER', text="Abrir Shot")
        
        if context.scene.current_shot:
            col.separator(factor=0.5)
            
            # Botões adicionais
            row = col.row(align=True)
            row.scale_y = 0.9
            row.operator("project.link_role", icon='LINK_BLEND', text="Linkar Cargo")
            
            if context.scene.current_role:
                # Controle de versão
                col.separator(factor=0.5)
                version_box = col.box()
                version_box.label(text="Controle de Versão:", icon='RECOVER_LAST')
                
                # WIP
                row = version_box.row(align=True)
                row.scale_y = 0.9
                row.operator("project.new_wip_version", icon='FILE_NEW', text="Nova WIP")
                row.operator("project.open_latest_wip", icon='FILE_TICK', text="Última WIP")
                
                # Publish
                row = version_box.row()
                row.scale_y = 0.9
                row.operator("project.publish_version", icon='EXPORT', text="Publicar")
    
    def draw_assembly_tools(self, context, layout):
        """Desenha as ferramentas de assembly"""
        if context.scene.current_shot:
            # Cabeçalho
            header = layout.row()
            header.scale_y = 1.2
            header.label(text="Assembly", icon='SCENE_DATA')
            
            box = layout.box()
            col = box.column(align=True)
            
            # Verificar se estamos em um arquivo de assembly
            is_assembly = False
            if bpy.data.is_saved:
                current_file = os.path.basename(bpy.data.filepath)
                is_assembly = "_ASSEMBLY.blend" in current_file
            
            # Botões
            row = col.row(align=True)
            row.scale_y = 1.2
            row.operator("project.open_assembly", icon='FILE_BLEND', text="Abrir Assembly")
            
            if is_assembly:
                col.separator(factor=0.5)
                
                row = col.row(align=True)
                row.scale_y = 0.9
                row.operator("project.rebuild_assembly", icon='FILE_REFRESH', text="Reconstruir")
                row.operator("project.prepare_assembly_render", icon='RENDER_STILL', text="Preparar Render")
    
    def draw(self, context):
        layout = self.layout
        
        if not context.scene.current_project:
            # Projetos Recentes
            self.draw_recent_projects(context, layout)
            
            # Botões de projeto
            layout.separator()
            col = layout.column(align=True)
            col.scale_y = 1.2
            
            if context.preferences.addons['gerenciador_projetos'].preferences.use_fixed_root:
                col.operator("project.create_project", icon='FILE_NEW', text="Criar Novo Projeto (Raiz Fixa)")
            else:
                col.operator("project.create_project", icon='FILE_NEW', text="Criar Novo Projeto")
            
            col.operator("project.load_project", icon='FILE_FOLDER', text="Carregar Projeto")
        else:
            # Informações do Projeto
            self.draw_project_info(context, layout)
            
            layout.separator()
            
            # Shot Tools
            self.draw_shot_tools(context, layout)
            
            if context.scene.current_shot:
                layout.separator()
                
                # Assembly Tools
                self.draw_assembly_tools(context, layout)
                
                layout.separator()
                
                # Role Status
                self.draw_role_status(context, layout)
            
            layout.separator()
            
            # Asset Manager
            self.draw_asset_manager(context, layout)

def register():
    bpy.utils.register_class(PROJECT_PT_Panel)
    
def unregister():
    bpy.utils.unregister_class(PROJECT_PT_Panel)