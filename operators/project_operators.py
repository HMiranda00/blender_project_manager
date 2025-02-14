import bpy
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty
import os
import re
from ..utils import (
    get_project_info, 
    get_publish_path,
    save_current_file
)
from ..utils.versioning import (
    redirect_to_latest_wip,
    create_first_wip
)
from ..utils.cache import DirectoryCache

class SaveContextOperator(Operator):
    bl_idname = "project.save_context"
    bl_label = "Salvar Contexto"
    bl_description = "Salva o contexto do projeto atual"
    
    project_path: StringProperty(
        name="Project Path",
        description="Caminho do projeto",
        default=""
    )
    
    shot_name: StringProperty(
        name="Shot Name",
        description="Nome do shot",
        default=""
    )
    
    role_name: StringProperty(
        name="Role Name",
        description="Nome do cargo",
        default=""
    )
    
    def execute(self, context):
        context.scene.current_project = self.project_path
        context.scene.current_shot = self.shot_name
        context.scene.current_role = self.role_name
        return {'FINISHED'}

class SetContextOperator(Operator):
    bl_idname = "project.set_context"
    bl_label = "Set Context"
    bl_description = "Define o contexto do projeto"
    
    project_path: StringProperty(default="")
    shot_name: StringProperty(default="")
    role_name: StringProperty(default="")
    
    def execute(self, context):
        if self.project_path:
            context.scene.current_project = self.project_path
        if self.shot_name:
            context.scene.current_shot = self.shot_name
        if self.role_name:
            context.scene.current_role = self.role_name
        return {'FINISHED'}

