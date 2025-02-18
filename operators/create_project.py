import bpy
import os
import re
from bpy.types import Operator
from bpy.props import StringProperty
from ..utils import get_project_info, create_project_structure, save_current_file

class CreateProjectOperator(Operator):
    bl_idname = "project.create_project"
    bl_label = "Criar Novo Projeto"

    project_name: StringProperty(
        name="Nome do Projeto",
        description="Nome do novo projeto",
        default=""
    )
    
    project_path: StringProperty(
        name="Pasta do Projeto",
        description="Selecione a pasta do projeto",
        subtype='DIR_PATH',
        default=""
    )
    
    def check_preferences(self, context):
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        missing = []
        
        if prefs.use_fixed_root:
            if not prefs.fixed_root_path:
                missing.append("Pasta Raiz Fixa")
        return missing

    def execute(self, context):
        try:
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            
            if prefs.use_fixed_root:
                if not self.project_name:
                    self.report({'ERROR'}, "Nome do projeto não pode ser vazio")
                    return {'CANCELLED'}
                
                root_path = bpy.path.abspath(prefs.fixed_root_path)
                
                # Encontrar próximo número de projeto
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
                
                # Criar nome da pasta do projeto: "003 - Nome do Projeto"
                project_folder_name = f"{next_number:03d} - {self.project_name}"
                project_path = os.path.join(root_path, project_folder_name)
                
                # Criar pasta do projeto
                os.makedirs(project_path, exist_ok=True)
                
                # Criar pasta de trabalho: sempre "03 - 3D"
                workspace_folder = "03 - 3D"  # Agora é sempre "03 - 3D"
                workspace_path = os.path.join(project_path, workspace_folder)
                
                # Criar estrutura do projeto diretamente na pasta 03 - 3D
                os.makedirs(workspace_path, exist_ok=True)
                create_project_structure(workspace_path)
                
            else:
                if not self.project_path:
                    self.report({'ERROR'}, "Selecione uma pasta de projeto válida")
                    return {'CANCELLED'}
                project_path = bpy.path.abspath(self.project_path)
                
                if not os.path.exists(os.path.dirname(project_path)):
                    self.report({'ERROR'}, "Caminho do projeto não existe")
                    return {'CANCELLED'}
                
                workspace_path = os.path.join(project_path, "3D")
                os.makedirs(workspace_path, exist_ok=True)
                create_project_structure(workspace_path)
            
            # Definir projeto atual
            context.scene.current_project = project_path

            # Configurar Asset Browser automaticamente
            try:
                bpy.ops.project.setup_asset_browser()
            except Exception as e:
                self.report({'WARNING'}, f"Projeto criado, mas houve um erro ao configurar o Asset Browser: {str(e)}")
                return {'FINISHED'}

            self.report({'INFO'}, f"Projeto criado: {os.path.basename(project_path)}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao criar projeto: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        save_current_file()
        
        missing_prefs = self.check_preferences(context)
        if missing_prefs:
            self.report({'ERROR'}, f"Configure as seguintes preferências primeiro: {', '.join(missing_prefs)}")
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
            return {'CANCELLED'}
            
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        
        if prefs.use_fixed_root:
            layout.prop(self, "project_name")
            layout.label(text=f"Pasta Raiz: {prefs.fixed_root_path}")
        else:
            layout.prop(self, "project_path")

def register():
    bpy.utils.register_class(CreateProjectOperator)

def unregister():
    bpy.utils.unregister_class(CreateProjectOperator)