import bpy
import os  # Adicionar esta linha
from bpy.types import Operator
from bpy.props import StringProperty
from ..utils import save_current_file
from ..utils.cache import DirectoryCache  # Novo import

class PROJECTMANAGER_OT_open_role_file(Operator):
    bl_idname = "project.open_role_file"
    bl_label = "Abrir Arquivo do Cargo"
    bl_description = "Abrir o arquivo deste cargo"
    
    role_name: StringProperty()
    
    def execute(self, context):
        try:  # Adicionar try/except para melhor tratamento de erro
            project_path = context.scene.current_project
            shot_name = context.scene.current_shot
            
            from ..panels.project_panel import PROJECT_PT_Panel
            panel = PROJECT_PT_Panel(bpy.context)
            
            if panel.open_role_file(context, self.role_name):
                context.scene.current_project = project_path
                context.scene.current_shot = shot_name
                context.scene.current_role = self.role_name
                
                if context.scene.current_project:
                    project_dir = os.path.dirname(context.scene.current_project)
                    DirectoryCache.invalidate(project_dir)
                
                return {'FINISHED'}
                
            self.report({'WARNING'}, f"Arquivo do cargo {self.role_name} não encontrado")
            return {'CANCELLED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao abrir arquivo: {str(e)}")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(PROJECTMANAGER_OT_open_role_file)

def unregister():
    bpy.utils.unregister_class(PROJECTMANAGER_OT_open_role_file)