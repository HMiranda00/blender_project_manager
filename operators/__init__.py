from . import create_project
from . import create_shot
from . import load_project
from . import link_role
from . import asset_operators
from . import ui_operators
from . import shot_browser
from . import open_role_file
from . import asset_browser_setup
from . import asset_browser_view
from . import recent_projects

def register():
    create_project.register()
    create_shot.register()
    load_project.register()
    link_role.register()
    asset_operators.register()
    ui_operators.register()
    shot_browser.register()
    open_role_file.register()
    asset_browser_setup.register()
    asset_browser_view.register()
    recent_projects.register()

def unregister():
    asset_browser_view.unregister()
    asset_browser_setup.unregister()
    open_role_file.unregister()
    shot_browser.unregister()
    ui_operators.unregister()
    asset_operators.unregister()
    link_role.unregister()
    load_project.unregister()
    create_shot.unregister()
    create_project.unregister()
    recent_projects.unregister()