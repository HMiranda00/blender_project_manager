import bpy
import os
from bpy.types import Operator
from bpy.props import BoolProperty
from ...utils import get_project_info, save_current_file

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

def register():
    bpy.utils.register_class(ASSEMBLY_OT_prepare_render)

def unregister():
    bpy.utils.unregister_class(ASSEMBLY_OT_prepare_render)