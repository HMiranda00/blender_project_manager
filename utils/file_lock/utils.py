"""
Funções utilitárias para o gerenciador de bloqueio de arquivos.
"""

import os

def normalize_path(file_path):
    """Normaliza um caminho de arquivo para garantir consistência entre plataformas"""
    if not file_path:
        return ""
    return os.path.normpath(file_path) 