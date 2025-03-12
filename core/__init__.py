# Importar módulos necessários
from . import registry

# Exportar registry para uso em __init__.py
from .registry import register_all, unregister_all 