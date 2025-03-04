import bpy
import os
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
from ..utils.core import get_project_settings
from ..utils.core import verify_role_file

class ROLE_OT_create_role_file(Operator):
    """Cria um novo arquivo de role para o projeto"""
    bl_idname = "project.create_role_file"
    bl_label = "Create Role File"
    bl_description = "Creates a new role file for the project"
    bl_options = {'REGISTER', 'UNDO'}
    
    role_name: StringProperty(
        name="Role Name",
        description="Nome do role (função) para o arquivo",
        default=""
    )
    
    file_name: StringProperty(
        name="File Name",
        description="Nome do arquivo a ser criado",
        default=""
    )
    
    open_after_creation: BoolProperty(
        name="Open After Creation",
        description="Abre o arquivo após a criação",
        default=True
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "role_name")
        layout.prop(self, "file_name")
        layout.prop(self, "open_after_creation")
    
    def execute(self, context):
        # Verifica se os campos foram preenchidos
        if not self.role_name:
            self.report({'ERROR'}, "Role name is required")
            return {'CANCELLED'}
        
        if not self.file_name:
            self.report({'ERROR'}, "File name is required")
            return {'CANCELLED'}
        
        # Pega as configurações do projeto
        project_settings = get_project_settings()
        if not project_settings:
            self.report({'ERROR'}, "No active project")
            return {'CANCELLED'}
        
        # Verifica o diretório para o arquivo de role
        role_dir = project_settings.get_role_dir(self.role_name)
        
        # Verifica se o diretório existe
        if not os.path.exists(role_dir):
            try:
                os.makedirs(role_dir)
                self.report({'INFO'}, f"Created directory: {role_dir}")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to create directory: {e}")
                return {'CANCELLED'}
        
        # Construir caminho completo para o arquivo
        file_path = os.path.join(role_dir, f"{self.file_name}.blend")
        
        # Verifica se o arquivo já existe
        if os.path.exists(file_path):
            self.report({'ERROR'}, f"File already exists: {file_path}")
            return {'CANCELLED'}
        
        # Salvar o arquivo atual com novo nome
        try:
            # Salva o arquivo atual como novo arquivo
            bpy.ops.wm.save_as_mainfile(filepath=file_path, copy=True)
            self.report({'INFO'}, f"Created role file: {file_path}")
            
            # Registra o arquivo de role no projeto
            success = verify_role_file(file_path, self.role_name)
            if not success:
                self.report({'WARNING'}, "File created but not registered in project settings")
            
            # Abre o arquivo se solicitado
            if self.open_after_creation:
                bpy.ops.wm.open_mainfile(filepath=file_path)
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create file: {e}")
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(ROLE_OT_create_role_file)


def unregister():
    bpy.utils.unregister_class(ROLE_OT_create_role_file) 