import bpy
import os
from bpy.types import Operator
from ...utils import get_project_info, get_publish_path
from .utils import get_role_publish_file

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

def register():
    bpy.utils.register_class(ASSEMBLY_OT_rebuild)

def unregister():
    bpy.utils.unregister_class(ASSEMBLY_OT_rebuild) 