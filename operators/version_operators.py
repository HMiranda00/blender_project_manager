"""
Version control operators for managing file versions
"""
import bpy
import os
import shutil
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from datetime import datetime
from ..utils import get_project_info, get_publish_path
from ..utils.versioning import get_next_version_path, redirect_to_latest_wip, get_version_number, get_next_version
from ..utils.project_utils import get_addon_prefs, save_current_file
from .. import i18n

class SaveVersionOperator(Operator):
    bl_idname = "project.save_version"
    bl_label = i18n.translate("Save Version")
    
    version_note: StringProperty(
        name=i18n.translate("Version Note"),
        description=i18n.translate("Note about this version"),
        default=""
    )
    
    def execute(self, context):
        try:
            # Get addon preferences
            prefs = get_addon_prefs()
            if not prefs:
                self.report({'ERROR'}, i18n.translate("Addon preferences not found"))
                return {'CANCELLED'}
            
            # Get current file path
            current_file = bpy.data.filepath
            if not current_file:
                self.report({'ERROR'}, i18n.translate("Save the file first"))
                return {'CANCELLED'}
            
            # Get next version number
            current_version = get_version_number(current_file)
            next_version = get_next_version(current_version)
            
            # Create new version path
            new_file = current_file.replace(f"v{current_version:03d}", f"v{next_version:03d}")
            
            # Save new version
            bpy.ops.wm.save_as_mainfile(filepath=new_file)
            
            # Save version note if provided
            if self.version_note:
                version_info = {
                    'version': next_version,
                    'note': self.version_note,
                    'date': bpy.utils.time.strftime("%Y-%m-%d %H:%M:%S")
                }
                version_file = os.path.join(os.path.dirname(new_file), "version_info.json")
                import json
                with open(version_file, 'w', encoding='utf-8') as f:
                    json.dump(version_info, f, indent=4)
            
            self.report({'INFO'}, i18n.translate("Version saved: v{:03d}").format(next_version))
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error saving version: {}").format(str(e)))
            return {'CANCELLED'}

class PublishVersionOperator(Operator):
    bl_idname = "project.publish_version"
    bl_label = i18n.translate("Publish Version")
    
    publish_note: StringProperty(
        name=i18n.translate("Publish Note"),
        description=i18n.translate("Note about this publish"),
        default=""
    )
    
    def execute(self, context):
        try:
            # Get addon preferences
            prefs = get_addon_prefs()
            if not prefs:
                self.report({'ERROR'}, i18n.translate("Addon preferences not found"))
                return {'CANCELLED'}
            
            # Get current file path
            current_file = bpy.data.filepath
            if not current_file:
                self.report({'ERROR'}, i18n.translate("Save the file first"))
                return {'CANCELLED'}
            
            # Get current version
            current_version = get_version_number(current_file)
            
            # Create publish path
            publish_path = current_file.replace("WIP", "PUBLISH")
            publish_path = publish_path.replace(f"v{current_version:03d}", "LATEST")
            
            # Create publish directory if needed
            os.makedirs(os.path.dirname(publish_path), exist_ok=True)
            
            # Save publish version
            bpy.ops.wm.save_as_mainfile(filepath=publish_path)
            
            # Save publish info
            if self.publish_note:
                publish_info = {
                    'version': current_version,
                    'note': self.publish_note,
                    'date': bpy.utils.time.strftime("%Y-%m-%d %H:%M:%S")
                }
                info_file = os.path.join(os.path.dirname(publish_path), "publish_info.json")
                import json
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(publish_info, f, indent=4)
            
            self.report({'INFO'}, i18n.translate("Version published"))
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error publishing version: {}").format(str(e)))
            return {'CANCELLED'}

class PROJECTMANAGER_OT_create_version(Operator):
    bl_idname = "project.create_version"
    bl_label = "Nova VersÃ£o"
    bl_description = "Cria uma nova versÃ£o do arquivo atual"
    
    def execute(self, context):
        try:
            if not context.scene.current_project or not context.scene.current_shot:
                self.report({'ERROR'}, "Carregue um shot ou cena primeiro")
                return {'CANCELLED'}

            if not context.scene.current_role:
                self.report({'ERROR'}, "Cargo nÃ£o definido")
                return {'CANCELLED'}

            # Obter caminho da prÃ³xima versÃ£o
            next_version = get_next_version_path(context)
            if not next_version:
                self.report({'ERROR'}, "Erro ao gerar caminho da prÃ³xima versÃ£o")
                return {'CANCELLED'}
            
            # Salvar como nova versÃ£o
            bpy.ops.wm.save_as_mainfile(filepath=next_version)
            
            # Abrir o arquivo recÃ©m criado
            bpy.ops.wm.open_mainfile(filepath=next_version)
            
            self.report({'INFO'}, f"Nova versÃ£o criada: {os.path.basename(next_version)}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao criar versÃ£o: {str(e)}")
            return {'CANCELLED'}

