from .utils import get_assembly_path, get_role_publish_file
from .rebuild import ASSEMBLY_OT_rebuild
from .render import ASSEMBLY_OT_prepare_render
from .open import ASSEMBLY_OT_open, ASSEMBLY_OT_open_directory

def register():
    from . import rebuild
    from . import render
    from . import open
    
    rebuild.register()
    render.register()
    open.register()

def unregister():
    from . import rebuild
    from . import render
    from . import open
    
    open.unregister()
    render.unregister()
    rebuild.unregister()

__all__ = [
    'get_assembly_path',
    'get_role_publish_file',
    'ASSEMBLY_OT_rebuild',
    'ASSEMBLY_OT_prepare_render',
    'ASSEMBLY_OT_open',
    'ASSEMBLY_OT_open_directory'
]