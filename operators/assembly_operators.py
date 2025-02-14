"""
Assembly operators for managing project assembly
"""
import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from ..utils.project_utils import get_addon_prefs, save_current_file
from ..utils import get_project_info
from .. import i18n

class PrepareAssemblyOperator(Operator):
    """Prepare assembly file for current shot"""
    bl_idname = "project.prepare_assembly"
    bl_label = i18n.translate("Prepare Assembly")
    bl_description = i18n.translate("Create or update assembly file for current shot")
    
    def execute(self, context):
        try:
            # Get addon preferences
            prefs = get_addon_prefs()
            if not prefs:
                self.report({'ERROR'}, i18n.translate("Addon preferences not found"))
                return {'CANCELLED'}
            
            # Get project info
            project_path = context.scene.current_project
            if not project_path:
                self.report({'ERROR'}, i18n.translate("No project loaded"))
                return {'CANCELLED'}
            
            # Get current shot
            if not context.scene.current_shot:
                self.report({'ERROR'}, i18n.translate("No shot selected"))
                return {'CANCELLED'}
            
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Get assembly path
            assembly_path = os.path.join(workspace_path, "SHOTS", context.scene.current_shot, "ASSEMBLY")
            os.makedirs(assembly_path, exist_ok=True)
            
            # Create assembly file
            assembly_file = f"{project_prefix}_{context.scene.current_shot}_ASSEMBLY.blend"
            assembly_filepath = os.path.join(assembly_path, assembly_file)
            
            # Create new file
            bpy.ops.wm.read_homefile(use_empty=True)
            
            # Setup scene
            context.scene.name = f"{context.scene.current_shot}_ASSEMBLY"
            
            # Create assembly collection
            assembly_collection = bpy.data.collections.new("ASSEMBLY")
            context.scene.collection.children.link(assembly_collection)
            
            # Save file
            bpy.ops.wm.save_as_mainfile(filepath=assembly_filepath)
            
            # Update context
            context.scene.current_project = project_path
            context.scene.current_shot = context.scene.current_shot
            context.scene.current_role = "ASSEMBLY"
            
            # Update shot list
            context.scene.shot_list.clear()
            
            # Add shot
            shot_item = context.scene.shot_list.add()
            shot_item.name = context.scene.current_shot
            shot_item.type = 'SHOT'
            
            # Add roles
            for rm in prefs.role_mappings:
                if rm.role_name != "ASSEMBLY":
                    role_item = context.scene.shot_list.add()
                    role_item.name = rm.role_name
                    role_item.type = 'ROLE'
                    role_item.icon = rm.icon
                    role_item.is_linked = False
            
            self.report({'INFO'}, i18n.translate("Assembly file created"))
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error creating assembly: {}").format(str(e)))
            return {'CANCELLED'}

class RebuildAssemblyOperator(Operator):
    """Rebuild assembly file by relinking all roles"""
    bl_idname = "project.rebuild_assembly"
    bl_label = i18n.translate("Rebuild Assembly")
    bl_description = i18n.translate("Relink all roles in assembly file")
    
    def execute(self, context):
        try:
            # Get addon preferences
            prefs = get_addon_prefs()
            if not prefs:
                self.report({'ERROR'}, i18n.translate("Addon preferences not found"))
                return {'CANCELLED'}
            
            # Get project info
            project_path = context.scene.current_project
            if not project_path:
                self.report({'ERROR'}, i18n.translate("No project loaded"))
                return {'CANCELLED'}
            
            # Get current shot
            if not context.scene.current_shot:
                self.report({'ERROR'}, i18n.translate("No shot selected"))
                return {'CANCELLED'}
            
            # Check if we're in an assembly file
            if not bpy.data.filepath or "ASSEMBLY" not in bpy.data.filepath:
                self.report({'ERROR'}, i18n.translate("Not in an assembly file"))
                return {'CANCELLED'}
            
            # Save current file
            if not save_current_file():
                self.report({'WARNING'}, i18n.translate("Current file not saved"))
            
            # Clear existing collections
            for collection in bpy.data.collections:
                if collection.name != "ASSEMBLY":
                    bpy.data.collections.remove(collection)
            
            # Update shot list
            context.scene.shot_list.clear()
            
            # Add shot
            shot_item = context.scene.shot_list.add()
            shot_item.name = context.scene.current_shot
            shot_item.type = 'SHOT'
            
            # Add roles
            for rm in prefs.role_mappings:
                if rm.role_name != "ASSEMBLY":
                    role_item = context.scene.shot_list.add()
                    role_item.name = rm.role_name
                    role_item.type = 'ROLE'
                    role_item.icon = rm.icon
                    role_item.is_linked = False
                    
                    # Try to link role
                    bpy.ops.project.link_role(selected_role=rm.role_name)
            
            self.report({'INFO'}, i18n.translate("Assembly rebuilt"))
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error rebuilding assembly: {}").format(str(e)))
            return {'CANCELLED'}