class PROJECT_OT_open_shot(Operator):
    """Operador para abrir um shot existente"""
    bl_idname = "project.open_shot"
    bl_label = "Abrir Shot"
    bl_description = "Abre um shot existente do projeto"

    def get_shots(self, context):
        print("\n=== Debug Get Shots ===")
        
        if not context.scene.current_project:
            print("Nenhum projeto selecionado")
            return [('NONE', "Nenhum projeto selecionado", "", 'ERROR', 0)]

        try:
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            project_path = context.scene.current_project
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            print(f"Project Path: {project_path}")
            print(f"Project Name: {project_name}")
            print(f"Workspace: {workspace_path}")
            
            shots_path = os.path.join(workspace_path, "SHOTS")
            print(f"Shots Path: {shots_path}")
            
            if not os.path.exists(shots_path):
                print("Pasta SHOTS não existe")
                return [('NONE', "Pasta SHOTS não encontrada", "", 'ERROR', 0)]

            # Listar pastas
            items = []
            shot_folders = []
            
            # Primeiro coletar todas as pastas válidas
            for f in os.listdir(shots_path):
                if f not in {'ASSEMBLY', '!LOCAL', '_WIP', 'ASSETS 3D'}:
                    full_path = os.path.join(shots_path, f)
                    if os.path.isdir(full_path):
                        shot_folders.append(f)
            
            print(f"Pastas encontradas: {shot_folders}")
            
            # Processar shots regulares primeiro
            for folder in sorted(shot_folders):
                if folder.startswith("SHOT_"):
                    shot_num = folder.replace("SHOT_", "")
                    items.append((
                        folder,
                        f"Shot {shot_num}",
                        f"Shot {shot_num}",
                        'SEQUENCE',
                        len(items)
                    ))
            
            # Depois processar cenas
            for folder in sorted(shot_folders):
                if folder.startswith("SCENE_"):
                    scene_name = folder.replace("SCENE_", "")
                    items.append((
                        folder,
                        f"Cena: {scene_name}",
                        f"Cena única: {scene_name}",
                        'SCENE_DATA',
                        len(items)
                    ))

            print(f"Items processados: {items}")
            
            if not items:
                return [('NONE', "Nenhum shot encontrado", "", 'ERROR', 0)]
            
            return items

        except Exception as e:
            print(f"Erro ao listar shots: {str(e)}")
            import traceback
            traceback.print_exc()
            return [('ERROR', "Erro ao listar shots", str(e), 'ERROR', 0)]

    def get_roles(self, context):
        """Lista todos os cargos configurados"""
        try:
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            return [(rm.role_name, rm.role_name, rm.description, rm.icon, i) 
                    for i, rm in enumerate(prefs.role_mappings)]
        except Exception as e:
            print(f"Erro ao listar cargos: {str(e)}")
            return [('NONE', "Erro ao listar cargos", "", 'ERROR', 0)]

    shot_to_open: EnumProperty(
        name="Shot",
        description="Selecione o shot para abrir",
        items=get_shots
    )

    selected_role: EnumProperty(
        name="Cargo",
        description="Selecione o cargo para abrir",
        items=get_roles
    )

    def execute(self, context):
        try:
            if not self.shot_to_open or self.shot_to_open in {'NONE', 'ERROR'}:
                self.report({'ERROR'}, "Selecione um shot válido")
                return {'CANCELLED'}

            if not self.selected_role:
                self.report({'ERROR'}, "Selecione um cargo")
                return {'CANCELLED'}

            # Salvar arquivo atual se necessário
            if bpy.data.is_saved and bpy.data.is_dirty:
                bpy.ops.wm.save_mainfile()

            # Obter informações do projeto
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            project_path = context.scene.current_project
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)

            # Encontrar configurações do cargo
            role_settings = None
            for role_mapping in prefs.role_mappings:
                if role_mapping.role_name == self.selected_role:
                    role_settings = role_mapping
                    break

            if not role_settings:
                self.report({'ERROR'}, f"Configurações do cargo '{self.selected_role}' não encontradas")
                return {'CANCELLED'}

            # Obter caminho do publish
            publish_path = get_publish_path(
                role_settings.publish_path_preset,
                role_settings,
                context,
                project_path,
                project_name,
                self.shot_to_open,
                asset_name=self.selected_role
            )

            # Nome base do arquivo
            blend_file = f"{project_prefix}_{self.shot_to_open}_{self.selected_role}.blend"
            publish_filepath = os.path.join(publish_path, blend_file)

            # Atualizar contexto em qualquer caso
            context.scene.current_shot = self.shot_to_open
            context.scene.current_role = self.selected_role

            # Verificar se existe arquivo publicado
            if os.path.exists(publish_filepath):
                # Verificar se existe WIP mais recente
                should_redirect, wip_path = redirect_to_latest_wip(context, publish_filepath)
                
                if should_redirect and wip_path:
                    # Abrir último WIP
                    bpy.ops.wm.open_mainfile(filepath=wip_path)
                    self.report({'INFO'}, f"Último WIP do shot {self.shot_to_open} aberto")
                else:
                    # Se não há WIP, criar primeiro WIP
                    wip_path = create_first_wip(context, publish_filepath)
                    if wip_path:
                        bpy.ops.wm.open_mainfile(filepath=wip_path)
                        self.report({'INFO'}, f"Primeiro WIP do shot {self.shot_to_open} criado e aberto")
                    else:
                        self.report({'ERROR'}, "Erro ao criar primeiro WIP")
                        return {'CANCELLED'}
            else:
                self.report({'WARNING'}, f"Arquivo do shot não encontrado: {publish_filepath}")

            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao abrir shot: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        if not context.scene.current_project:
            self.report({'ERROR'}, "Selecione um projeto primeiro")
            return {'CANCELLED'}
            
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        
        # Mostrar projeto atual
        box = layout.box()
        box.label(text="Projeto Atual:", icon='FILE_FOLDER')
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        project_name, _, _ = get_project_info(context.scene.current_project, prefs.use_fixed_root)
        box.label(text=project_name)
        
        # Seleção de shot
        layout.prop(self, "shot_to_open")
        layout.prop(self, "selected_role")

def register():
    bpy.utils.register_class(SaveContextOperator)
    bpy.utils.register_class(SetContextOperator)
    bpy.utils.register_class(PROJECT_OT_open_shot)

def unregister():
    bpy.utils.unregister_class(SaveContextOperator)
    bpy.utils.unregister_class(SetContextOperator)
    bpy.utils.unregister_class(PROJECT_OT_open_shot) 