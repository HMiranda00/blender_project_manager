import bpy
import os
import shutil
from bpy.types import Operator
from datetime import datetime
from ..utils import get_project_info, get_publish_path
from ..utils.versioning import get_next_version_path, redirect_to_latest_wip

class PROJECTMANAGER_OT_create_version(Operator):
    bl_idname = "project.create_version"
    bl_label = "Nova Versão"
    bl_description = "Cria uma nova versão do arquivo atual"
    
    def execute(self, context):
        try:
            if not context.scene.current_project or not context.scene.current_shot:
                self.report({'ERROR'}, "Carregue um shot ou cena primeiro")
                return {'CANCELLED'}

            if not context.scene.current_role:
                self.report({'ERROR'}, "Cargo não definido")
                return {'CANCELLED'}

            # Obter caminho da próxima versão
            next_version = get_next_version_path(context)
            if not next_version:
                self.report({'ERROR'}, "Erro ao gerar caminho da próxima versão")
                return {'CANCELLED'}
            
            # Salvar como nova versão
            bpy.ops.wm.save_as_mainfile(filepath=next_version)
            
            # Abrir o arquivo recém criado
            bpy.ops.wm.open_mainfile(filepath=next_version)
            
            self.report({'INFO'}, f"Nova versão criada: {os.path.basename(next_version)}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao criar versão: {str(e)}")
            return {'CANCELLED'}

class PROJECTMANAGER_OT_publish_version(Operator):
    bl_idname = "project.publish_version"
    bl_label = "Publicar Versão"
    bl_description = "Publica a versão atual do arquivo"
    
    def execute(self, context):
        try:
            if not bpy.data.is_saved:
                self.report({'ERROR'}, "Salve o arquivo antes de publicar")
                return {'CANCELLED'}
            
            # Verificar se é um arquivo WIP
            if "_WIP_" not in bpy.data.filepath:
                self.report({'ERROR'}, "Apenas arquivos WIP podem ser publicados")
                return {'CANCELLED'}
                
            # Obter informações do projeto
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            project_path = context.scene.current_project
            shot_name = context.scene.current_shot
            role_name = context.scene.current_role
            
            if not all([project_path, shot_name, role_name]):
                self.report({'ERROR'}, "Projeto, shot e cargo devem estar definidos")
                return {'CANCELLED'}
            
            project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Encontrar configurações do cargo
            role_settings = None
            for role_mapping in prefs.role_mappings:
                if role_mapping.role_name == role_name:
                    role_settings = role_mapping
                    break
                    
            if not role_settings:
                self.report({'ERROR'}, f"Cargo '{role_name}' não configurado")
                return {'CANCELLED'}
                
            # Construir caminho de publicação
            publish_path = get_publish_path(
                role_settings.publish_path_preset,
                role_settings,
                context,
                project_path,
                project_name,
                shot_name,
                asset_name=''
            )
            
            # Criar pasta PUBLISH se não existir
            os.makedirs(publish_path, exist_ok=True)
            
            # Nome do arquivo publicado com cargo
            publish_file = f"{project_prefix}_{shot_name}_{role_name}.blend"
            publish_filepath = os.path.join(publish_path, publish_file)
            
            # Salvar arquivo atual
            bpy.ops.wm.save_mainfile()
            
            # Copiar para PUBLISH
            shutil.copy2(bpy.data.filepath, publish_filepath)
            
            # Registrar timestamp da publicação
            publish_time = datetime.now()
            context.scene.last_publish_time = publish_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Forçar atualização de todas as áreas
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()
            
            self.report({'INFO'}, f"Arquivo publicado: {publish_file}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao publicar: {str(e)}")
            return {'CANCELLED'}

class PROJECTMANAGER_OT_open_latest_wip(Operator):
    bl_idname = "project.open_latest_wip"
    bl_label = "Abrir Último WIP"
    bl_description = "Abre a versão WIP mais recente deste arquivo"
    
    def execute(self, context):
        try:
            if not bpy.data.is_saved:
                self.report({'ERROR'}, "Salve o arquivo atual primeiro")
                return {'CANCELLED'}
            
            # Obter caminho do publish correspondente
            current_file = bpy.data.filepath
            if "_WIP_" in current_file:
                # Se já estiver em um WIP, usar o publish correspondente
                publish_file = os.path.dirname(os.path.dirname(current_file))
                publish_file = os.path.join(publish_file, "PUBLISH", os.path.basename(current_file).split("_WIP_")[0] + ".blend")
            else:
                # Se estiver no publish, usar o próprio arquivo
                publish_file = current_file
            
            # Verificar se existe WIP e redirecionar
            should_redirect, wip_path = redirect_to_latest_wip(context, publish_file)
            if should_redirect and wip_path:
                bpy.ops.wm.open_mainfile(filepath=wip_path)
                self.report({'INFO'}, f"Abrindo último WIP: {os.path.basename(wip_path)}")
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "Nenhum arquivo WIP encontrado")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao abrir último WIP: {str(e)}")
            return {'CANCELLED'}

class PROJECTMANAGER_OT_open_publish(Operator):
    bl_idname = "project.open_publish"
    bl_label = "Abrir Publicação"
    bl_description = "Abre a versão publicada deste arquivo"
    
    def execute(self, context):
        try:
            if not bpy.data.is_saved:
                self.report({'ERROR'}, "Salve o arquivo atual primeiro")
                return {'CANCELLED'}
            
            current_file = bpy.data.filepath
            if "_WIP_" not in current_file:
                self.report({'ERROR'}, "Este não é um arquivo WIP")
                return {'CANCELLED'}
            
            # Construir caminho do arquivo publicado
            publish_path = os.path.dirname(os.path.dirname(current_file))
            publish_file = os.path.basename(current_file).replace("_WIP_", "_").split("_", 4)[0:3]
            publish_file = "_".join(publish_file) + ".blend"
            publish_filepath = os.path.join(publish_path, "PUBLISH", publish_file)
            
            if os.path.exists(publish_filepath):
                bpy.ops.wm.open_mainfile(filepath=publish_filepath)
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Arquivo publicado não encontrado")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao abrir publicação: {str(e)}")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(PROJECTMANAGER_OT_create_version)
    bpy.utils.register_class(PROJECTMANAGER_OT_publish_version)
    bpy.utils.register_class(PROJECTMANAGER_OT_open_latest_wip)
    bpy.utils.register_class(PROJECTMANAGER_OT_open_publish)

def unregister():
    bpy.utils.unregister_class(PROJECTMANAGER_OT_open_publish)
    bpy.utils.unregister_class(PROJECTMANAGER_OT_open_latest_wip)
    bpy.utils.unregister_class(PROJECTMANAGER_OT_publish_version)
    bpy.utils.unregister_class(PROJECTMANAGER_OT_create_version) 