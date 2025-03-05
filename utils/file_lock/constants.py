"""
Constantes usadas pelo gerenciador de bloqueio de arquivos.
"""

# Tempo de inatividade em segundos antes de desbloquear automaticamente
DEFAULT_INACTIVITY_TIMEOUT = 300  # 5 minutos

# Intervalos de verificação em segundos
ACTIVITY_CHECK_INTERVAL = 10  # Verifica atividade a cada 10 segundos
SAVE_INTERVAL = 120  # Salva a cada 2 minutos em caso de arquivo bloqueado e com alterações 