import bpy
import os
import glob
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from datetime import datetime
from ..utils import get_project_info, get_publish_path, get_wip_path, save_current_file
from ..utils.cache import DirectoryCache

def get_wip_path(context, role_name):
    """Get the WIP path for the current role/shot"""
    try:
        if not (context.scene.current_project and context.scene.current_shot):
            return None
            
        project_path = context.scene.current_project
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot
        
        role_settings = None
        for role_mapping in prefs.role_mappings:
            if role_mapping.role_name == role_name:
                role_settings = role_mapping
                break
                
        if not role_settings:
            return None
            
        # Get WIP path
        wip_path = os.path.join(workspace_path, "SHOTS", shot_name, role_name, "WIP")
        os.makedirs(wip_path, exist_ok=True)
        
        return wip_path
        
    except Exception as e:
        print(f"Error getting WIP path: {str(e)}")
        return None

def get_latest_wip(context, role_name):
    """Get the latest WIP version"""
    try:
        wip_path = get_wip_path(context, role_name)
        if not wip_path:
            return None, 0
            
        project_path = context.scene.current_project
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot
        
        # Find latest version
        latest_version = 0
        latest_file = None
        
        for file in os.listdir(wip_path):
            if file.endswith(".blend"):
                try:
                    # Extract version number from filename
                    version = int(file.split("_v")[-1].split(".")[0])
                    if version > latest_version:
                        latest_version = version
                        latest_file = file
                except ValueError:
                    continue
        
        if latest_file:
            return os.path.join(wip_path, latest_file), latest_version
        
        return None, 0
        
    except Exception as e:
        print(f"Error getting latest WIP: {str(e)}")
        return None, 0

def create_or_update_publish(context, role_name):
    """Create or update the publish file by copying the latest WIP"""
    try:
        if not (context.scene.current_project and context.scene.current_shot):
            return None
            
        # Get latest WIP
        latest_wip, version = get_latest_wip(context, role_name)
        if not latest_wip:
            return None
            
        # Get publish path
        project_path = context.scene.current_project
        prefs = context.preferences.addons['blender_project_manager'].preferences
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
        
        # Create publish file
        os.makedirs(publish_path, exist_ok=True)
        publish_file = os.path.join(publish_path, f"{project_prefix}_{shot_name}_{role_name}.blend")
        
        # Copy latest WIP to publish
        import shutil
        shutil.copy2(latest_wip, publish_file)
        
        return publish_file
        
    except Exception as e:
        print(f"Error creating/updating publish: {str(e)}")
        return None

class VERSION_OT_new_wip_version(Operator):
    """Create a new WIP version"""
    bl_idname = "project.new_wip_version"
    bl_label = "New WIP Version"
    bl_description = "Create a new WIP version of the current file"
    
    role_name: StringProperty()
    update_publish: BoolProperty(
        name="Update Publish",
        description="Update the publish file with this version",
        default=True
    )
    
    def execute(self, context):
        try:
            if not (context.scene.current_project and context.scene.current_shot and context.scene.current_role):
                self.report({'ERROR'}, "No project, shot or role selected")
                return {'CANCELLED'}
            
            role_name = context.scene.current_role
            
            # Get WIP path
            wip_path = get_wip_path(context, role_name)
            if not wip_path:
                self.report({'ERROR'}, "Could not get WIP path")
                return {'CANCELLED'}
            
            # Get project info
            project_path = context.scene.current_project
            prefs = context.preferences.addons['blender_project_manager'].preferences
            project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            shot_name = context.scene.current_shot
            
            # Get latest version
            _, latest_version = get_latest_wip(context, role_name)
            
            # Create new version
            new_version = latest_version + 1
            new_file = os.path.join(wip_path, f"{project_prefix}_{shot_name}_{role_name}_v{new_version:03d}.blend")
            
            # Save as new version
            bpy.ops.wm.save_as_mainfile(filepath=new_file)
            
            # Update publish
            publish_file = create_or_update_publish(context, role_name)
            if not publish_file:
                self.report({'WARNING'}, "Could not update publish file")
            
            self.report({'INFO'}, f"Created WIP version {new_version}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error creating new version: {str(e)}")
            return {'CANCELLED'}

