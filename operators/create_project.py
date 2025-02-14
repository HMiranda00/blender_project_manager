import bpy
import os
import re
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty, BoolProperty
from ..utils import get_project_info, create_project_structure, save_current_file
from .recent_projects import add_recent_project
from .. import i18n

class CreateProjectOperator(Operator):
    bl_idname = "project.create_project"
    bl_label = i18n.translate("Create Project")
    
    project_name: StringProperty(
        name=i18n.translate("Project Name"),
        description=i18n.translate("Name of the project to create")
    )
    
    project_type: EnumProperty(
        name=i18n.translate("Project Type"),
        items=[
            ('TEAM', i18n.translate("Team"), i18n.translate("Project with multiple roles and assembly"), 'COMMUNITY', 0),
            ('SOLO', i18n.translate("Solo"), i18n.translate("Simplified individual project"), 'PERSON', 1)
        ],
        default='TEAM'
    )
    
    asset_linking: EnumProperty(
        name=i18n.translate("Asset Reference"),
        items=[
            ('LINK', i18n.translate("Link"), i18n.translate("Assets will be linked (reference)"), 'LINKED', 0),
            ('APPEND', i18n.translate("Append"), i18n.translate("Assets will be appended (copy)"), 'APPEND_BLEND', 1)
        ],
        default='LINK'
    )
    
    use_versioning: BoolProperty(
        name=i18n.translate("Use Versioning"),
        description=i18n.translate("Enable WIP/Publish version control system"),
        default=True
    )
    
    project_path: StringProperty(
        name=i18n.translate("Project Folder"),
        description=i18n.translate("Select project folder"),
        subtype='DIR_PATH',
        default=""
    )
    
    def check_preferences(self, context):
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        missing = []
        
        if prefs.use_fixed_root:
            if not prefs.fixed_root_path:
                missing.append(i18n.translate("Fixed Root Path"))
        return missing

    def execute(self, context):
        try:
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            
            if prefs.use_fixed_root:
                if not self.project_name:
                    self.report({'ERROR'}, i18n.translate("Project name cannot be empty"))
                    return {'CANCELLED'}
                
                root_path = bpy.path.abspath(prefs.fixed_root_path)
                
                # Find next project number
                existing_projects = [
                    d for d in os.listdir(root_path) 
                    if os.path.isdir(os.path.join(root_path, d))
                ]
                project_numbers = []
                for d in existing_projects:
                    match = re.match(r'^(\d+)\s*-\s*', d)
                    if match:
                        project_numbers.append(int(match.group(1)))
                next_number = max(project_numbers, default=0) + 1
                
                # Create project folder name: "003 - Project Name"
                project_folder_name = f"{next_number:03d} - {self.project_name}"
                project_path = os.path.join(root_path, project_folder_name)
                
            else:
                if not self.project_path:
                    self.report({'ERROR'}, i18n.translate("Select a valid project folder"))
                    return {'CANCELLED'}
                project_path = bpy.path.abspath(self.project_path)
                
                if not os.path.exists(os.path.dirname(project_path)):
                    self.report({'ERROR'}, i18n.translate("Project path does not exist"))
                    return {'CANCELLED'}
            
            # Create project structure
            workspace_path = os.path.join(project_path, "3D")
            os.makedirs(workspace_path, exist_ok=True)
            
            # Create structure based on type
            create_project_structure(
                workspace_path, 
                project_prefix=self.project_name, 
                project_type=self.project_type
            )
            
            # Set current project
            context.scene.current_project = project_path
            
            # Register and configure project properties
            if not hasattr(context.scene, "project_settings"):
                from .. import properties
                properties.register()
            
            # Save project settings
            context.scene.project_settings.project_type = self.project_type
            context.scene.project_settings.asset_linking = self.asset_linking
            context.scene.project_settings.use_versioning = self.use_versioning
            
            # Setup Asset Browser with correct preferences
            bpy.ops.project.setup_asset_browser(
                link_type='LINK' if self.asset_linking == 'LINK' else 'APPEND'
            )
            
            # Add to recent projects
            if prefs.use_fixed_root:
                # For fixed root mode, use project name directly
                project_name = self.project_name
            else:
                # For free mode, use project folder name
                project_name = os.path.basename(project_path)
                
            add_recent_project(context, project_path, project_name)
            
            self.report({'INFO'}, i18n.translate("Project created: {}").format(os.path.basename(project_path)))
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, i18n.translate("Error creating project: {}").format(str(e)))
            return {'CANCELLED'}

    def invoke(self, context, event):
        save_current_file()
        
        missing_prefs = self.check_preferences(context)
        if missing_prefs:
            self.report({'ERROR'}, i18n.translate("Configure the following preferences first: {}").format(', '.join(missing_prefs)))
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
            return {'CANCELLED'}
            
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        
        if prefs.use_fixed_root:
            layout.prop(self, "project_name")
            layout.label(text=i18n.translate("Root Folder: {}").format(prefs.fixed_root_path))
        else:
            layout.prop(self, "project_path")
        
        # Project type
        box = layout.box()
        box.label(text=i18n.translate("Project Settings:"), icon='SETTINGS')
        box.prop(self, "project_type", expand=True)
        
        # Asset settings
        asset_box = layout.box()
        asset_box.label(text=i18n.translate("Asset Settings:"), icon='ASSET_MANAGER')
        asset_box.prop(self, "asset_linking")
        
        # Version control
        version_box = layout.box()
        version_box.label(text=i18n.translate("Version Control:"), icon='RECOVER_LAST')
        version_box.prop(self, "use_versioning")

def register():
    bpy.utils.register_class(CreateProjectOperator)

def unregister():
    bpy.utils.unregister_class(CreateProjectOperator)