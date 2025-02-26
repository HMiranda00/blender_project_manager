import bpy
import os
import re
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty
from ..utils import get_project_info, save_current_file
from .recent_projects import PROJECT_MT_recent_menu

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
        items=get_projects
    )
    
    project_path: StringProperty(
        name="Project Path",
        description="Path to the project folder",
        subtype='DIR_PATH'
    )
    
    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons['blender_project_manager'].preferences
        
        # Project selection
        if prefs.use_fixed_root:
            layout.prop(self, "selected_project")
        else:
            layout.prop(self, "project_path")
            
        # Recent projects menu
        if len(prefs.recent_projects) > 0:
            print("\n[DEBUG] Desenhando diálogo de Load Project")
            print(f"Total de projetos recentes: {len(prefs.recent_projects)}")
            layout.separator()
            row = layout.row()
            row.menu("PROJECT_MT_recent_menu", text="Recent Projects", icon='FILE_FOLDER')
    
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

            # Definir projeto atual
            context.scene.current_project = project_path
            
            # Adicionar aos projetos recentes
            from ..operators.recent_projects import add_recent_project
            
            # Determinar o nome do projeto
            project_name = os.path.basename(project_path.rstrip(os.path.sep))  # Remove trailing slash
            print(f"[DEBUG] Nome da pasta do projeto: {project_name}")
            
            if prefs.use_fixed_root:
                match = re.match(r'^(\d+)\s*-\s*(.+)$', project_name)
                if match:
                    project_name = match.group(2).strip()
                    print(f"[DEBUG] Nome após remover número: {project_name}")
            
            # Garantir que temos um nome
            if not project_name:
                project_name = os.path.basename(project_path.rstrip(os.path.sep))
                print(f"[DEBUG] Usando nome da pasta como fallback: {project_name}")
            
            print(f"\n[DEBUG] Carregando projeto:")
            print(f"Path: {project_path}")
            print(f"Name: {project_name}")
            
            add_recent_project(context, project_path, project_name)
            
            # Configurar Asset Browser automaticamente
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
        if not prefs.use_fixed_root:
            return context.window_manager.invoke_props_dialog(self)
        return context.window_manager.invoke_props_dialog(self, width=400)

def register():
    bpy.utils.register_class(LoadProjectOperator)

def unregister():
    bpy.utils.unregister_class(LoadProjectOperator)