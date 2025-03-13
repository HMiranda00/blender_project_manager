import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty, BoolProperty
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

class DuplicateShotOperator(Operator):
    bl_idname = "project.duplicate_shot"
    bl_label = "Duplicate Shot"
    bl_description = "Duplicate an existing shot with a new name"
    
    source_shot: StringProperty(
        name="Source Shot",
        description="Name of the shot to duplicate",
        default=""
    )
    
    new_shot_name: StringProperty(
        name="New Shot Name",
        description="Name for the duplicated shot (e.g., SHOT_020)",
        default="SHOT_"
    )
    
    update_scene_names: BoolProperty(
        name="Update Scene Names",
        description="Update scene names inside .blend files",
        default=True
    )
    
    @classmethod
    def poll(cls, context):
        return context.scene.current_project and context.scene.current_shot
    
    def fix_library_links(self, source_shot, target_shot):
        """Fix library links in the currently open .blend file"""
        # Process all libraries and update their paths
        fixed_links = False
        
        # First, make paths relative - this helps with some links
        bpy.ops.file.make_paths_relative()
        
        # Second, process each library and relocate it
        for lib in bpy.data.libraries:
            if source_shot in lib.filepath:
                old_path = lib.filepath
                new_path = old_path.replace(source_shot, target_shot)
                
                # Update filepath directly
                lib.filepath = new_path
                fixed_links = True
                
                # Try to force a reload
                try:
                    lib.reload()
                except:
                    pass
        
        # For libraries that might still be broken, look for any links we can fix
        libs_to_fix = []
        for lib in bpy.data.libraries:
            abs_path = bpy.path.abspath(lib.filepath)
            if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
                libs_to_fix.append(lib)
        
        # Try to fix each broken link
        for lib in libs_to_fix:
            # Generate a new expected path
            if source_shot in lib.filepath:
                new_lib_path = lib.filepath.replace(source_shot, target_shot)
                
                # Set the filepath directly
                lib.filepath = new_lib_path
                fixed_links = True
                
                # Try to force a reload/update
                try:
                    lib.reload()
                except:
                    pass
        
        return fixed_links, len(bpy.data.libraries)
        
    def execute(self, context):
        try:
            if not context.scene.current_project:
                self.report({'ERROR'}, "Select a project first")
                return {'CANCELLED'}
                
            if not self.new_shot_name.strip():
                self.report({'ERROR'}, "New shot name cannot be empty")
                return {'CANCELLED'}
            
            # Get the source shot (current)
            if not self.source_shot:
                self.source_shot = context.scene.current_shot
            
            # Save current file
            save_current_file()
            
            # Get project info
            project_path = context.scene.current_project
            prefs = context.preferences.addons['blender_project_manager'].preferences
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Check source shot path
            source_shot_path = os.path.join(workspace_path, "SHOTS", self.source_shot)
            if not os.path.exists(source_shot_path):
                self.report({'ERROR'}, f"Source shot {self.source_shot} does not exist")
                return {'CANCELLED'}
            
            # Check if target shot already exists
            target_shot_path = os.path.join(workspace_path, "SHOTS", self.new_shot_name)
            if os.path.exists(target_shot_path):
                self.report({'ERROR'}, f"Shot {self.new_shot_name} already exists")
                return {'CANCELLED'}
            
            # Store current file path before starting operations
            current_filepath = None
            if bpy.data.is_saved:
                current_filepath = bpy.data.filepath
            
            # Copy entire shot folder
            import shutil
            self.report({'INFO'}, f"Copying shot folder structure...")
            shutil.copytree(source_shot_path, target_shot_path)
            
            # Dictionary to track renamed files
            original_to_new_paths = {}
            
            # Rename .blend files in the target directory
            self.report({'INFO'}, f"Renaming files to match new shot name...")
            for root, dirs, files in os.walk(target_shot_path):
                for file in files:
                    if file.endswith('.blend'):
                        old_path = os.path.join(root, file)
                        if self.source_shot in file:
                            new_file = file.replace(self.source_shot, self.new_shot_name)
                            new_path = os.path.join(root, new_file)
                            
                            # Store the mapping for later
                            original_to_new_paths[old_path] = new_path
                            
                            # Rename file
                            try:
                                os.rename(old_path, new_path)
                            except Exception as e:
                                print(f"Error renaming {old_path} to {new_path}: {str(e)}")
            
            # Process .blend files to update scene names and relink assets
            self.report({'INFO'}, f"Processing .blend files and updating links...")
            # Get all .blend files in the duplicated shot
            blend_files = []
            for root, dirs, files in os.walk(target_shot_path):
                for file in files:
                    if file.endswith('.blend'):
                        blend_files.append(os.path.join(root, file))
            
            # Count of fixed files
            files_processed = 0
            files_with_fixed_links = 0
            
            # Process each .blend file
            for blend_file in blend_files:
                try:
                    # Open the file
                    bpy.ops.wm.open_mainfile(filepath=blend_file)
                    
                    # Check and rename scenes if requested
                    if self.update_scene_names:
                        renamed = False
                        for scene in bpy.data.scenes:
                            if self.source_shot in scene.name:
                                # Replace old shot name in the scene name
                                new_scene_name = scene.name.replace(self.source_shot, self.new_shot_name)
                                scene.name = new_scene_name
                                renamed = True
                    
                    # Fix links in the current file
                    fixed_links, num_libs = self.fix_library_links(self.source_shot, self.new_shot_name)
                    
                    if fixed_links:
                        files_with_fixed_links += 1
                    
                    # Save updated file
                    bpy.ops.wm.save_as_mainfile(filepath=blend_file)
                    files_processed += 1
                    
                except Exception as e:
                    print(f"Error processing file {blend_file}: {str(e)}")
            
            # Return to original file if possible
            success_message = ""
            
            # Special handling for assembly file
            assembly_path = os.path.join(target_shot_path, "ASSEMBLY")
            assembly_file = f"{project_prefix}_{self.new_shot_name}_ASSEMBLY.blend"
            assembly_filepath = os.path.join(assembly_path, assembly_file)
            
            has_assembly = False
            if os.path.exists(assembly_filepath):
                has_assembly = True
                # Open assembly file
                try:
                    bpy.ops.wm.open_mainfile(filepath=assembly_filepath)
                    
                    # Update context to new shot
                    context.scene.current_project = project_path
                    context.scene.current_shot = self.new_shot_name
                    
                    # Fix links in assembly
                    fixed_links, num_libs = self.fix_library_links(self.source_shot, self.new_shot_name)
                    
                    # Save updated assembly
                    bpy.ops.wm.save_as_mainfile(filepath=assembly_filepath)
                    
                    success_message = f"Shot duplicated as {self.new_shot_name}"
                    if self.update_scene_names:
                        success_message += ", scenes renamed"
                    success_message += f" and assembly updated ({num_libs} links processed)"
                    if fixed_links:
                        success_message += " - fixed broken links"
                    
                    # Add stats about processed files
                    success_message += f" | Processed {files_processed} files, fixed links in {files_with_fixed_links} files"
                except Exception as e:
                    print(f"Error updating assembly file: {str(e)}")
                    success_message = f"Shot duplicated but error updating assembly: {str(e)}"
            else:
                success_message = f"Shot duplicated as {self.new_shot_name}"
                if self.update_scene_names:
                    success_message += ", scenes renamed"
                success_message += f" but assembly file not found | Processed {files_processed} files, fixed links in {files_with_fixed_links} files"
            
            # Return to original file if possible and if we opened an assembly
            if current_filepath and os.path.exists(current_filepath):
                try:
                    bpy.ops.wm.open_mainfile(filepath=current_filepath)
                    
                    # Restore original project context
                    context.scene.current_project = project_path
                    if self.source_shot == context.scene.current_shot:
                        context.scene.current_shot = self.source_shot
                except Exception as e:
                    print(f"Error returning to original file: {str(e)}")
            
            self.report({'INFO'}, success_message)
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error duplicating shot: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        # Fill source shot with the current one
        if context.scene.current_shot:
            self.source_shot = context.scene.current_shot
            
            # Suggest next shot name (increment number)
            import re
            match = re.search(r'SHOT_(\d+)', self.source_shot)
            if match:
                shot_num = int(match.group(1))
                next_shot = shot_num + 10
                self.new_shot_name = f"SHOT_{next_shot:03d}"
            
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        # Source shot info
        layout.prop(self, "source_shot")
        
        # Target shot name
        layout.prop(self, "new_shot_name")
        
        # Option to update scene names
        layout.prop(self, "update_scene_names")
        
        # Info about current project
        box = layout.box()
        box.label(text="Current Project:", icon='FILE_FOLDER')
        prefs = context.preferences.addons['blender_project_manager'].preferences
        project_name, _, _ = get_project_info(context.scene.current_project, prefs.use_fixed_root)
        box.label(text=project_name)

def register():
    bpy.utils.register_class(CreateShotOperator)
    bpy.utils.register_class(DuplicateShotOperator)

def unregister():
    bpy.utils.unregister_class(CreateShotOperator)
    bpy.utils.unregister_class(DuplicateShotOperator)