import bpy
import os
from bpy.types import Operator
from ..utils import get_project_info
from ..utils.versioning import redirect_to_latest_wip, create_first_wip

class PROJECTMANAGER_OT_open_scene(Operator):
    bl_idname = "project.open_scene"
    bl_label = "Abrir Cena"
    bl_description = "Abre uma cena existente"
    
    def get_scenes(self, context):
        try:
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            project_path = context.scene.current_project
            _, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
            
            scenes_path = os.path.join(workspace_path, "SCENES")
            if not os.path.exists(scenes_path):
                return []
            
            scenes = []
            for scene in os.listdir(scenes_path):
                scene_path = os.path.join(scenes_path, scene)
                if os.path.isdir(scene_path) and not scene.startswith('_'):
                    scenes.append((scene, scene, ""))
            
            return scenes if scenes else [("", "Nenhuma cena encontrada", "")]
            
        except Exception as e:
            print(f"Erro ao listar cenas: {str(e)}")
            return [("", "Erro ao carregar cenas", "")]
    
    scene: bpy.props.EnumProperty(
        name="Cena",
        items=get_scenes,
        description="Selecione a cena para abrir"
    )
    
    @classmethod
    def poll(cls, context):
        return context.scene.current_project is not None
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        try:
            if not self.scene:
                self.report({'ERROR'}, "Selecione uma cena válida")
                return {'CANCELLED'}
            
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            project_path = context.scene.current_project
            project_name, workspace_path, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            
            scene_base_path = os.path.join(workspace_path, "SCENES", self.scene)
            publish_path = os.path.join(scene_base_path, "PUBLISH")
            
            # Nome do arquivo publicado
            publish_file = f"{project_prefix}_SCENE_{self.scene}.blend"
            publish_filepath = os.path.join(publish_path, publish_file)
            
            # Verificar se existe arquivo publicado
            if os.path.exists(publish_filepath):
                # Verificar se existe WIP mais recente
                should_redirect, wip_path = redirect_to_latest_wip(context, publish_filepath)
                
                if should_redirect and wip_path:
                    # Abrir último WIP
                    bpy.ops.wm.open_mainfile(filepath=wip_path)
                    self.report({'INFO'}, f"Último WIP da cena {self.scene} aberto")
                else:
                    # Se não há WIP, criar primeiro WIP
                    wip_path = create_first_wip(context, publish_filepath)
                    if wip_path:
                        bpy.ops.wm.open_mainfile(filepath=wip_path)
                        self.report({'INFO'}, f"Primeiro WIP da cena {self.scene} criado e aberto")
                    else:
                        self.report({'ERROR'}, "Erro ao criar primeiro WIP")
                        return {'CANCELLED'}
            else:
                self.report({'ERROR'}, f"Arquivo da cena não encontrado: {publish_filepath}")
                return {'CANCELLED'}
            
            # Atualizar contexto
            context.scene.current_shot = f"SCENE_{self.scene}"
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao abrir cena: {str(e)}")
            return {'CANCELLED'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "scene") 