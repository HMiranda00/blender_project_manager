def register():
    from . import create_project
    from . import load_project
    from . import create_shot
    from . import open_shot
    from . import link_role
    from . import open_role_file
    from . import asset_operators
    from . import asset_browser_setup
    from . import asset_browser_view
    from . import recent_projects
    from . import ui_operators
    from . import version_control
    from . import assembly_control
    
    create_project.register()
    load_project.register()
    create_shot.register()
    open_shot.register()
    link_role.register()
    open_role_file.register()
    asset_operators.register()
    asset_browser_setup.register()
    asset_browser_view.register()
    recent_projects.register()
    ui_operators.register()
    version_control.register()
    assembly_control.register()

def unregister():
    from . import create_project
    from . import load_project
    from . import create_shot
    from . import open_shot
    from . import link_role
    from . import open_role_file
    from . import asset_operators
    from . import asset_browser_setup
    from . import asset_browser_view
    from . import recent_projects
    from . import ui_operators
    from . import version_control
    from . import assembly_control
    
    assembly_control.unregister()
    version_control.unregister()
    ui_operators.unregister()
    recent_projects.unregister()
    asset_browser_view.unregister()
    asset_browser_setup.unregister()
    asset_operators.unregister()
    open_role_file.unregister()
    link_role.unregister()
    open_shot.unregister()
    create_shot.unregister()
    load_project.unregister()
    create_project.unregister()