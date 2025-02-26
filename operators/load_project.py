import bpy
import os
import re
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty
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
            
        # Recent projects
        if len(prefs.recent_projects) > 0:
            layout.separator()
            box = layout.box()
            box.label(text="Recent Projects:", icon='FILE_FOLDER')
            
            # Usar o mesmo estilo do Blender para a lista de recentes
            for recent in prefs.recent_projects:
                # Criar um row que funciona como botão
                row = box.row()
                
                # Adicionar o operador com o nome do projeto
                project_name = os.path.basename(recent.path)
                if recent.is_fixed_root:
                    # Para projetos com raiz fixa, remover o número do início
                    match = re.match(r'^\d+\s*-\s*(.+)$', project_name)
                    if match:
                        project_name = match.group(1)
                
                op = row.operator(
                    "project.open_recent",
                    text=project_name,
                    icon='FILE_FOLDER',
                    emboss=False,
                    depress=False
                )
                op.project_path = recent.path
                op.is_fixed_root = recent.is_fixed_root
            
            # Clear list button
            row = layout.row()
            row.alignment = 'RIGHT'
            row.operator("project.clear_recent_list", text="Clear Recent", icon='TRASH', emboss=False)
    
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
            project_name = os.path.basename(project_path)
            add_recent_project(context, project_path, project_name)
            
            # Configurar Asset Browser automaticamente
            try:
                bpy.ops.project.setup_asset_browser()
            except Exception as e:
                self.report({'WARNING'}, f"Projeto carregado, mas houve um erro ao configurar o Asset Browser: {str(e)}")
                return {'FINISHED'}

            self.report({'INFO'}, f"Projeto carregado: {os.path.basename(project_path)}")
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