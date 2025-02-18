import bpy
import os
from bpy.types import Operator
from bpy.props import IntProperty, EnumProperty
from ..utils import (
    get_publish_path, 
    save_current_file, 
    get_project_info,
    setup_collection_settings,
    setup_role_world
)
from ..utils.cache import DirectoryCache

class CreateShotOperator(Operator):
    bl_idname = "project.create_shot"
    bl_label = "Criar Novo Shot"

    shot_number: IntProperty(
        name="Número do Shot",
        default=1,
        min=1
    )

    def get_roles(self, context):
        prefs = context.preferences.addons['project_manager'].preferences
        return [(rm.role_name, rm.role_name, rm.description, rm.icon, i)
                for i, rm in enumerate(prefs.role_mappings)]

    role: EnumProperty(
        name="Seu Cargo",
        description="Selecione seu cargo para este shot",
        items=get_roles
    )

    def check_preferences(self, context):
        prefs = context.preferences.addons['project_manager'].preferences
        missing = []

        if len(prefs.role_mappings) == 0:
            missing.append("Configurações de Cargos")

        return missing

    def execute(self, context):
        try:
            save_current_file()
            
            prefs = context.preferences.addons['project_manager'].preferences
            project_path = context.scene.current_project

            if not project_path or not os.path.exists(project_path):
                self.report({'ERROR'}, "Nenhum projeto selecionado.")
                return {'CANCELLED'}

            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            shot_name = f"SHOT_{str(self.shot_number).zfill(3)}"
            
            role_settings = None
            for role_mapping in prefs.role_mappings:
                if role_mapping.role_name == self.role:
                    role_settings = role_mapping
                    break

            if not role_settings:
                self.report({'ERROR'}, f"Cargo '{self.role}' não configurado nas preferências.")
                return {'CANCELLED'}

            publish_path = get_publish_path(
                role_settings.publish_path_preset,
                role_settings,
                context,
                project_path,
                project_name,
                shot_name,
                asset_name=''
            )
            publish_path = bpy.path.abspath(publish_path)
            os.makedirs(publish_path, exist_ok=True)

            # Verificar se o arquivo existe usando cache
            blend_filename = f"{project_prefix}_{shot_name}_{self.role}.blend"
            files = DirectoryCache.get_files(publish_path)
            if blend_filename in files:
                self.report({'ERROR'}, f"Shot já existe: {blend_filename}")
                return {'CANCELLED'}

            # Se não existe, criar novo arquivo
            bpy.ops.wm.read_homefile(use_empty=True)

            # Configurar cena
            context.scene.name = shot_name

            # Criar collection principal
            main_collection = bpy.data.collections.new(self.role)
            context.scene.collection.children.link(main_collection)
            context.view_layer.active_layer_collection = context.view_layer.layer_collection.children[self.role]

            # Configurar collection e world
            setup_collection_settings(main_collection, role_settings)
            setup_role_world(role_settings)

            # Salvar arquivo principal do shot
            blend_path = os.path.join(publish_path, blend_filename)
            bpy.ops.wm.save_as_mainfile(filepath=blend_path)
            # Invalidar cache após criar arquivo
            DirectoryCache.invalidate(publish_path)

            # Criar/atualizar assembly apenas se o cargo não estiver marcado para ignorar
            if not role_settings.skip_assembly:
                assembly_path = os.path.join(workspace_path, "SHOTS", "ASSEMBLY")
                os.makedirs(assembly_path, exist_ok=True)
                assembly_file = f"{project_prefix}_{shot_name}_ASSEMBLY.blend"
                assembly_filepath = os.path.join(assembly_path, assembly_file)

                # Salvar arquivo atual
                current_filepath = bpy.data.filepath

                # Verificar assembly existente usando cache
                assembly_files = DirectoryCache.get_files(assembly_path)
                assembly_exists = assembly_file in assembly_files

                # Se não existe, criar novo. Se existe, atualizar
                if not assembly_exists:
                    bpy.ops.wm.read_homefile(use_empty=True)
                    context.scene.name = shot_name
                else:
                    bpy.ops.wm.open_mainfile(filepath=assembly_filepath)

                # Remover collection antiga se existir (para atualizar)
                if self.role in bpy.data.collections:
                    collection = bpy.data.collections[self.role]
                    if collection.name in context.scene.collection.children:
                        context.scene.collection.children.unlink(collection)
                    bpy.data.collections.remove(collection)

                # Linkar o cargo
                with bpy.data.libraries.load(blend_path, link=True) as (data_from, data_to):
                    data_to.collections = [self.role]
                    if role_settings.owns_world:
                        data_to.worlds = [name for name in data_from.worlds]

                # Adicionar à cena
                for coll in data_to.collections:
                    if coll is not None:
                        context.scene.collection.children.link(coll)
                        setup_collection_settings(coll, role_settings)

                # Configurar world se necessário
                if role_settings.owns_world and len(data_to.worlds) > 0:
                    context.scene.world = data_to.worlds[0]

                # Salvar assembly
                bpy.ops.wm.save_as_mainfile(filepath=assembly_filepath)
                # Invalidar cache após criar/atualizar assembly
                DirectoryCache.invalidate(assembly_path)
                
                # Voltar para o arquivo do shot
                bpy.ops.wm.open_mainfile(filepath=current_filepath)

            # Estas linhas devem estar fora do if skip_assembly
            # Atualizar informações da cena
            context.scene.current_project = project_path
            context.scene.current_shot = shot_name
            context.scene.current_role = self.role

            self.report({'INFO'}, f"Shot criado e arquivo salvo em: {blend_path}")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Erro ao criar shot: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        missing_prefs = self.check_preferences(context)
        if missing_prefs:
            self.report({'ERROR'}, f"Configure as seguintes preferências primeiro: {', '.join(missing_prefs)}")
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
            return {'CANCELLED'}

        if not context.scene.current_project:
            self.report({'ERROR'}, "Por favor, selecione ou crie um projeto primeiro.")
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self)

def register():
    bpy.utils.register_class(CreateShotOperator)

def unregister():
    bpy.utils.unregister_class(CreateShotOperator)