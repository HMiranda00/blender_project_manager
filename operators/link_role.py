import bpy
import os
from bpy.types import Operator
from bpy.props import EnumProperty
from ..utils import get_publish_path, save_current_file, get_project_info

class LinkRoleOperator(Operator):
    bl_idname = "project.link_role"
    bl_label = "Linkar Cargo"
    bl_description = "Linkar ou anexar cargo ao arquivo atual"

    def get_roles(self, context):
        prefs = context.preferences.addons['project_manager'].preferences
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

    def execute(self, context):
        is_link = True  # Valor padrão
        try:
            save_current_file()
            
            prefs = context.preferences.addons['project_manager'].preferences
            project_path = context.scene.current_project
            project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            shot_name = context.scene.current_shot

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
                    data_to.worlds = [name for name in data_from.worlds]

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
            prefs = context.preferences.addons['project_manager'].preferences
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