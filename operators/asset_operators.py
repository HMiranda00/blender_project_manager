import bpy
import os
import traceback
from bpy.types import Operator
from bpy.props import EnumProperty, StringProperty, BoolProperty
from ..utils import save_current_file, get_project_info

class ASSET_OT_reload_links(Operator):
    """Reload all linked assets and libraries"""
    bl_idname = "project.reload_links"
    bl_label = "Reload Assets"
    bl_description = "Reload all linked assets and libraries"

    def execute(self, context):
        try:
            # Save current file first
            save_current_file()
            
            # Reload all libraries
            reloaded = 0
            for lib in bpy.data.libraries:
                try:
                    lib.reload()
                    reloaded += 1
                except Exception as e:
                    print(f"Error reloading library {lib.filepath}: {str(e)}")
            
            # Force UI update
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()
            
            if reloaded > 0:
                self.report({'INFO'}, f"Reloaded {reloaded} libraries")
            else:
                self.report({'INFO'}, "No libraries to reload")
                
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error reloading assets: {str(e)}")
            return {'CANCELLED'}

class ASSET_OT_create_asset(Operator):
    bl_idname = "project.create_asset"
    bl_label = "Create Asset"
    bl_description = "Mark a collection as an asset or create a new asset file"

    asset_type: EnumProperty(
        name="Asset Type",
        items=[
            ('PROPS', "Prop", "General objects and props"),
            ('CHR', "Character", "Characters and rigs"),
            ('ENV', "Environment", "Environments and scenarios")
        ],
        default='PROPS'
    )

    name: StringProperty(
        name="Asset Name",
        description="Name of the asset"
    )

    save_mode: EnumProperty(
        name="Save Mode",
        items=[
            ('NEW_FILE', "New File", "Create a new file for the asset"),
            ('SAVE_AS', "Save As", "Save the current file as an asset file"),
            ('MARK_ONLY', "Mark Only", "Only mark as asset without saving new file")
        ],
        default='NEW_FILE',
        description="Defines how the asset will be saved"
    )

    @classmethod
    def poll(cls, context):
        if not context.scene.current_project:
            return False
        
        if bpy.data.is_saved:
            return (context.view_layer.active_layer_collection is not None and
                    context.view_layer.active_layer_collection.collection is not None)
            
        return True

    def _is_shot_file(self, context):
        """Verifica se estamos em um arquivo de shot"""
        if not bpy.data.is_saved:
            return False
            
        current_file = os.path.basename(bpy.data.filepath)
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_path = context.scene.current_project
        _, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        return current_file.startswith(project_prefix + "_SHOT_")

    def get_asset_path(self, context):
        """Retorna o caminho correto para o asset"""
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_path = context.scene.current_project
        _, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
        
        asset_path = os.path.join(workspace_path, "ASSETS 3D", self.asset_type)
        os.makedirs(asset_path, exist_ok=True)
        return asset_path

    def mark_as_asset(self, collection, generate_preview=True):
        """Marca a collection como asset e define o catálogo"""
        # Configurar catálogo antes de marcar como asset
        catalog_ids = {
            'PROPS': "d1f81597-d27d-42fd-8386-3a3def6c9200",
            'CHR': "8bfeff41-7692-4f58-8238-a5c4d9dad2d0",
            'ENV': "b741e8a3-5da8-4f5a-8f4c-e05dd1e4766c"
        }
        
        # Garantir que a collection está ativa
        layer_collection = bpy.context.view_layer.layer_collection.children.get(collection.name)
        if layer_collection:
            bpy.context.view_layer.active_layer_collection = layer_collection
            
        # Marcar como asset - isso já gera o preview automaticamente
        if not collection.asset_data:
            collection.asset_mark()
            
            # Definir catálogo após marcar como asset
            if self.asset_type in catalog_ids:
                collection.asset_data.catalog_id = catalog_ids[self.asset_type]

    def _get_preview_path(self, context):
        """Retorna o caminho onde o asset será salvo"""
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_path = context.scene.current_project
        _, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        
        base_path = os.path.join(workspace_path, "ASSETS 3D", self.asset_type)
        return os.path.join(base_path, f"{project_prefix}_{self.asset_type}_{self.name}.blend")

    def _create_new_file(self, context, blend_path):
        """Cria um novo arquivo para o asset"""
        current_project = context.scene.current_project
        
        # Criar novo arquivo
        bpy.ops.wm.read_homefile(use_empty=True)
        context.scene.current_project = current_project
        
        # Criar collection principal
        main_collection = bpy.data.collections.new(self.name)
        context.scene.collection.children.link(main_collection)
        self.mark_as_asset(main_collection)
        
        # Configurar collection ativa
        layer_collection = context.view_layer.layer_collection.children[self.name]
        context.view_layer.active_layer_collection = layer_collection
        
        # Salvar arquivo
        os.makedirs(os.path.dirname(blend_path), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    def execute(self, context):
        try:
            if not context.scene.current_project:
                self.report({'ERROR'}, "Selecione um projeto primeiro")
                return {'CANCELLED'}

            # Guardar informações do arquivo atual
            is_shot = self._is_shot_file(context)
            current_filepath = bpy.data.filepath
            
            # Obter caminho do asset
            blend_path = self._get_preview_path(context)

            # Em caso de arquivo de shot
            if is_shot:
                # Obter a collection ativa
                active_collection = context.view_layer.active_layer_collection.collection
                if not active_collection:
                    self.report({'ERROR'}, "Selecione uma collection para criar o asset")
                    return {'CANCELLED'}

                # Guardar nome da collection
                collection_name = active_collection.name

                # Criar conjunto para armazenar datablocks
                datablocks = set()

                def collect_dependencies(collection, seen=None):
                    """Coleta todas as dependências da collection recursivamente"""
                    if seen is None:
                        seen = set()
                    if collection in seen:
                        return
                    seen.add(collection)
                    
                    if collection and isinstance(collection, bpy.types.ID):
                        datablocks.add(collection)
                    for obj in collection.objects:
                        if obj and isinstance(obj, bpy.types.ID):
                            datablocks.add(obj)
                            if obj.data and isinstance(obj.data, bpy.types.ID):
                                datablocks.add(obj.data)
                            for mat_slot in obj.material_slots:
                                mat = mat_slot.material
                                if mat and isinstance(mat, bpy.types.ID):
                                    datablocks.add(mat)
                                    if mat.node_tree:
                                        datablocks.add(mat.node_tree)
                    for child in collection.children:
                        collect_dependencies(child, seen)

                # Coletar dependências
                collect_dependencies(active_collection)

                # Criar uma cena temporária para exportação
                temp_scene = bpy.data.scenes.new(name="TempScene")
                temp_scene.collection.children.link(active_collection)
                datablocks.add(temp_scene)

                # Marcar como asset antes de salvar
                self.mark_as_asset(active_collection)

                # Salvar os datablocks no arquivo de asset
                os.makedirs(os.path.dirname(blend_path), exist_ok=True)
                bpy.data.libraries.write(blend_path, datablocks, fake_user=True)

                # Remover cena temporária
                bpy.data.scenes.remove(temp_scene)

                # Remover collection original da cena
                if collection_name in context.scene.collection.children:
                    old_collection = context.scene.collection.children[collection_name]
                    context.scene.collection.children.unlink(old_collection)
                
                # Limpar collection do blend data
                if collection_name in bpy.data.collections:
                    bpy.data.collections.remove(bpy.data.collections[collection_name])

                # Linkar o asset de volta
                with bpy.data.libraries.load(blend_path, link=True) as (data_from, data_to):
                    data_to.collections = [collection_name]

                # Adicionar à cena
                for coll in data_to.collections:
                    if coll is not None:
                        context.scene.collection.children.link(coll)

                self.report({'INFO'}, f"Asset criado e linkado ao shot: {collection_name}")

            # Em caso de arquivo normal (não-shot)
            else:
                active_collection = context.view_layer.active_layer_collection.collection
                
                if self.save_mode == 'NEW_FILE':
                    # Criar novo arquivo do zero
                    if bpy.data.is_saved:
                        bpy.ops.wm.save_mainfile()
                    self._create_new_file(context, blend_path)
                    self.report({'INFO'}, f"Novo asset criado em: {blend_path}")
                    
                elif self.save_mode == 'SAVE_AS':
                    # Salvar arquivo atual como asset
                    if not active_collection:
                        self.report({'ERROR'}, "Selecione uma collection para o asset")
                        return {'CANCELLED'}
                    
                    # Marcar como asset
                    self.mark_as_asset(active_collection)
                    
                    # Salvar como novo arquivo
                    os.makedirs(os.path.dirname(blend_path), exist_ok=True)
                    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
                    self.report({'INFO'}, f"Arquivo salvo como asset em: {blend_path}")
                    
                else:  # MARK_ONLY
                    # Apenas marcar collection existente como asset
                    if not active_collection:
                        self.report({'ERROR'}, "Selecione uma collection para marcar como asset")
                        return {'CANCELLED'}
                    
                    # Marcar como asset
                    self.mark_as_asset(active_collection)
                    
                    # Salvar arquivo se já estiver salvo
                    if bpy.data.is_saved:
                        bpy.ops.wm.save_mainfile()
                        self.report({'INFO'}, f"Collection '{active_collection.name}' marcada como asset")
                    else:
                        self.report({'WARNING'}, "Collection marcada como asset, mas arquivo não está salvo")

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Erro ao criar asset: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        if not context.scene.current_project:
            self.report({'ERROR'}, "Selecione um projeto primeiro")
            return {'CANCELLED'}
            
        # Configurar modo de salvamento padrão baseado no contexto
        if self._is_shot_file(context):
            self.save_mode = 'NEW_FILE'  # Em shots, sempre criar novo arquivo
        elif not bpy.data.is_saved:
            self.save_mode = 'SAVE_AS'   # Se arquivo não está salvo, sugerir "Salvar Como"
        else:
            self.save_mode = 'MARK_ONLY' # Caso contrário, apenas marcar
        
        # Preencher nome com a collection selecionada
        if context.view_layer.active_layer_collection:
            active_collection = context.view_layer.active_layer_collection.collection
            if active_collection:
                self.name = active_collection.name
        
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        
        # Informações do Projeto
        box = layout.box()
        box.label(text="Projeto:", icon='FILE_FOLDER')
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_path = context.scene.current_project
        project_name, _, _ = get_project_info(project_path, prefs.use_fixed_root)
        box.label(text=project_name)
        
        # Tipo e Nome do Asset
        layout.prop(self, "asset_type")
        layout.prop(self, "name")
        
        # Opções de salvamento (exceto em shots)
        if not self._is_shot_file(context):
            box = layout.box()
            box.label(text="Modo de Salvamento:", icon='FILE_TICK')
            box.prop(self, "save_mode", text="")
            
            # Mostrar informação adicional baseado no modo
            info_box = box.box()
            if self.save_mode == 'NEW_FILE':
                info_box.label(text="• Salva arquivo atual")
                info_box.label(text="• Cria novo arquivo para o asset")
            elif self.save_mode == 'SAVE_AS':
                info_box.label(text="• Salva arquivo atual como asset")
                info_box.label(text="• Mantém conteúdo atual")
            else:  # MARK_ONLY
                info_box.label(text="• Apenas marca como asset")
                info_box.label(text="• Mantém no arquivo atual")
        else:
            # Em shots, mostrar informação sobre o comportamento
            box = layout.box()
            box.label(text="Modo Shot:", icon='SEQUENCE')
            info = box.box()
            info.label(text="• Cria novo arquivo para o asset")
            info.label(text="• Linka automaticamente ao shot")

def register():
    bpy.utils.register_class(ASSET_OT_reload_links)
    bpy.utils.register_class(ASSET_OT_create_asset)

def unregister():
    bpy.utils.unregister_class(ASSET_OT_create_asset)
    bpy.utils.unregister_class(ASSET_OT_reload_links)