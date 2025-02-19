import bpy
import os
from bpy.types import Operator
from ..utils import get_project_info

class PROJECTMANAGER_OT_toggle_asset_browser(Operator):
    bl_idname = "project.toggle_asset_browser"
    bl_label = "Asset Browser"
    bl_description = "Abre/Fecha o Asset Browser do projeto"

    def execute(self, context):
        try:
            # Encontrar área do Asset Browser
            asset_area = None
            for area in context.screen.areas:
                if area.type == 'FILE_BROWSER' and area.ui_type == 'ASSETS':
                    asset_area = area
                    break

            if asset_area:
                # Se existe, fechar a área do Asset Browser
                with context.temp_override(area=asset_area):
                    bpy.ops.screen.area_close()
            else:
                # Se não existe, dividir a área 3D atual
                view3d_area = None
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        view3d_area = area
                        break

                if view3d_area:
                    # Capturar as áreas antes da divisão
                    areas_before = context.screen.areas[:]

                    # Usar temp_override para substituir o contexto
                    with context.temp_override(area=view3d_area, region=view3d_area.regions[0]):
                        # Dividir horizontalmente com 15% da altura (área menor embaixo)
                        bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.15)

                    # Capturar as áreas depois da divisão
                    areas_after = context.screen.areas[:]

                    # Encontrar a nova área criada
                    new_area = None
                    for area in areas_after:
                        if area not in areas_before:
                            new_area = area
                            break

                    if new_area is None:
                        self.report({'ERROR'}, "Não foi possível encontrar a nova área criada.")
                        return {'CANCELLED'}

                    # Ajustar o tipo da nova área para 'FILE_BROWSER' e definir ui_type para 'ASSETS'
                    new_area.type = 'FILE_BROWSER'
                    new_area.ui_type = 'ASSETS'

                    # Obter o espaço ativo da nova área
                    space = new_area.spaces.active
                    
                    # Configurar o Asset Browser para usar a biblioteca do projeto atual
                    prefs = context.preferences.addons['blender_project_manager'].preferences
                    project_path = context.scene.current_project
                    project_name, _, _ = get_project_info(project_path, prefs.use_fixed_root)
                    
                    # Esperar um frame para garantir que o espaço foi atualizado
                    def set_library():
                        for library in context.preferences.filepaths.asset_libraries:
                            if library.name == project_name:
                                space = new_area.spaces.active
                                if hasattr(space, "params"):
                                    space.params.asset_library_reference = library.name
                                return None
                        return None
                    
                    bpy.app.timers.register(set_library, first_interval=0.1)

            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(PROJECTMANAGER_OT_toggle_asset_browser)

def unregister():
    bpy.utils.unregister_class(PROJECTMANAGER_OT_toggle_asset_browser)