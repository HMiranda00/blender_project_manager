"""
Shot and scene creation operator
"""
import bpy
import os
from bpy.types import Operator
from bpy.props import IntProperty, EnumProperty, StringProperty
from ..utils.project_utils import get_addon_prefs, get_project_info, create_project_structure, save_current_file
from ..utils import (
    setup_collection_settings,
    setup_role_world
)
from ..utils.cache import DirectoryCache
from .. import i18n

class CreateShotOperator(Operator):
    """Create a new shot or scene"""
    bl_idname = "project.create_shot"
    bl_label = i18n.translate("Create Shot")
    bl_description = i18n.translate("Create a new shot or scene")
    bl_options = {'REGISTER', 'UNDO'}

    shot_number: IntProperty(
        name=i18n.translate("Shot Number"),
        default=1,
        min=1
    )

    scene_name: StringProperty(
        name=i18n.translate("Scene Name"),
        default="MAIN"
    )

    def get_roles(self, context):
        prefs = get_addon_prefs()
        return [(rm.role_name, rm.role_name, rm.description, rm.icon, i)
                for i, rm in enumerate(prefs.role_mappings)
                if rm.role_name != "ASSEMBLY"]  # Don't show ASSEMBLY role

    role: EnumProperty(
        name=i18n.translate("Your Role"),
        description=i18n.translate("Select your role for this shot"),
        items=get_roles
    )

    def check_preferences(self, context):
        prefs = get_addon_prefs()
        if not prefs:
            return [i18n.translate("Addon Preferences")]
        return []

    def execute(self, context):
        try:
            save_current_file()
            
            prefs = get_addon_prefs()
            settings = context.scene.project_settings
            project_path = context.scene.current_project

            if not project_path or not os.path.exists(project_path):
                self.report({'ERROR'}, i18n.translate("No project selected."))
                return {'CANCELLED'}

            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Determine shot/scene name based on mode
            if settings.project_type == 'TEAM':
                # Team mode - always create numbered shots
                shot_name = f"SHOT_{str(self.shot_number).zfill(3)}"
                role_name = self.role
                
                # Create role file
                wip_path = os.path.join(workspace_path, "SHOTS", shot_name, role_name, "_WIP")
                publish_path = os.path.join(workspace_path, "SHOTS", shot_name, role_name, "PUBLISH")
            else:
                # Solo mode - always create single scenes
                shot_name = f"SCENE_{self.scene_name}"
                role_name = "MAIN"
                
                # Create scene file
                wip_path = os.path.join(workspace_path, "SCENES", shot_name, "_WIP")
                publish_path = os.path.join(workspace_path, "SCENES", shot_name, "PUBLISH")
            
            os.makedirs(wip_path, exist_ok=True)
            os.makedirs(publish_path, exist_ok=True)

            # Create new file
            bpy.ops.wm.read_homefile(use_empty=True)

            # Setup scene
            context.scene.name = shot_name

            # Create main collection
            main_collection = bpy.data.collections.new(role_name)
            context.scene.collection.children.link(main_collection)
            context.view_layer.active_layer_collection = context.view_layer.layer_collection.children[role_name]

            # Save WIP file
            wip_filename = f"{project_prefix}_{shot_name}_{role_name}_WIP_001.blend"
            wip_filepath = os.path.join(wip_path, wip_filename)
            bpy.ops.wm.save_as_mainfile(filepath=wip_filepath)
            
            # Save publish file
            publish_filename = f"{project_prefix}_{shot_name}_{role_name}.blend"
            publish_filepath = os.path.join(publish_path, publish_filename)
            bpy.ops.wm.save_as_mainfile(filepath=publish_filepath)
            
            # Reopen WIP file
            bpy.ops.wm.open_mainfile(filepath=wip_filepath)
            
            # Update context
            context.scene.current_project = project_path
            context.scene.current_shot = shot_name
            context.scene.current_role = role_name

            self.report({'INFO'}, i18n.translate("Shot created and WIP file saved at: {}").format(wip_filepath))
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error creating shot: {}").format(str(e)))
            return {'CANCELLED'}

    def invoke(self, context, event):
        missing_prefs = self.check_preferences(context)
        if missing_prefs:
            self.report({'ERROR'}, i18n.translate("Configure the following preferences first: {}").format(', '.join(missing_prefs)))
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
            return {'CANCELLED'}

        if not context.scene.current_project:
            self.report({'ERROR'}, i18n.translate("Please select or create a project first."))
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        settings = context.scene.project_settings
        
        # Mostrar campos baseado no tipo de projeto
        if settings.project_type == 'TEAM':
            # Team mode - shot number and role
            layout.prop(self, "shot_number")
            layout.prop(self, "role")
        else:
            # Solo mode - scene name only
            layout.prop(self, "scene_name")

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
