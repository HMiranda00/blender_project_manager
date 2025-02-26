import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from ..utils import get_project_info, get_publish_path, save_current_file

def get_assembly_path(context, shot_name):
    """Get the assembly file path for a shot"""
    prefs = context.preferences.addons['blender_project_manager'].preferences
    project_path = context.scene.current_project
    project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
    
    # Assembly is always in SHOTS folder
    shots_path = os.path.join(workspace_path, "SHOTS", shot_name, "ASSEMBLY")
    os.makedirs(shots_path, exist_ok=True)
    
    assembly_file = f"{project_prefix}_{shot_name}_ASSEMBLY.blend"
    return os.path.join(shots_path, assembly_file)

def get_role_publish_file(context, role_name, shot_name):
    """Get the publish file path for a role"""
    prefs = context.preferences.addons['blender_project_manager'].preferences
    project_path = context.scene.current_project
    project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
    
    # Get role settings
    role_settings = None
    for role_mapping in prefs.role_mappings:
        if role_mapping.role_name == role_name:
            role_settings = role_mapping
            break
            
    if not role_settings or role_settings.skip_assembly:
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
    
    publish_file = f"{project_prefix}_{shot_name}_{role_name}.blend"
    return os.path.join(publish_path, publish_file)

class ASSEMBLY_OT_rebuild(Operator):
    """Rebuild the assembly file by relinking all roles. Only use if links are broken or for initial setup."""
    bl_idname = "project.rebuild_assembly"
    bl_label = "Rebuild Assembly"
    bl_description = "Relink all roles in the assembly. Only needed if links are broken."
    
    def execute(self, context):
        try:
            if not (context.scene.current_project and context.scene.current_shot):
                self.report({'ERROR'}, "No project or shot selected")
                return {'CANCELLED'}
            
            # Store current context and file
            current_file = bpy.data.filepath
            current_project = context.scene.current_project
            current_shot = context.scene.current_shot
            current_role = context.scene.current_role
            
            # Get project info
            project_path = context.scene.current_project
            prefs = context.preferences.addons['blender_project_manager'].preferences
            project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            shot_name = context.scene.current_shot
            
            # Only remove collections that have broken links
            for collection in bpy.data.collections:
                if collection.name != "Master Collection":
                    if collection.library and not os.path.exists(collection.library.filepath):
                        bpy.data.collections.remove(collection)
            
            # Track which roles were successfully linked
            linked_roles = []
            required_roles = []
            
            # Link each role's publish file if not already linked
            for role_mapping in prefs.role_mappings:
                if role_mapping.skip_assembly:
                    continue
                    
                required_roles.append(role_mapping.role_name)
                publish_path = get_publish_path(
                    role_mapping.publish_path_preset,
                    role_mapping,
                    context,
                    project_path,
                    project_name,
                    shot_name,
                    asset_name=role_mapping.role_name
                )
                
                blend_filename = f"{project_prefix}_{shot_name}_{role_mapping.role_name}.blend"
                blend_path = os.path.join(publish_path, blend_filename)
                
                # Check if collection is already linked
                collection_exists = False
                for collection in bpy.data.collections:
                    if collection.name == role_mapping.role_name and collection.library:
                        if os.path.normpath(collection.library.filepath) == os.path.normpath(blend_path):
                            collection_exists = True
                            linked_roles.append(role_mapping.role_name)
                            break
                
                # Only link if collection doesn't exist and file exists
                if not collection_exists and os.path.exists(blend_path):
                    with bpy.data.libraries.load(blend_path, link=True) as (data_from, data_to):
                        data_to.collections = [c for c in data_from.collections]
                    
                    # Add to scene
                    for coll in data_to.collections:
                        if coll is not None:
                            context.scene.collection.children.link(coll)
                            linked_roles.append(role_mapping.role_name)
            
            # Save the assembly file
            bpy.ops.wm.save_mainfile()
            
            # Restore context
            context.scene.current_project = current_project
            context.scene.current_shot = current_shot
            context.scene.current_role = current_role
            
            # Check if all required roles were linked
            missing_roles = [role for role in required_roles if role not in linked_roles]
            
            if missing_roles:
                self.report({'WARNING'}, f"Assembly rebuilt but missing roles: {', '.join(missing_roles)}")
            else:
                self.report({'INFO'}, "Assembly rebuilt successfully with all required roles")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error rebuilding assembly: {str(e)}")
            return {'CANCELLED'}