class PROJECTMANAGER_OT_publish_version(Operator):
    bl_idname = "project.publish_version"
    bl_label = "Publicar VersÃ£o"
    bl_description = "Publica a versÃ£o atual do arquivo"
    
    def execute(self, context):
        try:
            if not bpy.data.is_saved:
                self.report({'ERROR'}, "Salve o arquivo antes de publicar")
                return {'CANCELLED'}
            
            # Verificar se Ã© um arquivo WIP
            if "_WIP_" not in bpy.data.filepath:
                self.report({'ERROR'}, "Apenas arquivos WIP podem ser publicados")
                return {'CANCELLED'}
                
            # Obter informaÃ§Ãµes do projeto
            prefs = (get_addon_prefs())
            project_path = context.scene.current_project
            shot_name = context.scene.current_shot
            role_name = context.scene.current_role
            
            if not all([project_path, shot_name, role_name]):
                self.report({'ERROR'}, "Projeto, shot e cargo devem estar definidos")
                return {'CANCELLED'}
            
            project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Encontrar configuraÃ§Ãµes do cargo
            role_settings = None
            for role_mapping in prefs.role_mappings:
                if role_mapping.role_name == role_name:
                    role_settings = role_mapping
                    break
                    
            if not role_settings:
                self.report({'ERROR'}, f"Cargo '{role_name}' nÃ£o configurado")
                return {'CANCELLED'}
                
            # Construir caminho de publicaÃ§Ã£o
            publish_path = get_publish_path(
                role_settings.publish_path_preset,
                role_settings,
                context,
                project_path,
                project_name,
                shot_name,
                asset_name=''
            )
            
            # Criar pasta PUBLISH se nÃ£o existir
            os.makedirs(publish_path, exist_ok=True)
            
            # Nome do arquivo publicado com cargo
            publish_file = f"{project_prefix}_{shot_name}_{role_name}.blend"
            publish_filepath = os.path.join(publish_path, publish_file)
            
            # Salvar arquivo atual
            bpy.ops.wm.save_mainfile()
            
            # Copiar para PUBLISH
            shutil.copy2(bpy.data.filepath, publish_filepath)
            
            # Registrar timestamp da publicaÃ§Ã£o
            publish_time = datetime.now()
            context.scene.last_publish_time = publish_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # ForÃ§ar atualizaÃ§Ã£o de todas as Ã¡reas
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
    bl_label = "Abrir Ãšltimo WIP"
    bl_description = "Abre a versÃ£o WIP mais recente deste arquivo"
    
    def execute(self, context):
        try:
            if not bpy.data.is_saved:
                self.report({'ERROR'}, "Salve o arquivo atual primeiro")
                return {'CANCELLED'}
            
            # Obter caminho do publish correspondente
            current_file = bpy.data.filepath
            if "_WIP_" in current_file:
                # Se jÃ¡ estiver em um WIP, usar o publish correspondente
                publish_file = os.path.dirname(os.path.dirname(current_file))
                publish_file = os.path.join(publish_file, "PUBLISH", os.path.basename(current_file).split("_WIP_")[0] + ".blend")
            else:
                # Se estiver no publish, usar o prÃ³prio arquivo
                publish_file = current_file
            
            # Verificar se existe WIP e redirecionar
            should_redirect, wip_path = redirect_to_latest_wip(context, publish_file)
            if should_redirect and wip_path:
                bpy.ops.wm.open_mainfile(filepath=wip_path)
                self.report({'INFO'}, f"Abrindo Ãºltimo WIP: {os.path.basename(wip_path)}")
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "Nenhum arquivo WIP encontrado")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao abrir Ãºltimo WIP: {str(e)}")
            return {'CANCELLED'}

class PROJECTMANAGER_OT_open_publish(Operator):
    bl_idname = "project.open_publish"
    bl_label = "Abrir PublicaÃ§Ã£o"
    bl_description = "Abre a versÃ£o publicada deste arquivo"
    
    def execute(self, context):
        try:
            if not bpy.data.is_saved:
                self.report({'ERROR'}, "Salve o arquivo atual primeiro")
                return {'CANCELLED'}
            
            current_file = bpy.data.filepath
            if "_WIP_" not in current_file:
                self.report({'ERROR'}, "Este nÃ£o Ã© um arquivo WIP")
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
                self.report({'ERROR'}, "Arquivo publicado nÃ£o encontrado")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao abrir publicaÃ§Ã£o: {str(e)}")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(SaveVersionOperator)
    bpy.utils.register_class(PublishVersionOperator)
    bpy.utils.register_class(PROJECTMANAGER_OT_create_version)
    bpy.utils.register_class(PROJECTMANAGER_OT_publish_version)
    bpy.utils.register_class(PROJECTMANAGER_OT_open_latest_wip)
    bpy.utils.register_class(PROJECTMANAGER_OT_open_publish)

def unregister():
    bpy.utils.unregister_class(PROJECTMANAGER_OT_open_publish)
    bpy.utils.unregister_class(PROJECTMANAGER_OT_open_latest_wip)
    bpy.utils.unregister_class(PROJECTMANAGER_OT_publish_version)
    bpy.utils.unregister_class(PROJECTMANAGER_OT_create_version)
    bpy.utils.unregister_class(PublishVersionOperator)
    bpy.utils.unregister_class(SaveVersionOperator) 