class VERSION_OT_open_latest_wip(Operator):
    """Open the latest WIP version"""
    bl_idname = "project.open_latest_wip"
    bl_label = "Open Latest WIP"
    bl_description = "Open the latest WIP version of the current role"
    
    # Manter role_name mas torná-lo interno (não exibido na interface)
    role_name: StringProperty(
        name="Role Name",
        description="Name of the role to open latest WIP for (internal use only)",
        options={'HIDDEN'}  # Oculta da interface do usuário
    )
    
    def execute(self, context):
        try:
            if not (context.scene.current_project and context.scene.current_shot):
                self.report({'ERROR'}, "No project or shot selected")
                return {'CANCELLED'}
            
            # Usar o role_name fornecido ou o current_role da cena
            role_name = self.role_name if self.role_name else context.scene.current_role
            
            if not role_name:
                self.report({'ERROR'}, "No role selected")
                return {'CANCELLED'}
            
            # Definir o role atual
            context.scene.current_role = role_name
            
            # Get latest WIP
            latest_wip, version = get_latest_wip(context, role_name)
            if not latest_wip:
                # Create first version if none exists
                wip_path = get_wip_path(context, role_name)
                if not wip_path:
                    self.report({'ERROR'}, "Could not get WIP path")
                    return {'CANCELLED'}
                
                project_path = context.scene.current_project
                prefs = context.preferences.addons['blender_project_manager'].preferences
                project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
                shot_name = context.scene.current_shot
                
                latest_wip = os.path.join(wip_path, f"{project_prefix}_{shot_name}_{role_name}_v001.blend")
                bpy.ops.wm.save_as_mainfile(filepath=latest_wip)
                
                # Create initial publish
                publish_file = create_or_update_publish(context, role_name)
                if not publish_file:
                    self.report({'WARNING'}, "Could not create publish file")
                
                self.report({'INFO'}, "Created first WIP version")
            else:
                # Open latest version
                save_current_file()
                bpy.ops.wm.open_mainfile(filepath=latest_wip)
                self.report({'INFO'}, f"Opened WIP version {version}")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error opening latest WIP: {str(e)}")
            return {'CANCELLED'}

class VERSION_OT_publish(Operator):
    bl_idname = "project.publish_version"
    bl_label = "Publish Version"
    bl_description = "Create a publish version from the current WIP"
    
    def execute(self, context):
        try:
            if not (context.scene.current_project and context.scene.current_shot and context.scene.current_role):
                self.report({'ERROR'}, "No project, shot or role selected")
                return {'CANCELLED'}
            
            role_name = context.scene.current_role
            
            # Save current file first
            save_current_file()
            
            # Create publish
            publish_file = create_or_update_publish(context, role_name)
            if not publish_file:
                self.report({'ERROR'}, "Could not create publish file")
                return {'CANCELLED'}
            
            self.report({'INFO'}, f"Published file created: {os.path.basename(publish_file)}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error publishing version: {str(e)}")
            return {'CANCELLED'}

class VERSION_OT_open_version_list(Operator):
    """Select and open a version from list"""
    bl_idname = "project.open_version_list"
    bl_label = "Select Version"
    bl_description = "Open a specific version from the list"
    bl_property = "version_enum"
    
    # Dicionário de caminhos como atributo de CLASSE (estático)
    file_paths = dict()
    
    def get_version_list(self, context):
        """Retorna itens para o menu de versões"""
        # Limpar paths armazenados anteriormente
        VERSION_OT_open_version_list.file_paths.clear()
        
        # Lista para armazenar os itens do menu
        items = []
        
        # Verificar requisitos
        if not (context.scene.current_project and context.scene.current_shot and context.scene.current_role):
            return [('NONE', "No versions available", "")]
            
        # Obter informações básicas
        role_name = context.scene.current_role
        project_path = context.scene.current_project
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot
        
        # Obter caminho da pasta WIP
        wip_path = get_wip_path(context, role_name)
        if not wip_path or not os.path.exists(wip_path):
            return [('NONE', "No versions available", "")]
        
        # Item para Latest WIP
        items.append(('LATEST', "Latest WIP", "Open the latest WIP version"))
        
        # Arquivo publicado
        for role_mapping in prefs.role_mappings:
            if role_mapping.role_name == role_name:
                publish_path = get_publish_path(
                    role_mapping.publish_path_preset,
                    role_mapping,
                    context,
                    project_path,
                    project_name,
                    shot_name,
                    asset_name=role_name
                )
                
                if publish_path:
                    publish_file = os.path.join(publish_path, f"{project_prefix}_{shot_name}_{role_name}.blend")
                    if os.path.exists(publish_file):
                        VERSION_OT_open_version_list.file_paths['PUBLISHED'] = publish_file
                        items.append(('PUBLISHED', "Published Version", "Open the published version"))
                break
        
        # Buscar todas as versões WIP
        try:
            # Padrão para o nome do arquivo WIP
            file_prefix = f"{project_prefix}_{shot_name}_{role_name}_v"
            
            # Lista para armazenar arquivos WIP encontrados
            wip_files = []
            
            # Listar todos os arquivos .blend na pasta WIP
            for file in os.listdir(wip_path):
                if file.endswith(".blend") and file.startswith(file_prefix):
                    try:
                        # Extrair número da versão
                        version_str = file.split("_v")[-1].split(".")[0]
                        version_num = int(version_str)
                        filepath = os.path.join(wip_path, file)
                        wip_files.append((version_num, filepath, file))
                    except (ValueError, IndexError):
                        continue
            
            # Ordenar por número de versão (mais recente primeiro)
            wip_files.sort(reverse=True)
            
            # Adicionar versões ao menu
            for version_num, filepath, filename in wip_files:
                item_id = f"V{version_num:03d}"
                VERSION_OT_open_version_list.file_paths[item_id] = filepath
                items.append((item_id, f"Version {version_num:03d}", f"Open {filename}"))
                
        except Exception as e:
            print(f"Error listing WIP files: {str(e)}")
        
        # Se não encontrou nenhuma versão (além do Latest WIP)
        if len(items) <= 1:
            return [('NONE', "No versions available", "")]
            
        return items
    
    # Propriedade para o menu enum
    version_enum: bpy.props.EnumProperty(
        name="Version",
        description="Select a version to open",
        items=get_version_list
    )
    
    def invoke(self, context, event):
        # Verificar requisitos
        if not (context.scene.current_project and context.scene.current_shot and context.scene.current_role):
            self.report({'ERROR'}, "No project, shot or role selected")
            return {'CANCELLED'}
        
        # Forçar a execução do get_version_list antes de mostrar o menu
        self.get_version_list(context)
        
        # Mostrar menu popup
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        # Verificar seleção
        if self.version_enum == 'NONE':
            self.report({'INFO'}, "No versions available")
            return {'CANCELLED'}
        
        # Processar Latest WIP
        if self.version_enum == 'LATEST':
            bpy.ops.project.open_latest_wip()
            return {'FINISHED'}
        
        # Processar Published Version
        if self.version_enum == 'PUBLISHED':
            bpy.ops.project.open_published()
            return {'FINISHED'}
        
        # Processar versão específica
        filepath = VERSION_OT_open_version_list.file_paths.get(self.version_enum)
        if not filepath or not os.path.exists(filepath):
            self.report({'ERROR'}, f"File not found: {self.version_enum}")
            return {'CANCELLED'}
        
        # Salvar arquivo atual
        save_current_file()
        
        # Abrir arquivo selecionado
        bpy.ops.wm.open_mainfile(filepath=filepath)
        self.report({'INFO'}, f"Opened: {os.path.basename(filepath)}")
        
        # Invalidar cache
        project_dir = os.path.dirname(context.scene.current_project)
        DirectoryCache.invalidate(project_dir)
        
        return {'FINISHED'}