class ASSEMBLY_OT_prepare_render(Operator):
    """Prepare assembly for rendering"""
    bl_idname = "project.prepare_assembly_render"
    bl_label = "Prepare for Render"
    bl_description = "Prepare a local copy of the assembly for rendering"
    
    purge_data: BoolProperty(
        name="Clean Unused Data",
        description="Remove all unused data from the file",
        default=True
    )
    
    make_local: BoolProperty(
        name="Make Local",
        description="Convert all linked data to local",
        default=True
    )
    
    pack_resources: BoolProperty(
        name="Pack Resources",
        description="Pack all external textures and resources into the file",
        default=True
    )
    
    check_missing: BoolProperty(
        name="Check Missing Files",
        description="Generate report of missing files",
        default=True
    )
    
    def execute(self, context):
        try:
            # Check if we're in an assembly file
            if not bpy.data.is_saved or "_ASSEMBLY.blend" not in bpy.data.filepath:
                self.report({'ERROR'}, "This operation can only be executed in the Assembly file")
                return {'CANCELLED'}
            
            # Save current file first
            save_current_file()
            
            # Get project info
            project_path = context.scene.current_project
            prefs = context.preferences.addons['blender_project_manager'].preferences
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            shot_name = context.scene.current_shot
            
            # Create !local directory with date subfolder
            from datetime import datetime
            local_path = os.path.join(workspace_path, "SHOTS", "!local")
            date_folder = datetime.now().strftime("%d-%m-%Y")
            render_path = os.path.join(local_path, date_folder)
            os.makedirs(render_path, exist_ok=True)
            
            # File name
            current_time = datetime.now().strftime("%Hh%M")
            render_file = f"{project_prefix}_{shot_name}_ASSEMBLY_RENDER_{current_time}.blend"
            render_filepath = os.path.join(render_path, render_file)
            
            # First save a copy of current file
            bpy.ops.wm.save_as_mainfile(filepath=render_filepath, copy=True)
            
            # Reopen the copied file
            bpy.ops.wm.open_mainfile(filepath=render_filepath)
            
            # Set render settings
            context.scene.render.engine = 'CYCLES'
            context.scene.cycles.device = 'GPU'
            
            # Enable all collections for rendering
            for collection in bpy.data.collections:
                collection.hide_render = False
            
            # Execute operations in order
            if self.purge_data:
                bpy.ops.outliner.orphans_purge(do_recursive=True)
            
            if self.make_local:
                # Make everything local
                bpy.ops.object.make_local(type='ALL')
                # Make collections local too
                for coll in bpy.data.collections:
                    if coll.library:
                        coll.override_create(remap_local_usages=True)
            
            if self.purge_data:
                bpy.ops.outliner.orphans_purge(do_recursive=True)
            
            if self.pack_resources:
                bpy.ops.file.pack_all()
            
            if self.check_missing:
                bpy.ops.file.report_missing_files()
            
            # Save local file
            bpy.ops.wm.save_mainfile()
            
            # Open file directory
            directory = os.path.dirname(render_filepath)
            if os.path.exists(directory):
                if os.name == 'nt':
                    os.startfile(directory)
                else:
                    import subprocess
                    subprocess.Popen(['xdg-open', directory])
            
            self.report({'INFO'}, f"Local file prepared for render: {render_filepath}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error preparing file: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class ASSEMBLY_OT_open(Operator):
    """Open the assembly file"""
    bl_idname = "project.open_assembly"
    bl_label = "Open Assembly"
    bl_description = "Open the assembly file for the current shot"
    
    def execute(self, context):
        try:
            if not (context.scene.current_project and context.scene.current_shot):
                self.report({'ERROR'}, "No project or shot selected")
                return {'CANCELLED'}
            
            # Get project info
            project_path = context.scene.current_project
            prefs = context.preferences.addons['blender_project_manager'].preferences
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            shot_name = context.scene.current_shot
            
            # Save current file path to return later
            if bpy.data.is_saved:
                context.scene.previous_file = bpy.data.filepath
            
            # Get assembly file path
            assembly_path = get_assembly_path(context, shot_name)
            
            # Save current file before opening assembly
            save_current_file()
            
            # Store current context
            current_project = context.scene.current_project
            current_shot = context.scene.current_shot
            current_role = context.scene.current_role
            
            # Create new file if assembly doesn't exist
            if not os.path.exists(assembly_path):
                bpy.ops.wm.read_homefile(app_template="")
                context.scene.name = shot_name
                bpy.ops.wm.save_as_mainfile(filepath=assembly_path)
            
            # Open assembly file
            bpy.ops.wm.open_mainfile(filepath=assembly_path)
            
            # Restore context
            context.scene.current_project = current_project
            context.scene.current_shot = current_shot
            context.scene.current_role = current_role
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error opening assembly: {str(e)}")
            return {'CANCELLED'}

class ASSEMBLY_OT_open_directory(Operator):
    """Open current file directory"""
    bl_idname = "project.open_current_directory"
    bl_label = "Open File Directory"
    bl_description = "Open the directory of the current file in system's file explorer"
    
    def execute(self, context):
        try:
            filepath = bpy.data.filepath
            if not filepath:
                self.report({'ERROR'}, "No file is currently open")
                return {'CANCELLED'}
                
            directory = os.path.dirname(filepath)
            if not os.path.exists(directory):
                self.report({'ERROR'}, "Directory not found")
                return {'CANCELLED'}
                
            if os.name == 'nt':
                os.startfile(directory)
            else:
                import subprocess
                subprocess.Popen(['xdg-open', directory])
                
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error opening directory: {str(e)}")
            return {'CANCELLED'}

def register():
    bpy.types.Scene.previous_file = StringProperty(
        name="Previous File",
        description="Path to the file that was open before the assembly"
    )
    
    bpy.utils.register_class(ASSEMBLY_OT_rebuild)
    bpy.utils.register_class(ASSEMBLY_OT_prepare_render)
    bpy.utils.register_class(ASSEMBLY_OT_open)
    bpy.utils.register_class(ASSEMBLY_OT_open_directory)

def unregister():
    bpy.utils.unregister_class(ASSEMBLY_OT_open)
    bpy.utils.unregister_class(ASSEMBLY_OT_prepare_render)
    bpy.utils.unregister_class(ASSEMBLY_OT_rebuild)
    bpy.utils.unregister_class(ASSEMBLY_OT_open_directory)
    
    del bpy.types.Scene.previous_file 