import bpy
import os
import re
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty, BoolProperty
from ..utils import get_project_info, save_current_file

class LoadProjectOperator(Operator):
    bl_idname = "project.load_project"
    bl_label = "Load Project"
    
    def get_projects(self, context):
        items = []
        prefs = context.preferences.addons['blender_project_manager'].preferences
        
        if not prefs.use_fixed_root or not prefs.fixed_root_path:
            return [('CUSTOM', "Select folder...", "Manually select the project folder", 'FILE_FOLDER', 0)]
            
        root_path = bpy.path.abspath(prefs.fixed_root_path)
        if not os.path.exists(root_path):
            return items
            
        # List all projects in root folder
        for folder in sorted(os.listdir(root_path)):
            folder_path = os.path.join(root_path, folder)
            if os.path.isdir(folder_path):
                match = re.match(r'^(\d+)\s*-\s*', folder)
                if match:
                    try:
                        number = int(match.group(1))
                        items.append((
                            folder_path,  # value
                            folder,       # label
                            f"Load project: {folder}",  # description
                            'FILE_FOLDER',  # icon
                            number  # sort index
                        ))
                    except (IndexError, ValueError):
                        continue
                    
        if not items:
            items = [('CUSTOM', "Select folder...", "Manually select the project folder", 'FILE_FOLDER', 0)]
            
        return items
    
    selected_project: EnumProperty(
        name="Project",
        description="Select the project to load",
        items=get_projects,
        update=lambda self, context: self.on_project_update(context)
    )
    
    project_path: StringProperty(
        name="Project Path",
        description="Path to the project folder",
        subtype='DIR_PATH'
    )
    
    def on_project_update(self, context):
        """Called when selected_project changes"""
        if self.selected_project != 'CUSTOM':
            self.project_path = self.selected_project
    
    def execute(self, context):
        try:
            save_current_file()
            
            prefs = context.preferences.addons['blender_project_manager'].preferences
            
            if prefs.use_fixed_root:
                if self.selected_project == 'CUSTOM':
                    if not self.project_path:
                        self.report({'ERROR'}, "Selecione uma pasta de projeto válida")
                        return {'CANCELLED'}
                    project_path = bpy.path.abspath(self.project_path)
                else:
                    project_path = self.selected_project
            else:
                if not self.project_path:
                    self.report({'ERROR'}, "Selecione uma pasta de projeto válida")
                    return {'CANCELLED'}
                project_path = bpy.path.abspath(self.project_path)

            if not os.path.exists(project_path):
                self.report({'ERROR'}, "Caminho do projeto não existe")
                return {'CANCELLED'}

            # Get project name for display
            project_name = os.path.basename(project_path.rstrip(os.path.sep))
            if prefs.use_fixed_root:
                match = re.match(r'^(\d+)\s*-\s*(.+)$', project_name)
                if match:
                    project_name = match.group(2).strip()

            # Set current project
            context.scene.current_project = project_path
            
            # Add to recent projects
            from ..operators.recent_projects import add_recent_project
            add_recent_project(context, project_path, project_name)
            
            # Configure Asset Browser automatically
            try:
                bpy.ops.project.setup_asset_browser()
            except Exception as e:
                self.report({'WARNING'}, f"Projeto carregado, mas houve um erro ao configurar o Asset Browser: {str(e)}")
                return {'FINISHED'}

            self.report({'INFO'}, f"Projeto carregado: {project_name}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao carregar projeto: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        prefs = context.preferences.addons['blender_project_manager'].preferences
        
        # Sync recent projects from preferences to scene
        context.scene.recent_projects.clear()
        for proj in prefs.recent_projects:
            item = context.scene.recent_projects.add()
            item.name = proj.name
            item.path = proj.path
        
        # Reset selection
        context.scene.recent_project_list_index = -1
        
        if not prefs.use_fixed_root:
            return context.window_manager.invoke_props_dialog(self)
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons['blender_project_manager'].preferences
        
        # Project selection
        if prefs.use_fixed_root:
            layout.prop(self, "selected_project")
            if self.selected_project == 'CUSTOM':
                layout.prop(self, "project_path")
        else:
            layout.prop(self, "project_path")
        
        # Recent projects list
        if len(context.scene.recent_projects) > 0:
            layout.label(text="Recent Projects:")
            
            # UIList
            row = layout.row()
            row.template_list(
                "PROJECTMANAGER_UL_recent_projects",
                "recent_projects",
                context.scene,
                "recent_projects",
                context.scene,
                "recent_project_list_index",
                rows=min(len(context.scene.recent_projects), 5)
            )
            
            # Clear button at bottom
            layout.operator("project.clear_recent_list", text="Clear Recent", icon='TRASH')
            
            # Auto-fill path when selecting from list
            if context.scene.recent_project_list_index >= 0 and len(context.scene.recent_projects) > 0:
                selected = context.scene.recent_projects[context.scene.recent_project_list_index]
                if selected:
                    self.project_path = selected.path

def register():
    bpy.utils.register_class(LoadProjectOperator)

def unregister():
    bpy.utils.unregister_class(LoadProjectOperator)