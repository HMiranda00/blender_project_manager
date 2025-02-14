import bpy
import os
import shutil
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty, EnumProperty
from ..utils import (
    get_project_info, 
    save_current_file, 
    get_publish_path,
    setup_collection_settings,
    setup_role_world,
    get_assembly_role,
    is_assembly_role
)

class DuplicateShotOperator(Operator):
    bl_idname = "project.duplicate_shot"
    bl_label = "Duplicar Shot"
    bl_description = "Duplica um shot existente preservando referências"

    mode: EnumProperty(
        name="Modo",
        items=[
            ('SHOT', "Shot", "Criar um novo shot numerado"),
            ('SCENE', "Cena Única", "Criar uma cena única sem numeração")
        ],
        default='SHOT'
    )

    shot_number: IntProperty(
        name="Número do Shot",
        description="Número para o novo shot",
        min=1
    )

    scene_name: StringProperty(
        name="Nome da Cena",
        default="MAIN"
    )

    def update_file_links(self, context, current_shot, new_shot_name, project_prefix):
        """Atualiza os links no arquivo atual para apontar para os novos arquivos"""
        def get_new_path(filepath, current_shot, new_shot_name):
            """Retorna o novo caminho para o arquivo"""
            # Separar o caminho em partes
            parts = filepath.split(os.sep)
            
            # Encontrar e substituir o nome do shot em cada parte do caminho
            for i, part in enumerate(parts):
                if current_shot in part:
                    # Se for o nome do arquivo .blend
                    if part.endswith('.blend'):
                        parts[i] = f"{project_prefix}_{new_shot_name}_{part.split('_')[-1]}"
                    # Se for o nome da pasta do shot
                    elif part == current_shot:
                        parts[i] = new_shot_name
            
            # Reconstruir o caminho
            return os.sep.join(parts)
        
        # Lista para guardar bibliotecas que precisam ser recarregadas
        libraries_to_reload = set()
        
        # Atualizar caminhos e coletar bibliotecas
        for collection in bpy.data.collections:
            if collection.library:
                old_path = collection.library.filepath
                new_path = get_new_path(old_path, current_shot, new_shot_name)
                print(f"Atualizando caminho da collection {collection.name}:")
                print(f"De: {old_path}")
                print(f"Para: {new_path}")
                collection.library.filepath = new_path
                libraries_to_reload.add(collection.library)
        
        for material in bpy.data.materials:
            if material.library:
                old_path = material.library.filepath
                new_path = get_new_path(old_path, current_shot, new_shot_name)
                print(f"Atualizando caminho do material {material.name}:")
                print(f"De: {old_path}")
                print(f"Para: {new_path}")
                material.library.filepath = new_path
                libraries_to_reload.add(material.library)
        
        for node_group in bpy.data.node_groups:
            if node_group.library:
                old_path = node_group.library.filepath
                new_path = get_new_path(old_path, current_shot, new_shot_name)
                print(f"Atualizando caminho do node group {node_group.name}:")
                print(f"De: {old_path}")
                print(f"Para: {new_path}")
                node_group.library.filepath = new_path
                libraries_to_reload.add(node_group.library)
        
        # Recarregar cada biblioteca
        for library in libraries_to_reload:
            try:
                print(f"Recarregando biblioteca: {library.filepath}")
                library.reload()
            except Exception as e:
                print(f"Erro ao recarregar biblioteca {library.filepath}: {str(e)}")
        
        # Forçar atualização da interface
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()

    def check_role(self, context):
        """Verifica se o cargo atual permite duplicação"""
        if is_assembly_role(context.scene.current_role):
            self.report({'ERROR'}, "Não é possível duplicar shots no cargo Assembly")
            return False
        return True

    def execute(self, context):
        try:
            if not self.check_role(context):
                return {'CANCELLED'}

            if not context.scene.current_project or not context.scene.current_shot:
                self.report({'ERROR'}, "Nenhum shot selecionado para duplicar")
                return {'CANCELLED'}

            save_current_file()
            
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            project_path = context.scene.current_project
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Determinar nome do novo shot
            if self.mode == 'SHOT':
                new_shot_name = f"SHOT_{str(self.shot_number).zfill(3)}"
            else:
                new_shot_name = self.scene_name
            
            # Verificar se o novo shot já existe
            shots_path = os.path.join(workspace_path, "SHOTS")
            if not os.path.exists(shots_path):
                self.report({'ERROR'}, f"Diretório de shots não encontrado: {shots_path}")
                return {'CANCELLED'}
            
            # Guardar informações importantes
            current_role = context.scene.current_role
            current_shot = context.scene.current_shot
            current_filepath = bpy.data.filepath
            
            # Encontrar configurações do cargo atual
            role_settings = None
            for role_mapping in prefs.role_mappings:
                if role_mapping.role_name == current_role:
                    role_settings = role_mapping
                    break
            
            if not role_settings:
                self.report({'ERROR'}, f"Cargo atual '{current_role}' não encontrado nas configurações")
                return {'CANCELLED'}
            
            # Para cada cargo configurado
            for role_mapping in prefs.role_mappings:
                # Obter caminhos do arquivo original
                original_publish_path = get_publish_path(
                    role_mapping.publish_path_preset,
                    role_mapping,
                    context,
                    project_path,
                    project_name,
                    current_shot,
                    asset_name=''
                )
                original_blend = f"{project_prefix}_{current_shot}_{role_mapping.role_name}.blend"
                original_filepath = os.path.join(original_publish_path, original_blend)
                
                # Se existe arquivo para este cargo
                if os.path.exists(original_filepath):
                    # Obter caminhos para o novo arquivo
                    new_publish_path = get_publish_path(
                        role_mapping.publish_path_preset,
                        role_mapping,
                        context,
                        project_path,
                        project_name,
                        new_shot_name,
                        asset_name=''
                    )
                    os.makedirs(new_publish_path, exist_ok=True)
                    
                    new_blend = f"{project_prefix}_{new_shot_name}_{role_mapping.role_name}.blend"
                    new_filepath = os.path.join(new_publish_path, new_blend)
                    
                    # Se for o cargo atual, atualizar o arquivo atual
                    if role_mapping.role_name == current_role:
                        # Atualizar informações da cena
                        context.scene.name = new_shot_name
                        context.scene.current_shot = new_shot_name
                        
                        # Atualizar links
                        self.update_file_links(context, current_shot, new_shot_name, project_prefix)
                        
                        # Salvar como novo arquivo
                        bpy.ops.wm.save_as_mainfile(filepath=new_filepath)
                    else:
                        # Para outros cargos, copiar e atualizar o arquivo
                        # Primeiro copiar o arquivo
                        shutil.copy2(original_filepath, new_filepath)
                        
                        # Abrir e atualizar
                        bpy.ops.wm.open_mainfile(filepath=new_filepath)
                        context.scene.name = new_shot_name
                        context.scene.current_shot = new_shot_name
                        context.scene.current_project = project_path
                        context.scene.current_role = current_role
                        
                        # Atualizar links
                        self.update_file_links(context, current_shot, new_shot_name, project_prefix)
                        
                        bpy.ops.wm.save_mainfile()
            
            # Criar/atualizar assembly
            assembly_role = get_assembly_role()
            assembly_path = os.path.join(workspace_path, "SHOTS", "ASSEMBLY")
            os.makedirs(assembly_path, exist_ok=True)
            
            # Copiar assembly existente
            original_assembly = f"{project_prefix}_{current_shot}_ASSEMBLY.blend"
            new_assembly = f"{project_prefix}_{new_shot_name}_ASSEMBLY.blend"
            original_assembly_path = os.path.join(assembly_path, original_assembly)
            new_assembly_path = os.path.join(assembly_path, new_assembly)
            
            if os.path.exists(original_assembly_path):
                # Copiar assembly
                shutil.copy2(original_assembly_path, new_assembly_path)
                
                # Abrir e atualizar assembly
                bpy.ops.wm.open_mainfile(filepath=new_assembly_path)
                context.scene.name = new_shot_name
                context.scene.current_shot = new_shot_name
                context.scene.current_project = project_path
                context.scene.current_role = assembly_role
                
                # Atualizar links
                self.update_file_links(context, current_shot, new_shot_name, project_prefix)
                
                # Salvar assembly atualizado
                bpy.ops.wm.save_mainfile()
            
            # Voltar para o arquivo do cargo atual
            new_current_path = os.path.join(
                get_publish_path(
                    role_settings.publish_path_preset,
                    role_settings,
                    context,
                    project_path,
                    project_name,
                    new_shot_name,
                    asset_name=''
                ),
                f"{project_prefix}_{new_shot_name}_{current_role}.blend"
            )
            bpy.ops.wm.open_mainfile(filepath=new_current_path)
            
            self.report({'INFO'}, f"Shot duplicado com sucesso: {new_shot_name}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao duplicar shot: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        if not context.scene.current_shot:
            self.report({'ERROR'}, "Selecione um shot para duplicar")
            return {'CANCELLED'}
            
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        project_path = context.scene.current_project
        _, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
        
        # Verificar se o diretório SHOTS existe
        shots_path = os.path.join(workspace_path, "SHOTS")
        if not os.path.exists(shots_path):
            self.report({'ERROR'}, f"Diretório de shots não encontrado: {shots_path}")
            return {'CANCELLED'}
        
        # Sugerir próximo número disponível
        existing_shots = [d for d in os.listdir(shots_path) if d.startswith("SHOT_")]
        shot_numbers = [int(s.split("_")[1]) for s in existing_shots]
        self.shot_number = max(shot_numbers, default=0) + 1
        
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        
        # Modo de criação
        layout.prop(self, "mode")
        
        # Campos específicos do modo
        if self.mode == 'SHOT':
            layout.prop(self, "shot_number")
        else:
            layout.prop(self, "scene_name")
            
        # Informações do shot atual
        box = layout.box()
        box.label(text="Shot Original:", icon='SEQUENCE')
        box.label(text=context.scene.current_shot)

def register():
    bpy.utils.register_class(DuplicateShotOperator)

def unregister():
    bpy.utils.unregister_class(DuplicateShotOperator) 