"""
Painel principal do gerenciamento de projetos.
"""

import bpy
from bpy.types import Panel
from ...preferences import get_addon_preferences
from ...utils.path_utils import verify_role_file
from ...utils.role_utils import open_role_file
from .sections import (
    draw_header_section,
    draw_recent_projects_section,
    draw_shot_management_section,
    draw_role_management_section,
    draw_current_role_tools_section,
    draw_assembly_tools_section,
    draw_utilities_section
)

class PROJECT_PT_Panel(Panel):
    bl_label = "Blender Project Manager"
    bl_idname = "VIEW3D_PT_project_management"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Project'
    
    verify_role_file = verify_role_file
    open_role_file = open_role_file
    
    def draw(self, context):
        layout = self.layout
        prefs = get_addon_preferences(context)

        # 1. HEADER - Projeto Atual ou Seleção de Projeto
        draw_header_section(layout, context)
        
        # Se não há projeto atual, mostrar projetos recentes e retornar
        if not context.scene.current_project:
            draw_recent_projects_section(layout, context)
            return

        # 2. SHOT MANAGEMENT
        draw_shot_management_section(layout, context)

        # 3. ROLE MANAGEMENT
        draw_role_management_section(layout, context, self)

        # 4. CURRENT ROLE TOOLS
        draw_current_role_tools_section(layout, context)

        # 5. ASSEMBLY TOOLS
        draw_assembly_tools_section(layout, context)

        # 6. UTILITIES
        draw_utilities_section(layout, context)

    @classmethod
    def register(cls):
        bpy.utils.register_class(cls)
    
    @classmethod
    def unregister(cls):
        bpy.utils.unregister_class(cls)

def tag_redraw_all_areas():
    """Force all areas to redraw"""
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw() 