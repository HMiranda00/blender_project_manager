import bpy
import os
from bpy.types import Operator
from bpy.props import IntProperty, EnumProperty, StringProperty
from ..utils import (
    get_publish_path, 
    save_current_file, 
    get_project_info,
    setup_collection_settings,
    setup_role_world
)
from ..utils.cache import DirectoryCache
from ..utils.versioning import create_first_wip
from ..i18n.translations import translate as i18n_translate

class CreateShotOperator(Operator):
    """Create a new shot or scene"""
    bl_idname = "project.create_shot"
    bl_label = i18n_translate("Create Shot")
    bl_description = i18n_translate("Create a new shot or scene")
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(
        name=i18n_translate("Mode"),
        items=[
            ('SHOT', i18n_translate("Shot"), i18n_translate("Create a new numbered shot")),
            ('SCENE', i18n_translate("Single Scene"), i18n_translate("Create a single scene without numbering"))
        ],
        default='SHOT'
    )

    shot_number: IntProperty(
        name=i18n_translate("Shot Number"),
        default=1,
        min=1
    )

    scene_name: StringProperty(
        name=i18n_translate("Scene Name"),
        default="MAIN"
    )

    def get_roles(self, context):
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        return [(rm.role_name, rm.role_name, rm.description, rm.icon, i)
                for i, rm in enumerate(prefs.role_mappings)
                if rm.role_name != "ASSEMBLY"]  # Don't show ASSEMBLY role in the list

    role: EnumProperty(
        name=i18n_translate("Your Role"),
        description=i18n_translate("Select your role for this shot"),
        items=get_roles
    )

    def check_preferences(self, context):
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        missing = []

        if len(prefs.role_mappings) == 0:
            missing.append(i18n_translate("Role Settings"))

        return missing

    def setup_compositor_nodes(self, context, role_settings):
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
            else:
                # Fallback: setup básico
                tree.nodes.clear()
                render_node = tree.nodes.new('CompositorNodeRLayers')
                render_node.location = (-300, 0)
                composite = tree.nodes.new("CompositorNodeComposite")
                composite.location = (300, 0)
                tree.links.new(render_node.outputs["Image"], composite.inputs["Image"])
            
            # Organizar layout
            tree.nodes.update()
            
        except Exception as e:
            print(f"Erro ao configurar compositor: {str(e)}")

    def execute(self, context):
        try:
            save_current_file()
            
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            settings = context.scene.project_settings
            project_path = context.scene.current_project

            if not project_path or not os.path.exists(project_path):
                self.report({'ERROR'}, i18n_translate("No project selected."))
                return {'CANCELLED'}

            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Determine shot/scene name based on mode and project type
            if settings.project_type == 'TEAM':
                shot_name = f"SHOT_{str(self.shot_number).zfill(3)}"
            else:  # SOLO mode
                if self.mode == 'SHOT':
                    shot_name = f"SHOT_{str(self.shot_number).zfill(3)}"
                else:
                    shot_name = f"SCENE_{self.scene_name}"

            role_settings = None
            for role_mapping in prefs.role_mappings:
                if role_mapping.role_name == self.role:
                    role_settings = role_mapping
                    break

            if not role_settings:
                self.report({'ERROR'}, i18n_translate("Role '{}' not configured in preferences.").format(self.role))
                return {'CANCELLED'}

            # Create role file
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

            # Check if file exists using cache
            blend_filename = f"{project_prefix}_{shot_name}_{self.role}.blend"
            files = DirectoryCache.get_files(publish_path)
            if blend_filename in files:
                self.report({'ERROR'}, i18n_translate("Shot already exists: {}").format(blend_filename))
                return {'CANCELLED'}

            # If it doesn't exist, create new file
            bpy.ops.wm.read_homefile(use_empty=True)

            # Setup scene
            context.scene.name = shot_name

            # Create main collection
            main_collection = bpy.data.collections.new(self.role)
            context.scene.collection.children.link(main_collection)
            context.view_layer.active_layer_collection = context.view_layer.layer_collection.children[self.role]

            # Setup collection and world
            setup_collection_settings(main_collection, role_settings)
            setup_role_world(role_settings)
            
            # Save main shot file
            blend_path = os.path.join(publish_path, blend_filename)
            bpy.ops.wm.save_as_mainfile(filepath=blend_path)
            # Invalidate cache after creating file
            DirectoryCache.invalidate(publish_path)

            # Create first WIP
            wip_path = create_first_wip(context, blend_path)
            if not wip_path:
                self.report({'ERROR'}, i18n_translate("Error creating WIP version"))
                return {'CANCELLED'}
            
            # If in team mode, create or update assembly
            if settings.project_type == 'TEAM':
                # Save current WIP file
                bpy.ops.wm.save_mainfile()
                
                # Setup assembly paths
                assembly_path = os.path.join(workspace_path, "SHOTS", "ASSEMBLY")
                os.makedirs(assembly_path, exist_ok=True)
                assembly_file = f"{project_prefix}_{shot_name}_ASSEMBLY.blend"
                assembly_filepath = os.path.join(assembly_path, assembly_file)
                
                # Check if assembly exists
                if os.path.exists(assembly_filepath):
                    # Open existing assembly
                    bpy.ops.wm.open_mainfile(filepath=assembly_filepath)
                    
                    # Link the new role collection
                    with bpy.data.libraries.load(blend_path, link=True) as (data_from, data_to):
                        if self.role in data_from.collections:
                            data_to.collections = [self.role]
                    
                    # Add linked collection to scene if it doesn't exist
                    for coll in data_to.collections:
                        if coll is not None and coll.name not in context.scene.collection.children:
                            context.scene.collection.children.link(coll)
                    
                    # Save updated assembly
                    bpy.ops.wm.save_mainfile()
                else:
                    # Create new assembly file
                    bpy.ops.wm.read_homefile(use_empty=True)
                    context.scene.name = shot_name
                    
                    # Setup project info in assembly
                    context.scene.current_project = project_path
                    context.scene.current_shot = shot_name
                    context.scene.current_role = "ASSEMBLY"
                    
                    # Link current role collection
                    with bpy.data.libraries.load(blend_path, link=True) as (data_from, data_to):
                        if self.role in data_from.collections:
                            data_to.collections = [self.role]
                    
                    # Add linked collection to scene
                    for coll in data_to.collections:
                        if coll is not None and coll.name not in context.scene.collection.children:
                            context.scene.collection.children.link(coll)
                    
                    # Save new assembly
                    bpy.ops.wm.save_as_mainfile(filepath=assembly_filepath)
                
                # Reopen role WIP file
                bpy.ops.wm.open_mainfile(filepath=wip_path)
            
            # Update context
            context.scene.current_project = project_path
            context.scene.current_shot = shot_name
            context.scene.current_role = self.role

            self.report({'INFO'}, i18n_translate("Shot created and WIP file saved at: {}").format(wip_path))
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, i18n_translate("Error creating shot: {}").format(str(e)))
            return {'CANCELLED'}

    def invoke(self, context, event):
        missing_prefs = self.check_preferences(context)
        if missing_prefs:
            self.report({'ERROR'}, i18n_translate("Configure the following preferences first: {}").format(', '.join(missing_prefs)))
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
            return {'CANCELLED'}

        if not context.scene.current_project:
            self.report({'ERROR'}, i18n_translate("Please select or create a project first."))
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        settings = context.scene.project_settings
        
        # Creation mode
        if settings.project_type == 'SOLO':
            layout.prop(self, "mode")
            
            # Mode-specific fields
            if self.mode == 'SHOT':
                layout.prop(self, "shot_number")
            else:
                layout.prop(self, "scene_name")
        else:
            # In team mode, always use shot numbers
            layout.prop(self, "shot_number")
            
        # Role
        layout.prop(self, "role")

    @classmethod
    def poll(cls, context):
        """Check if operator can be called"""
        return (
            context.scene.current_project and 
            os.path.exists(context.scene.current_project) and
            hasattr(context.scene, "project_settings")
        )

def register():
    bpy.utils.register_class(CreateShotOperator)

def unregister():
    bpy.utils.unregister_class(CreateShotOperator)