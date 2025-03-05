"""
Gerenciador de bloqueio de arquivos para o Blender Project Manager.
Previne edição simultânea de arquivos por diferentes usuários.
"""

from .manager import FileLockManager
from .constants import DEFAULT_INACTIVITY_TIMEOUT, ACTIVITY_CHECK_INTERVAL, SAVE_INTERVAL

# Singleton para acessar de qualquer lugar
file_lock_manager = FileLockManager()

__all__ = [
    'file_lock_manager',
    'FileLockManager',
    'DEFAULT_INACTIVITY_TIMEOUT',
    'ACTIVITY_CHECK_INTERVAL',
    'SAVE_INTERVAL'
] 