class CleanMissingOperator(Operator):
    """Clean missing files from assembly"""
    bl_idname = "project.clean_missing"
    bl_label = i18n.translate("Clean Missing")
    bl_description = i18n.translate("Remove missing files from assembly")
    
    def execute(self, context):
        try:
            # Check if we're in an assembly file
            if not bpy.data.filepath or "ASSEMBLY" not in bpy.data.filepath:
                self.report({'ERROR'}, i18n.translate("Not in an assembly file"))
                return {'CANCELLED'}
            
            # Save current file
            if not save_current_file():
                self.report({'WARNING'}, i18n.translate("Current file not saved"))
            
            # Remove missing files
            for collection in bpy.data.collections:
                if collection.library and not os.path.exists(collection.library.filepath):
                    bpy.data.collections.remove(collection)
            
            # Update shot list
            for item in context.scene.shot_list:
                if item.type == 'ROLE':
                    item.is_linked = item.name in bpy.data.collections
            
            self.report({'INFO'}, i18n.translate("Missing files cleaned"))
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error cleaning missing files: {}").format(str(e)))
            return {'CANCELLED'}

class CleanUnusedOperator(Operator):
    """Clean unused data from assembly"""
    bl_idname = "project.clean_unused"
    bl_label = i18n.translate("Clean Unused")
    bl_description = i18n.translate("Remove unused data from assembly")
    
    def execute(self, context):
        try:
            # Check if we're in an assembly file
            if not bpy.data.filepath or "ASSEMBLY" not in bpy.data.filepath:
                self.report({'ERROR'}, i18n.translate("Not in an assembly file"))
                return {'CANCELLED'}
            
            # Save current file
            if not save_current_file():
                self.report({'WARNING'}, i18n.translate("Current file not saved"))
            
            # Remove unused data
            for datablock in [
                bpy.data.meshes,
                bpy.data.materials,
                bpy.data.textures,
                bpy.data.images,
                bpy.data.armatures,
                bpy.data.actions,
                bpy.data.cameras,
                bpy.data.lights,
                bpy.data.curves,
                bpy.data.metaballs,
                bpy.data.fonts,
                bpy.data.grease_pencils,
                bpy.data.collections,
                bpy.data.worlds,
                bpy.data.particles,
                bpy.data.palettes,
                bpy.data.brushes,
                bpy.data.linestyles,
                bpy.data.cache_files,
                bpy.data.lightprobes,
                bpy.data.lattices,
                bpy.data.volumes,
                bpy.data.hair_curves,
                bpy.data.pointclouds
            ]:
                for block in datablock:
                    if block.users == 0:
                        datablock.remove(block)
            
            self.report({'INFO'}, i18n.translate("Unused data cleaned"))
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error cleaning unused data: {}").format(str(e)))
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(PrepareAssemblyOperator)
    bpy.utils.register_class(RebuildAssemblyOperator)
    bpy.utils.register_class(CleanMissingOperator)
    bpy.utils.register_class(CleanUnusedOperator)

def unregister():
    bpy.utils.unregister_class(CleanUnusedOperator)
    bpy.utils.unregister_class(CleanMissingOperator)
    bpy.utils.unregister_class(RebuildAssemblyOperator)
    bpy.utils.unregister_class(PrepareAssemblyOperator) 
