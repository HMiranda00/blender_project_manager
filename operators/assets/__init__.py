from .asset_creation import ASSET_OT_create_asset
from .asset_reload import ASSET_OT_reload_links
from .browser_setup import ASSETBROWSER_OT_setup
from .browser_view import PROJECTMANAGER_OT_toggle_asset_browser

def register():
    from . import asset_creation
    from . import asset_reload
    from . import browser_setup
    from . import browser_view
    
    asset_creation.register()
    asset_reload.register()
    browser_setup.register()
    browser_view.register()

def unregister():
    from . import asset_creation
    from . import asset_reload
    from . import browser_setup
    from . import browser_view
    
    browser_view.unregister()
    browser_setup.unregister()
    asset_reload.unregister()
    asset_creation.unregister()

__all__ = [
    'ASSET_OT_create_asset',
    'ASSET_OT_reload_links',
    'ASSETBROWSER_OT_setup',
    'PROJECTMANAGER_OT_toggle_asset_browser'
] 