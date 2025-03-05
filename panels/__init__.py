from . import project
from . import file_notes_panel

def register():
    project.register()
    file_notes_panel.register()

def unregister():
    file_notes_panel.unregister()
    project.unregister()