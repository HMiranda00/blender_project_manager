import bpy
import os
from bpy.types import Operator
from bpy.props import EnumProperty
from ..utils import get_project_info, save_current_file

class OpenShotOperator(Operator):
    bl_idname = "project.open_shot"
    bl_label = "Abrir Shot"
    bl_description = "Abre um shot existente do projeto"

    def get_shots(self, context):
        """Lista todos os shots disponíveis"""
        print("\n=== Debug Get Shots ===")
        
        if not context.scene.current_project:
            print("Nenhum projeto selecionado")
            return [('NONE', "Nenhum projeto selecionado", "", 'ERROR', 0)]

        try:
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            project_path = context.scene.current_project
            project_name, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
            
            print(f"Project Path: {project_path}")
            print(f"Project Name: {project_name}")
            print(f"Workspace: {workspace_path}")
            
            shots_path = os.path.join(workspace_path, "SHOTS")
            print(f"Shots Path: {shots_path}")
            
            if not os.path.exists(shots_path):
                print("Pasta SHOTS não existe")
                return [('NONE', "Pasta SHOTS não encontrada", "", 'ERROR', 0)]

            # Listar pastas
            items = []
            shot_folders = []
            
            # Primeiro coletar todas as pastas válidas
            for f in os.listdir(shots_path):
                if f not in {'ASSEMBLY', '!LOCAL', '_WIP', 'ASSETS 3D'}:
                    full_path = os.path.join(shots_path, f)
                    if os.path.isdir(full_path):
                        shot_folders.append(f)
            
            print(f"Pastas encontradas: {shot_folders}")
            
            # Processar shots regulares primeiro
            for folder in sorted(shot_folders):
                if folder.startswith("SHOT_"):
                    shot_num = folder.replace("SHOT_", "")
                    items.append((
                        folder,
                        f"Shot {shot_num}",
                        f"Shot {shot_num}",
                        'SEQUENCE',
                        len(items)
                    ))
            
            # Depois processar cenas
            for folder in sorted(shot_folders):
                if folder.startswith("SCENE_"):
                    scene_name = folder.replace("SCENE_", "")
                    items.append((
                        folder,
                        f"Cena: {scene_name}",
                        f"Cena única: {scene_name}",
                        'SCENE_DATA',
                        len(items)
                    ))

            print(f"Items processados: {items}")
            
            if not items:
                return [('NONE', "Nenhum shot encontrado", "", 'ERROR', 0)]
            
            return items

        except Exception as e:
            print(f"Erro ao listar shots: {str(e)}")
            import traceback
            traceback.print_exc()
            return [('ERROR', "Erro ao listar shots", str(e), 'ERROR', 0)]

    def get_roles(self, context):
        """Lista todos os cargos configurados"""
        try:
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            return [(rm.role_name, rm.role_name, rm.description, rm.icon, i) 
                    for i, rm in enumerate(prefs.role_mappings)]
        except Exception as e:
            print(f"Erro ao listar cargos: {str(e)}")
            return [('NONE', "Erro ao listar cargos", "", 'ERROR', 0)]

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
            if not self.selected_shot or self.selected_shot in {'NONE', 'ERROR'}:
                self.report({'ERROR'}, "Selecione um shot válido")
                return {'CANCELLED'}

            if not self.selected_role:
                self.report({'ERROR'}, "Selecione um cargo")
                return {'CANCELLED'}

            # Atualizar contexto
            context.scene.current_shot = self.selected_shot
            context.scene.current_role = self.selected_role

            self.report({'INFO'}, f"Shot {self.selected_shot} selecionado")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Erro ao abrir shot: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        if not context.scene.current_project:
            self.report({'ERROR'}, "Selecione um projeto primeiro")
            return {'CANCELLED'}

        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        if not prefs.role_mappings:
            self.report({'ERROR'}, "Configure pelo menos um cargo nas preferências do addon")
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        
        # Mostrar projeto atual
        box = layout.box()
        box.label(text="Projeto Atual:", icon='FILE_FOLDER')
        prefs = context.preferences.addons['gerenciador_projetos'].preferences
        project_name, _, _ = get_project_info(context.scene.current_project, prefs.use_fixed_root)
        box.label(text=project_name)
        
        # Seleção de shot e cargo
        layout.prop(self, "selected_shot")
        layout.prop(self, "selected_role")

def register():
    bpy.utils.register_class(OpenShotOperator)

def unregister():
    bpy.utils.unregister_class(OpenShotOperator)