import time
import os
import gc
from typing import Set, Dict, Any, Optional

class DirectoryCache:
    _cache: Dict[str, Set[str]] = {}
    _last_update: Dict[str, float] = {}
    _max_age: float = 1.0  # 1 segundo de cache por padrão
    _max_entries: int = 100  # Máximo de diretórios em cache
    _memory_threshold: int = 100 * 1024 * 1024  # 100MB

    @staticmethod
    def get_files(directory: str, max_age: Optional[float] = None) -> Set[str]:
        """Retorna lista de arquivos do diretório, usando cache se disponível"""
        if max_age is None:
            max_age = DirectoryCache._max_age

        current_time = time.time()
        
        # Verificar se precisamos limpar o cache
        DirectoryCache._check_memory()
        
        # Verificar se o cache existe e é válido
        if directory in DirectoryCache._cache:
            if current_time - DirectoryCache._last_update[directory] < max_age:
                # Atualizar contagem de acesso
                DirectoryCache._last_update[directory] = current_time
                return DirectoryCache._cache[directory]

        # Limpar cache se necessário
        DirectoryCache._cleanup()

        # Atualizar cache
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
    def invalidate(directory: Optional[str] = None) -> None:
        """Invalida o cache de um diretório ou todo o cache"""
        if directory:
            DirectoryCache._cache.pop(directory, None)
            DirectoryCache._last_update.pop(directory, None)
        else:
            DirectoryCache._cache.clear()
            DirectoryCache._last_update.clear()
        
        # Forçar coleta de lixo
        gc.collect()

    @staticmethod
    def _cleanup() -> None:
        """Limpa entradas antigas do cache"""
        if len(DirectoryCache._cache) > DirectoryCache._max_entries:
            # Ordenar por último acesso
            sorted_entries = sorted(
                DirectoryCache._last_update.items(),
                key=lambda x: x[1]
            )
            
            # Remover entradas mais antigas
            for directory, _ in sorted_entries[:-DirectoryCache._max_entries]:
                DirectoryCache._cache.pop(directory, None)
                DirectoryCache._last_update.pop(directory, None)

    @staticmethod
    def _check_memory() -> None:
        """Verifica uso de memória e limpa se necessário"""
        try:
            import psutil
            process = psutil.Process()
            memory_use = process.memory_info().rss
            
            if memory_use > DirectoryCache._memory_threshold:
                DirectoryCache.invalidate()
        except ImportError:
            # Se psutil não estiver disponível, usar limpeza baseada em tamanho
            if len(DirectoryCache._cache) > DirectoryCache._max_entries // 2:
                DirectoryCache._cleanup()