import bpy
import os
import json
from bpy.types import Operator
from bpy.app.handlers import (
    load_post,
    load_factory_preferences_post,
    load_factory_startup_post,
    undo_post,
    redo_post,
)
from ..utils import get_project_info

def cleanup_project_libraries(scene=None):
    """Remove bibliotecas de projeto temporárias"""
    try:
        ctx = bpy.context
        
        # Verificar se ainda temos contexto de projeto
        has_project_context = (
            hasattr(ctx.scene, "current_project") and 
            ctx.scene.current_project and 
            os.path.exists(ctx.scene.current_project)
        )
        
        current_project_name = None
        if has_project_context:
            prefs = ctx.preferences.addons['gerenciador_projetos'].preferences
            project_path = ctx.scene.current_project
            project_name, _, _ = get_project_info(project_path, prefs.use_fixed_root)
            current_project_name = project_name
        
        # Remover bibliotecas antigas
        asset_libs = ctx.preferences.filepaths.asset_libraries
        to_remove = []
        
        for i, lib in enumerate(asset_libs):
            lib_path = bpy.path.abspath(lib.path)
            if "ASSETS 3D" in lib_path:
                if not has_project_context or lib.name != current_project_name:
                    to_remove.append(i)
        
        # Remover do último para o primeiro para não afetar os índices
        for i in reversed(to_remove):
            bpy.ops.preferences.asset_library_remove(index=i)
            
    except Exception as e:
        print(f"Erro ao limpar bibliotecas: {str(e)}")

def on_file_change(dummy):
    """Handler para mudanças no arquivo"""
    cleanup_project_libraries()
    return None

def on_undo_redo(dummy):
    """Handler para undo/redo"""
    cleanup_project_libraries()
    return None

class PROJECTMANAGER_OT_setup_asset_browser(Operator):
    bl_idname = "project.setup_asset_browser"
    bl_label = "Configurar Asset Browser"
    bl_description = "Configura o Asset Browser para o projeto atual"
    
    link_type: bpy.props.EnumProperty(
        name="Tipo de Link",
        items=[
            ('LINK', "Link", "Assets serão linkados"),
            ('APPEND', "Append", "Assets serão anexados")
        ],
        default='LINK'
    )
    
    @classmethod
    def poll(cls, context):
        return context.scene.current_project is not None

    def setup_catalogs(self, library_path):
        """Cria catálogos padrão"""
        catalog_path = os.path.join(library_path, "blender_assets.cats.txt")
        
        catalogs_data = """# This is an Asset Catalog Definition file for Blender.
#
# Empty lines and lines starting with `#` will be ignored.
# The first non-ignored line should be the version indicator.
# Other lines are of the format "UUID:catalog/path/for/assets:simple catalog name"
VERSION 1
d1f81597-d27d-42fd-8386-3a3def6c9200:PROPS:PROPS
8bfeff41-7692-4f58-8238-a5c4d9dad2d0:CHR:CHR
b741e8a3-5da8-4f5a-8f4c-e05dd1e4766c:ENV:ENV
f5780a5c-74a4-4dd9-9e3d-c3654cf91f5c:MATERIALS:MATERIALS"""
        
        with open(catalog_path, 'w', encoding='utf-8') as f:
            f.write(catalogs_data)

    def execute(self, context):
        try:
            # Limpar outras bibliotecas de projeto primeiro
            cleanup_project_libraries(context.scene)
            
            prefs = context.preferences.addons['gerenciador_projetos'].preferences
            project_path = context.scene.current_project
            project_name, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
            
            # Configurar pasta de assets
            assets_path = os.path.join(workspace_path, "ASSETS 3D")
            if not os.path.exists(assets_path):
                os.makedirs(assets_path)

            # Criar catálogos primeiro
            self.setup_catalogs(assets_path)

            # Remover biblioteca existente com mesmo nome se houver
            asset_libs = context.preferences.filepaths.asset_libraries
            for i, lib in enumerate(asset_libs):
                if lib.name == project_name:
                    bpy.ops.preferences.asset_library_remove(index=i)
                    break
            
            # Adicionar nova biblioteca
            bpy.ops.preferences.asset_library_add()
            new_lib = context.preferences.filepaths.asset_libraries[-1]
            new_lib.name = project_name
            new_lib.path = assets_path
            
            # Configurar asset browser
            for asset_library in bpy.context.preferences.filepaths.asset_libraries:
                if asset_library.name == project_name:
                    # Configurar opções de linking baseado nas configurações do projeto
                    asset_library.import_method = 'APPEND' if self.link_type == 'APPEND' else 'LINK'
            
            self.report({'INFO'}, f"Asset Library '{project_name}' configurada com catálogos")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Erro ao configurar Asset Browser: {str(e)}")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(PROJECTMANAGER_OT_setup_asset_browser)
    
    # Registrar handlers para limpeza automática
    handlers = [
        (load_post, on_file_change),
        (load_factory_preferences_post, on_file_change),
        (load_factory_startup_post, on_file_change),
        (undo_post, on_undo_redo),
        (redo_post, on_undo_redo),
    ]
    
    for handler_list, func in handlers:
        if func not in handler_list:
            handler_list.append(func)

def unregister():
    bpy.utils.unregister_class(PROJECTMANAGER_OT_setup_asset_browser)
    
    # Remover handlers
    handlers = [
        (load_post, on_file_change),
        (load_factory_preferences_post, on_file_change),
        (load_factory_startup_post, on_file_change),
        (undo_post, on_undo_redo),
        (redo_post, on_undo_redo),
    ]
    
    for handler_list, func in handlers:
        if func in handler_list:
            handler_list.remove(func)
    
    # Limpar todas as bibliotecas ao desativar
    cleanup_project_libraries()