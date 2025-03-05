def register():
    from . import create_project
    from . import load_project
    from . import create_shot
    from . import open_shot
    from . import link_role
    from . import open_role_file
    from . import create_role_file
    from . import assets
    from . import recent_projects
    from . import ui_operators
    from . import version_control
    from . import assembly
    
    create_project.register()
    load_project.register()
    create_shot.register()
    open_shot.register()
    link_role.register()
    open_role_file.register()
    create_role_file.register()
    assets.register()
    recent_projects.register()
    ui_operators.register()
    version_control.register()
    assembly.register()

def unregister():
    from . import create_project
    from . import load_project
    from . import create_shot
    from . import open_shot
    from . import link_role
    from . import open_role_file
    from . import create_role_file
    from . import assets
    from . import recent_projects
    from . import ui_operators
    from . import version_control
    from . import assembly
    
    assembly.unregister()
    version_control.unregister()
    ui_operators.unregister()
    recent_projects.unregister()
    assets.unregister()
    create_role_file.unregister()
    open_role_file.unregister()
    link_role.unregister()
    open_shot.unregister()
    create_shot.unregister()
    load_project.unregister()
    create_project.unregister()