"""
Assembly panel for managing final project assembly
"""
import bpy
import os
from bpy.types import Panel
from ..utils import (
    get_project_info, 
    get_publish_path, 
    save_current_file
)
from ..utils.cache import DirectoryCache
from ..utils.project_utils import get_addon_prefs
from .. import i18n

class AssemblyPanel(Panel):
    bl_label = "Assembly"
    bl_idname = "VIEW3D_PT_assembly_manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Project'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        # Só mostrar se estiver em modo TEAM e tiver um projeto carregado
        if not context.scene.current_project:
            return False
        if not hasattr(context.scene, "project_settings"):
            return False
        return context.scene.project_settings.project_type == 'TEAM'
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(icon='COMMUNITY')
    
    def draw(self, context):
        layout = self.layout
        
        # Verificar se estamos em um arquivo de assembly
        is_assembly = False
        if bpy.data.filepath:
            filename = os.path.basename(bpy.data.filepath)
            is_assembly = "ASSEMBLY" in filename
        
        # Botões principais
        row = layout.row(align=True)
        row.operator("project.prepare_assembly", icon='MODIFIER')
        row.operator("project.rebuild_assembly", icon='FILE_REFRESH')
        
        # Status do assembly
        if context.scene.assembly_status:
            box = layout.box()
            box.label(text=i18n.translate("Assembly Status:"))
            box.label(text=context.scene.assembly_status)
        
        # Lista de funções
        if is_assembly:
            box = layout.box()
            box.label(text=i18n.translate("Roles:"), icon='OUTLINER_COLLECTION')
            
            # Listar todas as funções
            prefs = get_addon_prefs()
            if prefs:
                for rm in prefs.role_mappings:
                    if rm.role_name != "ASSEMBLY":
                        row = box.row()
                        # Mostrar status da coleção
                        if rm.role_name in bpy.data.collections:
                            row.label(text=rm.role_name, icon=rm.icon if rm.icon != 'NONE' else 'CHECKMARK')
                        else:
                            row.label(text=rm.role_name, icon='ERROR')
                        
                        # Botões de ação
                        sub = row.row(align=True)
                        if rm.role_name in bpy.data.collections:
                            # Botão para atualizar
                            op = sub.operator("project.reload_link", icon='FILE_REFRESH', text="")
                            # Botão para remover
                            op = sub.operator("project.unlink_role", icon='X', text="")
                            op.selected_role = rm.role_name
                        else:
                            # Botão para linkar
                            op = sub.operator("project.link_role", icon='LINKED', text="")
                            op.selected_role = rm.role_name
            
            # Ferramentas de limpeza
            box = layout.box()
            box.label(text=i18n.translate("Cleanup Tools:"), icon='BRUSH_DATA')
            row = box.row(align=True)
            row.operator("project.clean_missing", icon='GHOST_ENABLED')
            row.operator("project.clean_unused", icon='TRASH')

def register():
    bpy.utils.register_class(AssemblyPanel)

def unregister():
    bpy.utils.unregister_class(AssemblyPanel) 