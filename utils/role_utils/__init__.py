"""
Utilitários para manipulação de papéis (roles) no Blender Project Manager.
"""

from .role_functions import (
    get_roles,
    get_role_settings,
    open_role_file,
    setup_collection_settings,
    setup_role_world
)

__all__ = [
    'get_roles',
    'get_role_settings',
    'open_role_file',
    'setup_collection_settings',
    'setup_role_world'
] 