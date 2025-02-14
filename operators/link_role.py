"""
Link role operator for linking role collections to assembly
"""
import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty, BoolProperty
from ..utils.project_utils import get_addon_prefs, save_current_file
from ..utils import get_project_info
from .. import i18n

class LinkRoleOperator(Operator):
    bl_idname = "project.link_role"
    bl_label = i18n.translate("Link Role")
    bl_description = i18n.translate("Link role collection to assembly")
    
    def get_roles(self, context):
        """List all configured roles"""
        try:
            prefs = get_addon_prefs()
            if not prefs:
                return [('NONE', i18n.translate("No addon preferences"), "", 'ERROR', 0)]
                
            items = []
            for i, rm in enumerate(prefs.role_mappings):
                if rm.role_name != "ASSEMBLY":  # Don't show ASSEMBLY role
                    items.append((
                        rm.role_name,
                        rm.role_name,
                        rm.description or rm.role_name,
                        rm.icon if rm.icon != 'NONE' else 'OUTLINER_COLLECTION',
                        i
                    ))
            return items or [('NONE', i18n.translate("No roles configured"), "", 'ERROR', 0)]
            
        except Exception as e:
            print(f"Error listing roles: {str(e)}")
            return [('NONE', i18n.translate("Error listing roles"), "", 'ERROR', 0)]
    
    selected_role: EnumProperty(
        name=i18n.translate("Role"),
        description=i18n.translate("Select role to link"),
        items=get_roles
    )
    
    def execute(self, context):
        try:
            # Get addon preferences
            prefs = get_addon_prefs()
            if not prefs:
                self.report({'ERROR'}, i18n.translate("Addon preferences not found"))
                return {'CANCELLED'}
            
            # Validate role
            if not self.selected_role or self.selected_role == 'NONE':
                self.report({'ERROR'}, i18n.translate("Select a valid role"))
                return {'CANCELLED'}
            
            # Get project info
            project_path = context.scene.current_project
            if not project_path:
                self.report({'ERROR'}, i18n.translate("No project loaded"))
                return {'CANCELLED'}
            
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Get current shot
            if not context.scene.current_shot:
                self.report({'ERROR'}, i18n.translate("No shot selected"))
                return {'CANCELLED'}
            
            # Get role path
            shot_path = os.path.join(workspace_path, "SHOTS", context.scene.current_shot)
            role_path = os.path.join(shot_path, self.selected_role, "PUBLISH")
            role_file = os.path.join(role_path, f"{project_prefix}_{context.scene.current_shot}_{self.selected_role}.blend")
            
            # Check if role file exists
            if not os.path.exists(role_file):
                self.report({'WARNING'}, i18n.translate("Role file not found: {}").format(role_file))
                return {'CANCELLED'}
            
            # Save current file if needed
            if not save_current_file():
                self.report({'WARNING'}, i18n.translate("Current file not saved"))
            
            # Get role settings
            role_settings = None
            for rm in prefs.role_mappings:
                if rm.role_name == self.selected_role:
                    role_settings = rm
                    break
            
            if not role_settings:
                self.report({'ERROR'}, i18n.translate("Role settings not found"))
                return {'CANCELLED'}
            
            try:
                # Link role collection
                with bpy.data.libraries.load(role_file, link=True) as (data_from, data_to):
                    # Check if collection exists in file
                    if self.selected_role in data_from.collections:
                        data_to.collections = [self.selected_role]
                    else:
                        self.report({'ERROR'}, i18n.translate("Role collection not found in file"))
                        return {'CANCELLED'}
                
                # Add linked collection to scene if not exists
                for coll in data_to.collections:
                    if coll is not None:
                        # Remove existing collection if any
                        if coll.name in context.scene.collection.children:
                            old_coll = context.scene.collection.children[coll.name]
                            context.scene.collection.children.unlink(old_coll)
                            
                        # Link new collection
                        context.scene.collection.children.link(coll)
                        
                        # Configure collection settings
                        if role_settings.hide_viewport_default:
                            coll.hide_viewport = True
                        if role_settings.exclude_from_view_layer:
                            coll.exclude = True
                        if role_settings.collection_color != 'NONE':
                            coll.color_tag = role_settings.collection_color
                
                # Save file
                bpy.ops.wm.save_mainfile()
                
                self.report({'INFO'}, i18n.translate("Role linked: {}").format(self.selected_role))
                return {'FINISHED'}
                
            except Exception as e:
                self.report({'ERROR'}, i18n.translate("Error linking collection: {}").format(str(e)))
                return {'CANCELLED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error linking role: {}").format(str(e)))
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        if not context.scene.current_project:
            self.report({'ERROR'}, i18n.translate("Select a project first"))
            return {'CANCELLED'}
        
        if not context.scene.current_shot:
            self.report({'ERROR'}, i18n.translate("Select a shot first"))
            return {'CANCELLED'}
        
        prefs = get_addon_prefs()
        if not prefs or not prefs.role_mappings:
            self.report({'ERROR'}, i18n.translate("Configure at least one role in addon preferences"))
            return {'CANCELLED'}
        
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        # Show current project and shot
        box = layout.box()
        box.label(text=i18n.translate("Current Project:"), icon='FILE_FOLDER')
        prefs = get_addon_prefs()
        project_name, _, _ = get_project_info(context.scene.current_project, prefs.use_fixed_root)
        box.label(text=project_name)
        
        box = layout.box()
        box.label(text=i18n.translate("Current Shot:"), icon='SEQUENCE')
        box.label(text=context.scene.current_shot)
        
        # Role selection
        layout.prop(self, "selected_role")

def register():
    bpy.utils.register_class(LinkRoleOperator)

def unregister():
    bpy.utils.unregister_class(LinkRoleOperator)