# Novo operador para abrir a versão mais recente
class VERSION_OT_open_published(Operator):
    """Open the published version for the current role"""
    bl_idname = "project.open_published"
    bl_label = "Open Published Version"
    bl_description = "Open the published version of the current role"
    
    def execute(self, context):
        try:
            if not (context.scene.current_project and context.scene.current_shot and context.scene.current_role):
                self.report({'ERROR'}, "No project, shot or role selected")
                return {'CANCELLED'}
            
            # Obter informações do projeto
            role_name = context.scene.current_role
            project_path = context.scene.current_project
            prefs = context.preferences.addons['blender_project_manager'].preferences
            project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            shot_name = context.scene.current_shot
            
            # Encontrar o arquivo publicado
            for role_mapping in prefs.role_mappings:
                if role_mapping.role_name == role_name:
                    publish_path = get_publish_path(
                        role_mapping.publish_path_preset,
                        role_mapping,
                        context,
                        project_path,
                        project_name,
                        shot_name,
                        asset_name=role_name
                    )
                    
                    if not publish_path:
                        self.report({'ERROR'}, "Could not determine publish path")
                        return {'CANCELLED'}
                    
                    # Verificar arquivo publicado
                    publish_file = os.path.join(publish_path, f"{project_prefix}_{shot_name}_{role_name}.blend")
                    if not os.path.exists(publish_file):
                        self.report({'ERROR'}, "Published file does not exist")
                        return {'CANCELLED'}
                    
                    # Salvar arquivo atual
                    save_current_file()
                    
                    # Abrir arquivo publicado
                    bpy.ops.wm.open_mainfile(filepath=publish_file)
                    self.report({'INFO'}, f"Opened published file: {os.path.basename(publish_file)}")
                    
                    # Invalidar cache
                    DirectoryCache.invalidate(os.path.dirname(project_path))
                    
                    return {'FINISHED'}
            
            self.report({'ERROR'}, f"Role '{role_name}' not found in settings")
            return {'CANCELLED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error opening published version: {str(e)}")
            return {'CANCELLED'}

# Registration
classes = (
    VERSION_OT_new_wip_version,
    VERSION_OT_open_latest_wip,
    VERSION_OT_publish,
    VERSION_OT_open_version_list,
    VERSION_OT_open_published,
)

def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Erro ao registrar {cls.__name__}: {str(e)}")

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Erro ao desregistrar {cls.__name__}: {str(e)}") 