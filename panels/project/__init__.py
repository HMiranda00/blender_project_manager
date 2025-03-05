"""
Submódulo de painéis para o gerenciamento de projetos no Blender Project Manager.
"""

from .main_panel import PROJECT_PT_Panel, tag_redraw_all_areas

__all__ = [
    'PROJECT_PT_Panel',
    'tag_redraw_all_areas'
]

def register():
    PROJECT_PT_Panel.register()
    
def unregister():
    PROJECT_PT_Panel.unregister() 