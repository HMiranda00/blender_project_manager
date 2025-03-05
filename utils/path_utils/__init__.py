"""
Utilitários para manipulação de caminhos e informações de projeto.
"""

from .project_paths import (
    get_project_info,
    get_next_project_number,
    get_publish_path,
    verify_role_file,
    get_wip_path,
    get_latest_wip,
    get_role_path,
    get_assembly_path
)

__all__ = [
    'get_project_info',
    'get_next_project_number',
    'get_publish_path',
    'verify_role_file',
    'get_wip_path',
    'get_latest_wip',
    'get_role_path',
    'get_assembly_path'
] 