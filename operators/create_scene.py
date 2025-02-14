import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty
from ..utils import get_project_info, get_publish_path

class PROJECTMANAGER_OT_create_scene(Operator):
    bl_idname = "project.create_scene"
    bl_label = "Criar Nova Cena"
    bl_description = "Cria uma nova cena no projeto"
    
    scene_name: StringProperty(
        name="Nome da Cena",
        description="Nome da nova cena",
        default=""
    )
    
    @classmethod
    def poll(cls, context):
        return context.scene.current_project is not None
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        try:
            if not self.scene_name:
                self.report({'ERROR'}, "Nome da cena não pode ser vazio")
                return {'CANCELLED'}
            
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            project_path = context.scene.current_project
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            # Criar estrutura de pastas da cena
            scene_base_path = os.path.join(workspace_path, "SCENES", self.scene_name)
            wip_path = os.path.join(scene_base_path, "_WIP")
            publish_path = os.path.join(scene_base_path, "PUBLISH")
            
            os.makedirs(wip_path, exist_ok=True)
            os.makedirs(publish_path, exist_ok=True)
            
            # Criar primeiro WIP
            wip_file = f"{project_prefix}_SCENE_{self.scene_name}_WIP_001.blend"
            wip_filepath = os.path.join(wip_path, wip_file)
            
            # Salvar arquivo
            bpy.ops.wm.save_as_mainfile(filepath=wip_filepath)
            
            # Atualizar contexto
            context.scene.current_shot = f"SCENE_{self.scene_name}"
            
            self.report({'INFO'}, f"Cena criada: {self.scene_name}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao criar cena: {str(e)}")
            return {'CANCELLED'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "scene_name") 