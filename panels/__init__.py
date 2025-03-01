from . import project_panel
from . import file_notes_panel

def register():
    project_panel.register()
    file_notes_panel.register()

def unregister():
    file_notes_panel.unregister()
    project_panel.unregister()