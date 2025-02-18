import bpy
import os
from bpy.types import Operator
from bpy.props import EnumProperty
from ..utils import get_project_info, get_publish_path, save_current_file

class OpenShotOperator(Operator):
    bl_idname = "project.open_shot"
    bl_label = "Abrir Shot"
    bl_description = "Abre um shot existente do projeto"

    def get_shots(self, context):
        items = []
        
        if not context.scene.current_project:
            return items

        try:
            project_path = context.scene.current_project
            prefs = context.preferences.addons['project_manager'].preferences
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Caminho para a pasta SHOTS
            shots_path = os.path.join(workspace_path, "SHOTS")
            if not os.path.exists(shots_path):
                return items

            # Listar todos os shots
            shot_folders = [d for d in os.listdir(shots_path) if os.path.isdir(os.path.join(shots_path, d))]
            shot_folders.sort()

            for shot in shot_folders:
                if shot.startswith("SHOT_"):
                    items.append((shot, shot, f"Abrir {shot}"))

        except Exception as e:
            print(f"Erro ao listar shots: {str(e)}")

        return items

    def get_roles(self, context):
        prefs = context.preferences.addons['project_manager'].preferences
        return [(rm.role_name, rm.role_name, rm.description, rm.icon, i)
                for i, rm in enumerate(prefs.role_mappings)]

    selected_shot: EnumProperty(
        name="Shot",
        description="Selecione o shot para abrir",
        items=get_shots
    )

    selected_role: EnumProperty(
        name="Cargo",
        description="Selecione o cargo para abrir",
        items=get_roles
    )

    def execute(self, context):
        try:
            save_current_file()
            
            project_path = context.scene.current_project
            prefs = context.preferences.addons['project_manager'].preferences
            project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)

            # Usar o cargo selecionado em vez de ANIMATION
            role_name = self.selected_role

            # Encontrar configurações do cargo
            role_settings = None
            for role_mapping in prefs.role_mappings:
                if role_mapping.role_name == role_name:
                    role_settings = role_mapping
                    break

            if not role_settings:
                self.report({'ERROR'}, f"Cargo '{role_name}' não configurado.")
                return {'CANCELLED'}

            publish_path = get_publish_path(
                role_settings.publish_path_preset,
                role_settings,
                context,
                project_path,
                project_name,
                self.selected_shot,
                asset_name=''
            )
            
            blend_filename = f"{project_prefix}_{self.selected_shot}_{role_name}.blend"
            blend_path = os.path.join(publish_path, blend_filename)

            if not os.path.exists(blend_path):
                self.report({'ERROR'}, f"Arquivo não encontrado: {blend_filename}")
                return {'CANCELLED'}

            bpy.ops.wm.open_mainfile(filepath=blend_path)
            context.scene.current_project = project_path
            context.scene.current_shot = self.selected_shot
            context.scene.current_role = role_name

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Erro ao abrir shot: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        if not context.scene.current_project:
            self.report({'ERROR'}, "Selecione um projeto primeiro.")
            return {'CANCELLED'}
            
        # Se não houver cargos configurados
        prefs = context.preferences.addons['project_manager'].preferences
        if not prefs.role_mappings:
            self.report({'ERROR'}, "Configure pelo menos um cargo nas preferências do addon.")
            return {'CANCELLED'}
            
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "selected_shot")
        layout.prop(self, "selected_role")

def register():
    bpy.utils.register_class(OpenShotOperator)

def unregister():
    bpy.utils.unregister_class(OpenShotOperator)