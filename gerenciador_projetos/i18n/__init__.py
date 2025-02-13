"""
Internationalization module for the Project Manager addon.
"""

from .translations import (
    register as register_translations,
    unregister as unregister_translations,
    translate,
    translations,
    en_US,
    pt_BR
)

def register():
    """Register translations"""
    register_translations()

def unregister():
    """Unregister translations"""
    unregister_translations()

__all__ = [
    'register',
    'unregister',
    'translate',
    'translations',
    'en_US',
    'pt_BR'
] 