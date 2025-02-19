import time
import os

class DirectoryCache:
    _cache = {}
    _last_update = {}
    _max_age = 1.0  # 1 segundo de cache por padrão

    @staticmethod
    def get_files(directory, max_age=None):
        """Retorna lista de arquivos do diretório, usando cache se disponível"""
        if max_age is None:
            max_age = DirectoryCache._max_age

        current_time = time.time()
        
        # Verificar se o cache existe e é válido
        if directory in DirectoryCache._cache:
            if current_time - DirectoryCache._last_update[directory] < max_age:
                return DirectoryCache._cache[directory]

        # Atualizar cache se necessário
        try:
            DirectoryCache._cache[directory] = set(os.listdir(directory))
            DirectoryCache._last_update[directory] = current_time
            return DirectoryCache._cache[directory]
        except Exception:
            # Se houver erro, limpar cache deste diretório
            DirectoryCache._cache.pop(directory, None)
            DirectoryCache._last_update.pop(directory, None)
            return set()

    @staticmethod
    def invalidate(directory=None):
        """Invalida o cache de um diretório ou todo o cache"""
        if directory:
            DirectoryCache._cache.pop(directory, None)
            DirectoryCache._last_update.pop(directory, None)
        else:
            DirectoryCache._cache.clear()
            DirectoryCache._last_update.clear()