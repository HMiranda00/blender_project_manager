"""
Asset operators for managing assets in the project
"""
import bpy
import os
import traceback
from bpy.types import Operator
from bpy.props import EnumProperty, StringProperty, BoolProperty
from ..utils import save_current_file, get_project_info
from ..utils.cache import DirectoryCache
from ..utils.project_utils import get_addon_prefs, get_publish_path
from .. import i18n

class ASSET_OT_reload_link(Operator):
    """Operador para recarregar links"""
    bl_idname = "project.reload_link"
    bl_label = "Recarregar Links"
    bl_description = "Recarrega todos os arquivos linkados"

    def execute(self, context):
        try:
            save_current_file()
            for lib in bpy.data.libraries:
                lib.reload()
                self.report({'INFO'}, f"Biblioteca recarregada: {lib.filepath}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao recarregar: {str(e)}")
            return {'CANCELLED'}

class CreateAssetOperator(Operator):
    bl_idname = "project.create_asset"
    bl_label = i18n.translate("Create Asset")
    
    asset_name: StringProperty(
        name=i18n.translate("Asset Name"),
        description=i18n.translate("Name of the asset to create")
    )
    
    asset_type: EnumProperty(
        name=i18n.translate("Asset Type"),
        items=[
            ('PROPS', i18n.translate("Props"), i18n.translate("Props and small objects"), 'OBJECT_DATA', 0),
            ('CHR', i18n.translate("Characters"), i18n.translate("Characters and rigs"), 'ARMATURE_DATA', 1),
            ('ENV', i18n.translate("Environment"), i18n.translate("Environment and sets"), 'SCENE_DATA', 2),
            ('MAT', i18n.translate("Materials"), i18n.translate("Materials and shaders"), 'MATERIAL', 3)
        ],
        default='PROPS'
    )
    
    save_mode: EnumProperty(
        name="Modo de Salvamento",
        items=[
            ('NEW_FILE', "Novo Arquivo", "Cria um novo arquivo para o asset"),
            ('SAVE_AS', "Salvar Como", "Salva o arquivo atual como um arquivo de asset"),
            ('MARK_ONLY', "Apenas Marcar", "Apenas marca como asset sem salvar novo arquivo")
        ],
        default='NEW_FILE',
        description="Define como o asset serÃ¡ salvo"
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
        prefs = (get_addon_prefs())
        project_path = context.scene.current_project
        _, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        return current_file.startswith(project_prefix + "_SHOT_")

    def get_asset_path(self, context):
        """Retorna o caminho correto para o asset"""
        prefs = (get_addon_prefs())
        project_path = context.scene.current_project
        _, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
        
        asset_path = os.path.join(workspace_path, "ASSETS 3D")
        if self.asset_type == 'PROPS':
            asset_path = os.path.join(asset_path, "PROPS", self.asset_name)
        elif self.asset_type == 'CHR':
            asset_path = os.path.join(asset_path, "CHR", self.asset_name)
        elif self.asset_type == 'ENV':
            asset_path = os.path.join(asset_path, "ENV", self.asset_name)
        else:  # MAT
            asset_path = os.path.join(asset_path, "MATERIALS", self.asset_name)
        os.makedirs(asset_path, exist_ok=True)
        return asset_path

    def mark_as_asset(self, collection, generate_preview=True):
        """Marca a collection como asset e define o catÃ¡logo"""
        # Configurar catÃ¡logo antes de marcar como asset
        catalog_ids = {
            'PROPS': "d1f81597-d27d-42fd-8386-3a3def6c9200",
            'CHR': "8bfeff41-7692-4f58-8238-a5c4d9dad2d0",
            'ENV': "b741e8a3-5da8-4f5a-8f4c-e05dd1e4766c"
        }
        
        # Garantir que a collection estÃ¡ ativa
        layer_collection = bpy.context.view_layer.layer_collection.children.get(collection.name)
        if layer_collection:
            bpy.context.view_layer.active_layer_collection = layer_collection
            
        # Marcar como asset - isso jÃ¡ gera o preview automaticamente
        if not collection.asset_data:
            collection.asset_mark()
            
            # Definir catÃ¡logo apÃ³s marcar como asset
            if self.asset_type in catalog_ids:
                collection.asset_data.catalog_id = catalog_ids[self.asset_type]

    def _get_preview_path(self, context):
        """Retorna o caminho onde o asset serÃ¡ salvo"""
        prefs = (get_addon_prefs())
        project_path = context.scene.current_project
        _, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        
        base_path = os.path.join(workspace_path, "ASSETS 3D")
        if self.asset_type == 'PROPS':
            base_path = os.path.join(base_path, "PROPS", self.asset_name)
        elif self.asset_type == 'CHR':
            base_path = os.path.join(base_path, "CHR", self.asset_name)
        elif self.asset_type == 'ENV':
            base_path = os.path.join(base_path, "ENV", self.asset_name)
        else:  # MAT
            base_path = os.path.join(base_path, "MATERIALS", self.asset_name)
        return os.path.join(base_path, f"{project_prefix}_{self.asset_type}_{self.asset_name}.blend")

    def _create_new_file(self, context, blend_path):
        """Cria um novo arquivo para o asset"""
        current_project = context.scene.current_project
        
        # Criar novo arquivo
        bpy.ops.wm.read_homefile(use_empty=True)
        context.scene.current_project = current_project
        
        # Criar collection principal
        main_collection = bpy.data.collections.new(self.asset_name)
        context.scene.collection.children.link(main_collection)
        self.mark_as_asset(main_collection)
        
        # Configurar collection ativa
        layer_collection = context.view_layer.layer_collection.children[self.asset_name]
        context.view_layer.active_layer_collection = layer_collection
        
        # Salvar arquivo
        os.makedirs(os.path.dirname(blend_path), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    def execute(self, context):
        try:
            # Limpar cache antes de operaÃ§Ãµes pesadas
            DirectoryCache.invalidate()
            
            # ForÃ§ar limpeza de dados Ã³rfÃ£os
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            
            if not context.scene.current_project:
                self.report({'ERROR'}, "Selecione um projeto primeiro")
                return {'CANCELLED'}

            # Guardar informaÃ§Ãµes do arquivo atual
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
                    """Coleta todas as dependÃªncias da collection recursivamente"""
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

                # Coletar dependÃªncias
                collect_dependencies(active_collection)

                # Criar uma cena temporÃ¡ria para exportaÃ§Ã£o
                temp_scene = bpy.data.scenes.new(name="TempScene")
                temp_scene.collection.children.link(active_collection)
                datablocks.add(temp_scene)

                # Marcar como asset antes de salvar
                self.mark_as_asset(active_collection)

                # Salvar os datablocks no arquivo de asset
                os.makedirs(os.path.dirname(blend_path), exist_ok=True)
                bpy.data.libraries.write(blend_path, datablocks, fake_user=True)

                # Remover cena temporÃ¡ria
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

                # Adicionar Ã  cena
                for coll in data_to.collections:
                    if coll is not None:
                        context.scene.collection.children.link(coll)

                self.report({'INFO'}, f"Asset criado e linkado ao shot: {collection_name}")

            # Em caso de arquivo normal (nÃ£o-shot)
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
                    
                    # Salvar arquivo se jÃ¡ estiver salvo
                    if bpy.data.is_saved:
                        bpy.ops.wm.save_mainfile()
                        self.report({'INFO'}, f"Collection '{active_collection.name}' marcada como asset")
                    else:
                        self.report({'WARNING'}, "Collection marcada como asset, mas arquivo nÃ£o estÃ¡ salvo")

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Erro ao criar asset: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        if not context.scene.current_project:
            self.report({'ERROR'}, "Selecione um projeto primeiro")
            return {'CANCELLED'}
            
        # Configurar modo de salvamento padrÃ£o baseado no contexto
        if self._is_shot_file(context):
            self.save_mode = 'NEW_FILE'  # Em shots, sempre criar novo arquivo
        elif not bpy.data.is_saved:
            self.save_mode = 'SAVE_AS'   # Se arquivo nÃ£o estÃ¡ salvo, sugerir "Salvar Como"
        else:
            self.save_mode = 'MARK_ONLY' # Caso contrÃ¡rio, apenas marcar
        
        # Preencher nome com a collection selecionada
        if context.view_layer.active_layer_collection:
            active_collection = context.view_layer.active_layer_collection.collection
            if active_collection:
                self.asset_name = active_collection.name
        
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        
        # InformaÃ§Ãµes do Projeto
        box = layout.box()
        box.label(text="Projeto:", icon='FILE_FOLDER')
        prefs = (get_addon_prefs())
        project_path = context.scene.current_project
        project_name, _, _ = get_project_info(project_path, prefs.use_fixed_root)
        box.label(text=project_name)
        
        # Tipo e Nome do Asset
        layout.prop(self, "asset_type")
        layout.prop(self, "asset_name")
        
        # OpÃ§Ãµes de salvamento (exceto em shots)
        if not self._is_shot_file(context):
            box = layout.box()
            box.label(text="Modo de Salvamento:", icon='FILE_TICK')
            box.prop(self, "save_mode", text="")
            
            # Mostrar informaÃ§Ã£o adicional baseado no modo
            info_box = box.box()
            if self.save_mode == 'NEW_FILE':
                info_box.label(text="â€¢ Salva arquivo atual")
                info_box.label(text="â€¢ Cria novo arquivo para o asset")
            elif self.save_mode == 'SAVE_AS':
                info_box.label(text="â€¢ Salva arquivo atual como asset")
                info_box.label(text="â€¢ MantÃ©m conteÃºdo atual")
            else:  # MARK_ONLY
                info_box.label(text="â€¢ Apenas marca como asset")
                info_box.label(text="â€¢ MantÃ©m no arquivo atual")
        else:
            # Em shots, mostrar informaÃ§Ã£o sobre o comportamento
            box = layout.box()
            box.label(text="Modo Shot:", icon='SEQUENCE')
            info = box.box()
            info.label(text="â€¢ Cria novo arquivo para o asset")
            info.label(text="â€¢ Linka automaticamente ao shot")

def register():
    bpy.utils.register_class(ASSET_OT_reload_link)
    bpy.utils.register_class(CreateAssetOperator)

def unregister():
    bpy.utils.unregister_class(CreateAssetOperator)
    bpy.utils.unregister_class(ASSET_OT_reload_link)
