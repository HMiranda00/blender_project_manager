import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from ..utils import (
    get_project_info,
    get_publish_path,
    save_current_file
)
from ..utils.cache import DirectoryCache
from ..core.project_context import ProjectContextManager
from ..i18n.translations import translate as i18n_translate

class PROJECTMANAGER_OT_open_role_file(Operator):
    bl_idname = "project.open_role_file"
    bl_label = i18n_translate("Open Role File")
    bl_description = i18n_translate("Open role file")
    
    role_name: StringProperty()
    is_publish: BoolProperty(
        name=i18n_translate("Open Publish"),
        description=i18n_translate("If true, opens publish file instead of WIP"),
        default=False
    )
    
    def execute(self, context):
        try:
            save_current_file()
            
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            project_path = context.scene.current_project
            shot_name = context.scene.current_shot
            role_name = self.role_name or context.scene.current_role
            
            if not project_path or not shot_name or not role_name:
                self.report({'ERROR'}, i18n_translate("Project, shot and role must be selected"))
                return {'CANCELLED'}
            
            # Get project info
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Find role settings
            role_settings = None
            for role_mapping in prefs.role_mappings:
                if role_mapping.role_name == role_name:
                    role_settings = role_mapping
                    break
            
            if not role_settings:
                self.report({'ERROR'}, i18n_translate("Role '{}' not configured").format(role_name))
                return {'CANCELLED'}
            
            # Get publish path
            publish_path = get_publish_path(
                role_settings.publish_path_preset,
                role_settings,
                context,
                project_path,
                project_name,
                shot_name,
                asset_name=''
            )
            
            # Build file name
            blend_filename = f"{project_prefix}_{shot_name}_{role_name}.blend"
            
            # Assembly é um caso especial - não tem WIP, sempre abre direto da pasta ASSEMBLY
            if role_name == "ASSEMBLY":
                assembly_path = os.path.join(workspace_path, "SHOTS", "ASSEMBLY")
                blend_path = os.path.join(assembly_path, blend_filename)
                if not os.path.exists(blend_path):
                    self.report({'ERROR'}, i18n_translate("Assembly file not found: {}").format(blend_path))
                    return {'CANCELLED'}
            elif self.is_publish:
                # Open publish file
                blend_path = os.path.join(publish_path, blend_filename)
                if not os.path.exists(blend_path):
                    self.report({'ERROR'}, i18n_translate("Publish file not found: {}").format(blend_path))
                    return {'CANCELLED'}
            else:
                # Open latest WIP
                wip_path = os.path.join(publish_path, "_WIP")
                if not os.path.exists(wip_path):
                    self.report({'ERROR'}, i18n_translate("WIP folder not found: {}").format(wip_path))
                    return {'CANCELLED'}
                
                # Find latest WIP
                wip_files = [f for f in os.listdir(wip_path) if f.endswith('.blend')]
                if not wip_files:
                    self.report({'ERROR'}, i18n_translate("No WIP files found"))
                    return {'CANCELLED'}
                
                # Sort by name (which includes version number) and get latest
                wip_files.sort()
                blend_path = os.path.join(wip_path, wip_files[-1])
            
            # Save context before opening file
            ctx_manager = ProjectContextManager()
            ctx = ctx_manager.load(project_path)
            ctx.current_shot = shot_name
            ctx.current_role = role_name
            ctx.project_path = project_path
            ctx_manager.save(ctx)
            
            # Open the file
            bpy.ops.wm.open_mainfile(filepath=blend_path)
            
            # Update scene properties from context
            context.scene.current_project = project_path
            context.scene.current_shot = shot_name
            context.scene.current_role = role_name
            
            # Invalidate directory cache
            DirectoryCache.invalidate(publish_path)
            
            self.report({'INFO'}, i18n_translate("Opened {} file: {}").format(
                'publish' if self.is_publish else 'WIP', 
                blend_path
            ))
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n_translate("Error opening file: {}").format(str(e)))
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(PROJECTMANAGER_OT_open_role_file)

def unregister():
    bpy.utils.unregister_class(PROJECTMANAGER_OT_open_role_file)