import bpy
import os
import re
from bpy.types import Operator
from bpy.props import EnumProperty
from ..utils import (
    get_publish_path, 
    save_current_file, 
    get_project_info, 
    detect_file_context,
    get_assembly_role,
    is_assembly_role
)

class LinkRoleOperator(Operator):
    bl_idname = "project.link_role"
    bl_label = "Linkar Cargo"
    bl_description = "Linkar ou anexar cargo ao arquivo atual"

    def get_roles(self, context):
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        current_role = context.scene.current_role
        
        items = []
        for role_mapping in prefs.role_mappings:
            if role_mapping.role_name != current_role:
                items.append((
                    role_mapping.role_name,
                    role_mapping.role_name,
                    role_mapping.description,
                    role_mapping.icon,
                    len(items)
                ))
        return items

    role_to_link: EnumProperty(
        name="Selecionar Cargo",
        description="Escolha qual cargo você precisa linkar",
        items=get_roles
    )

    def setup_compositor_nodes(self, context, role_settings, node_group=None):
        """Configura os nodes do compositor para o cargo"""
        try:
            # Ativar nodes do compositor
            context.scene.use_nodes = True
            tree = context.scene.node_tree
            
            if not tree:
                return
            
            # Tentar carregar a nodetree base do template
            template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "compositor_template.blend")
            
            if os.path.exists(template_path):
                with bpy.data.libraries.load(template_path) as (data_from, data_to):
                    # Assumindo que a nodetree base se chama "BASE_COMPOSITOR"
                    if "BASE_COMPOSITOR" in data_from.node_groups:
                        data_to.node_groups = ["BASE_COMPOSITOR"]
                
                if data_to.node_groups:
                    base_tree = data_to.node_groups[0]
                    
                    # Limpar nodes existentes
                    tree.nodes.clear()
                    
                    # Copiar nodes da base
                    for node in base_tree.nodes:
                        new_node = tree.nodes.new(node.bl_idname)
                        new_node.location = node.location
                        # Copiar outras propriedades relevantes...
                    
                    # Copiar links
                    for link in base_tree.links:
                        from_socket = tree.nodes[link.from_node.name].outputs[link.from_socket.name]
                        to_socket = tree.nodes[link.to_node.name].inputs[link.to_socket.name]
                        tree.links.new(from_socket, to_socket)
                    
                    # Se temos um nodegroup do cargo, conectá-lo
                    if node_group:
                        # Assumindo que temos um node chamado "CARGO_GROUP" na base
                        if "CARGO_GROUP" in tree.nodes:
                            tree.nodes["CARGO_GROUP"].node_tree = node_group
            
            else:
                # Fallback: setup básico se não encontrar o template
                tree.nodes.clear()
                render_node = tree.nodes.new('CompositorNodeRLayers')
                render_node.location = (-300, 0)
                
                if node_group:
                    group_node = tree.nodes.new("CompositorNodeGroup")
                    group_node.node_tree = node_group
                    group_node.location = (0, 0)
                    tree.links.new(render_node.outputs["Image"], group_node.inputs["Image"])
                    
                    composite = tree.nodes.new("CompositorNodeComposite")
                    composite.location = (300, 0)
                    tree.links.new(group_node.outputs[0], composite.inputs["Image"])
                else:
                    composite = tree.nodes.new("CompositorNodeComposite")
                    composite.location = (300, 0)
                    tree.links.new(render_node.outputs["Image"], composite.inputs["Image"])
            
            # Organizar layout
            tree.nodes.update()
            
        except Exception as e:
            print(f"Erro ao configurar compositor: {str(e)}")

    def execute(self, context):
        try:
            # Verificar modo do projeto
            if context.scene.project_settings.project_type == 'SOLO':
                self.report({'ERROR'}, "Linkagem de cargos não disponível no modo Solo")
                return {'CANCELLED'}
            
            # Limpar dados não utilizados antes de linkar
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            
            save_current_file()
            
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            project_path = context.scene.current_project
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            shot_name = context.scene.current_shot

            # Se não tiver shot_name, tentar extrair do nome do arquivo
            if not shot_name and bpy.data.is_saved:
                shot_name, role_name = detect_file_context(bpy.data.filepath, project_prefix)
                if shot_name:
                    bpy.ops.project.set_context(shot_name=shot_name, role_name=role_name)

            if not shot_name:
                self.report({'ERROR'}, "Não foi possível determinar o shot atual.")
                return {'CANCELLED'}

            role_settings = None
            for role_mapping in prefs.role_mappings:
                if role_mapping.role_name == self.role_to_link:
                    role_settings = role_mapping
                    break

            if not role_settings:
                self.report({'ERROR'}, f"Cargo '{self.role_to_link}' não configurado nas preferências.")
                return {'CANCELLED'}

            is_link = role_settings.link_type == 'LINK'

            publish_path = get_publish_path(
                role_settings.publish_path_preset,
                role_settings,
                context,
                project_path,
                project_name,
                shot_name,
                asset_name=self.role_to_link
            )
            publish_path = bpy.path.abspath(publish_path)

            blend_filename = f"{project_prefix}_{shot_name}_{self.role_to_link}.blend"
            blend_path = os.path.join(publish_path, blend_filename)

            if not os.path.exists(blend_path):
                self.report({'ERROR'}, f"O arquivo do cargo '{self.role_to_link}' não foi encontrado.")
                return {'CANCELLED'}

            # Remover collection existente se houver
            if self.role_to_link in bpy.data.collections:
                collection = bpy.data.collections[self.role_to_link]
                if collection.name in context.scene.collection.children:
                    context.scene.collection.children.unlink(collection)
                bpy.data.collections.remove(collection)
            
            # Carregar a collection (link ou append)
            with bpy.data.libraries.load(blend_path, link=is_link) as (data_from, data_to):
                data_to.collections = [self.role_to_link]
                if role_settings.owns_world:
                    # Carregar apenas o world necessário
                    data_to.worlds = [name for name in data_from.worlds 
                                    if name.startswith(self.role_to_link)]

            # Adicionar à cena e configurar
            for coll in data_to.collections:
                if coll is not None:
                    context.scene.collection.children.link(coll)

            if role_settings.owns_world and len(data_to.worlds) > 0:
                context.scene.world = data_to.worlds[0]

            self.report({'INFO'}, f"Cargo '{self.role_to_link}' {'linkado' if is_link else 'anexado'} com sucesso.")
            return {'FINISHED'}

        except Exception as e:
            action = 'linkar' if is_link else 'anexar'
            self.report({'ERROR'}, f"Erro ao {action} cargo: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        if not context.scene.current_project or not context.scene.current_shot:
            self.report({'ERROR'}, "Selecione um projeto e um shot primeiro.")
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "role_to_link")
        
        if self.role_to_link:
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            for role_mapping in prefs.role_mappings:
                if role_mapping.role_name == self.role_to_link:
                    box = layout.box()
                    box.label(text=role_mapping.description, icon='INFO')
                    box.label(text=f"Tipo: {'Link' if role_mapping.link_type == 'LINK' else 'Append'}", 
                             icon='LINKED' if role_mapping.link_type == 'LINK' else 'APPEND_BLEND')

def register():
    bpy.utils.register_class(LinkRoleOperator)

def unregister():
    bpy.utils.unregister_class(LinkRoleOperator)