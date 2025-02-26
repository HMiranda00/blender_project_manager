import bpy
import os
from bpy.types import Operator
from bpy.props import EnumProperty
from ..utils import get_publish_path, save_current_file, get_project_info, get_folder_code

def get_role_file(context, role_name):
    """Get the publish file for a role"""
    try:
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_path = context.scene.current_project
        project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot
        
        # Get role settings
        role_settings = None
        for role_mapping in prefs.role_mappings:
            if role_mapping.role_name == role_name:
                role_settings = role_mapping
                break
                
        if not role_settings:
            print(f"Role settings not found for {role_name}")
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
        
        print(f"Checking publish path: {publish_path}")
        
        # Try old format first (for compatibility)
        old_file = f"{project_prefix}_{role_name}.blend"
        old_path = os.path.join(publish_path, old_file)
        if os.path.exists(old_path):
            print(f"Found old format file: {old_path}")
            return old_path
            
        # Try new format
        folder_code = get_folder_code(publish_path, role_settings)
        new_file = f"{project_prefix}_{folder_code}_{shot_name}_{role_name}.blend"
        new_path = os.path.join(publish_path, new_file)
        if os.path.exists(new_path):
            print(f"Found new format file: {new_path}")
            return new_path
            
        print(f"No file found for role {role_name}")
        return None
        
    except Exception as e:
        print(f"Error getting role file: {str(e)}")
        return None

class LinkRoleOperator(Operator):
    bl_idname = "project.link_role"
    bl_label = "Link Role"
    bl_description = "Link or append role to current file"

    def get_roles(self, context):
        prefs = context.preferences.addons['blender_project_manager'].preferences
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
        name="Select Role",
        description="Choose which role you need to link",
        items=get_roles
    )

    def execute(self, context):
        is_link = True  # Valor padrão
        try:
            save_current_file()
            
            prefs = context.preferences.addons['blender_project_manager'].preferences
            
            # Get role settings
            role_settings = None
            for role_mapping in prefs.role_mappings:
                if role_mapping.role_name == self.role_to_link:
                    role_settings = role_mapping
                    break

            if not role_settings:
                self.report({'ERROR'}, f"Role '{self.role_to_link}' not configured in preferences.")
                return {'CANCELLED'}

            is_link = role_settings.link_type == 'LINK'
            
            # Get role file
            blend_path = get_role_file(context, self.role_to_link)
            if not blend_path:
                self.report({'ERROR'}, f"Role file '{self.role_to_link}' not found.")
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
                    from ..utils import setup_collection_settings
                    setup_collection_settings(coll, role_settings)

            if role_settings.owns_world and len(data_to.worlds) > 0:
                context.scene.world = data_to.worlds[0]

            self.report({'INFO'}, f"Role '{self.role_to_link}' {'linked' if is_link else 'appended'} successfully.")
            return {'FINISHED'}

        except Exception as e:
            action = 'link' if is_link else 'append'
            self.report({'ERROR'}, f"Error trying to {action} role: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        if not context.scene.current_project or not context.scene.current_shot:
            self.report({'ERROR'}, "Select a project and shot first.")
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "role_to_link")
        
        if self.role_to_link:
            prefs = context.preferences.addons['blender_project_manager'].preferences
            for role_mapping in prefs.role_mappings:
                if role_mapping.role_name == self.role_to_link:
                    box = layout.box()
                    box.label(text=role_mapping.description, icon='INFO')
                    box.label(text=f"Type: {'Link' if role_mapping.link_type == 'LINK' else 'Append'}", 
                             icon='LINKED' if role_mapping.link_type == 'LINK' else 'APPEND_BLEND')

def register():
    bpy.utils.register_class(LinkRoleOperator)

def unregister():
    bpy.utils.unregister_class(LinkRoleOperator)