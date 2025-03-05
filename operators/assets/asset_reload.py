import bpy
from bpy.types import Operator
from ...utils import save_current_file

class ASSET_OT_reload_links(Operator):
    """Reload all linked assets and libraries"""
    bl_idname = "project.reload_links"
    bl_label = "Reload Assets"
    bl_description = "Reload all linked assets and libraries"

    def execute(self, context):
        try:
            # Save current file first
            save_current_file()
            
            # Reload all libraries
            reloaded = 0
            for lib in bpy.data.libraries:
                try:
                    lib.reload()
                    reloaded += 1
                except Exception as e:
                    print(f"Error reloading library {lib.filepath}: {str(e)}")
            
            # Force UI update
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()
            
            if reloaded > 0:
                self.report({'INFO'}, f"Reloaded {reloaded} libraries")
            else:
                self.report({'INFO'}, "No libraries to reload")
                
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error reloading assets: {str(e)}")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(ASSET_OT_reload_links)

def unregister():
    bpy.utils.unregister_class(ASSET_OT_reload_links) 