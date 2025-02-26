import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty
from ..utils import get_project_info, save_current_file
from ..utils.version_control import create_first_wip

class CreateShotOperator(Operator):
    bl_idname = "project.create_shot"
    bl_label = "Create Shot"
    
    shot_name: StringProperty(
        name="Shot Name",
        description="Name of the shot (e.g., SHOT_010)",
        default="SHOT_"
    )
    
    role_name: EnumProperty(
        name="Role",
        description="Role/department responsible for this file",
        items=lambda self, context: [
            (role.role_name, role.role_name, role.description)
            for role in context.preferences.addons['blender_project_manager'].preferences.role_mappings
        ]
    )
    
    def execute(self, context):
        try:
            if not context.scene.current_project:
                self.report({'ERROR'}, "Select a project first")
                return {'CANCELLED'}
                
            if not self.shot_name.strip():
                self.report({'ERROR'}, "Shot name cannot be empty")
                return {'CANCELLED'}
            
            # Save current file
            save_current_file()
            
            # Get project info
            project_path = context.scene.current_project
            prefs = context.preferences.addons['blender_project_manager'].preferences
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Create shot folder structure
            shot_path = os.path.join(workspace_path, "SHOTS", self.shot_name)
            os.makedirs(shot_path, exist_ok=True)
            
            # Create role folder and subfolders
            role_path = os.path.join(shot_path, self.role_name)
            wip_path = os.path.join(role_path, "WIP")
            publish_path = os.path.join(role_path, "PUBLISH")
            os.makedirs(wip_path, exist_ok=True)
            os.makedirs(publish_path, exist_ok=True)
            
            # Set current shot and role
            context.scene.current_shot = self.shot_name
            context.scene.current_role = self.role_name
            
            # Create new empty file
            bpy.ops.wm.read_homefile(use_empty=True)
            
            # Set scene name
            context.scene.name = self.shot_name
            
            # Restore project context
            context.scene.current_project = project_path
            context.scene.current_shot = self.shot_name
            context.scene.current_role = self.role_name
            
            # Create main collection for the role
            main_collection = bpy.data.collections.new(self.role_name)
            context.scene.collection.children.link(main_collection)
            
            # Make collection active in outliner
            layer_collection = context.view_layer.layer_collection.children[self.role_name]
            context.view_layer.active_layer_collection = layer_collection
            
            # Setup collection settings
            role_settings = None
            for role_mapping in prefs.role_mappings:
                if role_mapping.role_name == self.role_name:
                    role_settings = role_mapping
                    break
            
            if role_settings:
                from ..utils import setup_collection_settings, setup_role_world
                setup_collection_settings(main_collection, role_settings)
                setup_role_world(role_settings)
            
            # Create first WIP version and PUBLISH
            wip_file = create_first_wip(context, self.role_name)
            
            if not wip_file:
                self.report({'ERROR'}, "Error creating WIP version")
                return {'CANCELLED'}
                
            # Get assembly path
            assembly_path = os.path.join(workspace_path, "SHOTS", self.shot_name, "ASSEMBLY")
            os.makedirs(assembly_path, exist_ok=True)
            assembly_file = f"{project_prefix}_{self.shot_name}_ASSEMBLY.blend"
            assembly_filepath = os.path.join(assembly_path, assembly_file)
            
            # Store current file path to return later
            current_filepath = bpy.data.filepath
            
            # Create or update assembly
            if not os.path.exists(assembly_filepath):
                # Create new empty file for assembly
                bpy.ops.wm.read_homefile(use_empty=True)
                context.scene.name = self.shot_name
            else:
                # Open existing assembly
                bpy.ops.wm.open_mainfile(filepath=assembly_filepath)
            
            # Get publish file path
            publish_filename = f"{project_prefix}_{self.shot_name}_{self.role_name}.blend"
            publish_filepath = os.path.join(publish_path, publish_filename)
            
            # Link collection from publish if role is not set to skip assembly
            if role_settings and not role_settings.skip_assembly:
                # Remove old collection if exists
                if self.role_name in bpy.data.collections:
                    collection = bpy.data.collections[self.role_name]
                    if collection.name in context.scene.collection.children:
                        context.scene.collection.children.unlink(collection)
                    bpy.data.collections.remove(collection)
                
                # Link collection from publish
                with bpy.data.libraries.load(publish_filepath, link=True) as (data_from, data_to):
                    data_to.collections = [self.role_name]
                    if role_settings.owns_world:
                        data_to.worlds = [name for name in data_from.worlds]
                
                # Add to scene
                for coll in data_to.collections:
                    if coll is not None:
                        context.scene.collection.children.link(coll)
                        setup_collection_settings(coll, role_settings)
                
                # Setup world if needed
                if role_settings.owns_world and len(data_to.worlds) > 0:
                    context.scene.world = data_to.worlds[0]
            
            # Save assembly
            bpy.ops.wm.save_as_mainfile(filepath=assembly_filepath)
            
            # Return to WIP file
            bpy.ops.wm.open_mainfile(filepath=current_filepath)
            
            self.report({'INFO'}, f"Shot created and file saved at: {wip_file}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error creating shot: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

def register():
    bpy.utils.register_class(CreateShotOperator)

def unregister():
    bpy.utils.unregister_class(CreateShotOperator)