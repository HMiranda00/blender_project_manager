"""
Funções utilitárias para o painel de projeto.
"""

import bpy
import os
from ...preferences import get_addon_preferences
from ...utils.path_utils import verify_role_file
from ...utils.role_utils import open_role_file

# As funções verify_role_file e open_role_file foram movidas para os módulos de utilitários centralizados
# e são importadas acima para manter a compatibilidade com o código existente. 