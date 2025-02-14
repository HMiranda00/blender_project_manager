import bpy
import os
from datetime import datetime
from bpy.types import Operator
from bpy.props import BoolProperty
from ..utils import (
    get_project_info, 
    get_publish_path,
    show_progress_status,
    get_assembly_role,
    is_assembly_role
)

class PrepareAssemblyForRenderOperator(Operator):
    bl_idname = "project.prepare_assembly_render"
    bl_label = "Preparar para Render"
    bl_description = "Prepara uma cópia local do assembly para renderização"
    
    purge_data: BoolProperty(
        name="Limpar Dados Não Utilizados",
        description="Remove todos os dados não utilizados do arquivo",
        default=True
    )
    
    make_local: BoolProperty(
        name="Tornar Local",
        description="Converte todos os dados linkados em locais",
        default=True
    )
    
    pack_resources: BoolProperty(
        name="Empacotar Recursos",
        description="Empacota todas as texturas e recursos externos no arquivo",
        default=True
    )
    
    check_missing: BoolProperty(
        name="Verificar Arquivos Faltantes",
        description="Gera relatório de arquivos faltantes",
        default=True
    )
    
    def execute(self, context):
        if not is_assembly_role(context.scene.current_role):
            self.report({'ERROR'}, "Esta operação só pode ser executada no cargo Assembly")
            return {'CANCELLED'}
        try:
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            project_path = context.scene.current_project
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            shot_name = context.scene.current_shot
            
            # Criar diretório !LOCAL com subpasta da data
            local_path = os.path.join(workspace_path, "SHOTS", "!LOCAL")
            date_folder = datetime.now().strftime("%d-%m-%Y")
            render_path = os.path.join(local_path, date_folder)
            os.makedirs(render_path, exist_ok=True)
            
            # Nome do arquivo
            current_time = datetime.now().strftime("%H-%M")
            render_file = f"{project_prefix}_{shot_name}_ASSEMBLY_RENDER_{current_time}.blend"
            render_filepath = os.path.join(render_path, render_file)
            
            # Primeiro salvar uma cópia do arquivo atual
            bpy.ops.wm.save_as_mainfile(filepath=render_filepath, copy=True)
            
            # Reabrir o arquivo copiado
            bpy.ops.wm.open_mainfile(filepath=render_filepath)
            
            # Executar operações na ordem
            if self.purge_data:
                bpy.ops.outliner.orphans_purge(do_recursive=True)
            
            if self.make_local:
                # Tornar tudo local
                bpy.ops.object.make_local(type='ALL')
                # Tornar collections locais também
                for coll in bpy.data.collections:
                    if coll.library:
                        coll.override_create(remap_local_usages=True)
                
            if self.purge_data:
                bpy.ops.outliner.orphans_purge(do_recursive=True)
            
            if self.pack_resources:
                bpy.ops.file.pack_all()
            
            if self.check_missing:
                bpy.ops.file.report_missing_files()
            
            # Salvar arquivo local
            bpy.ops.wm.save_mainfile()
            
            self.report({'INFO'}, f"Arquivo local preparado para render: {render_filepath}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao preparar arquivo: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "purge_data")
        layout.prop(self, "make_local")
        layout.prop(self, "pack_resources")
        layout.prop(self, "check_missing")

class CleanMissingFilesOperator(Operator):
    bl_idname = "project.clean_missing_files"
    bl_label = "Limpar Arquivos Faltantes"
    bl_description = "Remove referências a arquivos faltantes"
    
    def execute(self, context):
        try:
            # Remover texturas faltantes
            for image in bpy.data.images:
                if image.filepath and not os.path.exists(bpy.path.abspath(image.filepath)):
                    bpy.data.images.remove(image)
            
            # Remover bibliotecas faltantes
            for library in bpy.data.libraries:
                if not os.path.exists(bpy.path.abspath(library.filepath)):
                    bpy.data.libraries.remove(library)
            
            # Purge final
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            
            self.report({'INFO'}, "Arquivos faltantes removidos")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao limpar arquivos: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

class RebuildAssemblyOperator(Operator):
    bl_idname = "project.rebuild_assembly"
    bl_label = "Reconstruir Assembly"
    bl_description = "Reconstrói o assembly do zero usando os arquivos dos cargos"
    
    def execute(self, context):
        try:
            wm = context.window_manager
            wm.assembly_progress = 0.0  # Iniciar progresso
            
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            project_path = context.scene.current_project
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            shot_name = context.scene.current_shot
            
            # Contar quantos cargos serão processados
            total_roles = len([role for role in prefs.role_mappings if not role.skip_assembly])
            current_role = 0
            
            # Salvar arquivo atual antes de reconstruir
            if bpy.data.is_saved:
                context.window_manager.assembly_previous_file = bpy.data.filepath
            
            # Criar novo arquivo vazio
            bpy.ops.wm.read_homefile(use_empty=True)
            context.scene.name = shot_name
            
            # Configurar informações do projeto
            context.scene.current_project = project_path
            context.scene.current_shot = shot_name
            context.scene.current_role = get_assembly_role()
            
            wm.assembly_progress = 0.05  # 5%
            
            # Lista para controlar worlds
            linked_worlds = []
            
            # Listas para tracking
            successful_roles = []
            failed_roles = []
            
            # Para cada cargo configurado, tentar linkar
            for role_mapping in prefs.role_mappings:
                if role_mapping.skip_assembly:
                    continue
                
                current_role += 1
                wm.assembly_progress = 0.05 + (current_role / total_roles * 0.85)  # 5-90%
                
                # Construir caminho do arquivo do cargo
                role_path = get_publish_path(
                    role_mapping.publish_path_preset,
                    role_mapping,
                    context,
                    project_path,
                    project_name,
                    shot_name,
                    asset_name=role_mapping.role_name
                )
                
                blend_filename = f"{project_prefix}_{shot_name}_{role_mapping.role_name}.blend"
                blend_path = os.path.join(role_path, blend_filename)
                
                if os.path.exists(blend_path):
                    # Linkar collection
                    with bpy.data.libraries.load(blend_path, link=True) as (data_from, data_to):
                        if role_mapping.role_name not in data_from.collections:
                            failed_roles.append((role_mapping.role_name, f"Collection '{role_mapping.role_name}' não encontrada no arquivo"))
                            continue
                            
                        data_to.collections = [role_mapping.role_name]
                        
                        if role_mapping.owns_world and not role_mapping.role_name in linked_worlds:
                            data_to.worlds = [name for name in data_from.worlds]
                            linked_worlds.append(role_mapping.role_name)
                    
                    # Adicionar à cena e ao ViewLayer
                    for coll in data_to.collections:
                        if coll is not None:
                            if coll.name not in context.scene.collection.children:
                                context.scene.collection.children.link(coll)
                            
                            layer_collection = context.view_layer.layer_collection.children.get(coll.name)
                            if layer_collection:
                                layer_collection.exclude = False
                                layer_collection.hide_viewport = role_mapping.hide_viewport_default
                                successful_roles.append(role_mapping.role_name)
                            else:
                                failed_roles.append((role_mapping.role_name, "Collection não encontrada no ViewLayer"))
                else:
                    failed_roles.append((role_mapping.role_name, "Arquivo não encontrado"))
            
            # Salvar assembly
            wm.assembly_progress = 0.9  # 90%
            
            assembly_path = os.path.join(workspace_path, "SHOTS", "ASSEMBLY")
            os.makedirs(assembly_path, exist_ok=True)
            assembly_file = f"{project_prefix}_{shot_name}_ASSEMBLY.blend"
            assembly_filepath = os.path.join(assembly_path, assembly_file)
            bpy.ops.wm.save_as_mainfile(filepath=assembly_filepath)
            
            # Finalizar
            wm.assembly_progress = 1.0  # 100%
            
            message = "Assembly reconstruído.\n"
            if successful_roles:
                message += f"\nCargos linkados com sucesso: {', '.join(successful_roles)}"
            if failed_roles:
                message += f"\nCargos com problemas:"
                for role, error in failed_roles:
                    message += f"\n• {role}: {error}"
            
            self.report({'INFO'}, message)
            
            # Resetar progresso
            wm.assembly_progress = 0.0
            return {'FINISHED'}
            
        except Exception as e:
            context.window_manager.assembly_progress = 0.0  # Resetar em caso de erro
            self.report({'ERROR'}, f"Erro ao reconstruir assembly: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

def register():
    print("Registrando operadores de assembly...")
    bpy.utils.register_class(PrepareAssemblyForRenderOperator)
    print("- PrepareAssemblyForRenderOperator registrado")
    bpy.utils.register_class(CleanMissingFilesOperator)
    print("- CleanMissingFilesOperator registrado")
    bpy.utils.register_class(RebuildAssemblyOperator)
    print("- RebuildAssemblyOperator registrado")
    print("Operadores de assembly registrados com sucesso!")

def unregister():
    print("Desregistrando operadores de assembly...")
    bpy.utils.unregister_class(RebuildAssemblyOperator)
    bpy.utils.unregister_class(CleanMissingFilesOperator)
    bpy.utils.unregister_class(PrepareAssemblyForRenderOperator)

def clear_status():
    try:
        # Tentar limpar em todos os workspaces
        for workspace in bpy.data.workspaces:
            workspace.status_text_set(None)
    except:
        pass 