import bpy
import os
import json
import threading
import time
from datetime import datetime

# Importar o gerenciador de notificações
from .notification_manager import notification_manager

# Tempo de inatividade em segundos antes de desbloquear automaticamente
DEFAULT_INACTIVITY_TIMEOUT = 300  # 5 minutos

# Intervalos de verificação em segundos
ACTIVITY_CHECK_INTERVAL = 10  # Verifica atividade a cada 10 segundos
SAVE_INTERVAL = 120  # Salva a cada 2 minutos em caso de arquivo bloqueado e com alterações

class FileLockManager:
    """Manages file locking to prevent simultaneous editing"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FileLockManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.locks = {}  # caminho_arquivo -> {user, timestamp, nota}
        self.lock_file_path = ""
        self.username = ""
        self.current_file = ""
        self.last_activity_time = datetime.now()
        self.monitoring = False
        self.activity_monitor_thread = None
        self.timer_save_event = None
        
        # Timer para auto-save em caso de arquivo bloqueado
        self.timer_save_handle = None
        
        # Tempo de inatividade em segundos
        self.inactivity_timeout = DEFAULT_INACTIVITY_TIMEOUT
        
        self._initialized = True
    
    def setup(self, locks_dir, username):
        """Configura o gerenciador com o diretório de locks e o nome de usuário"""
        os.makedirs(locks_dir, exist_ok=True)
        self.lock_file_path = os.path.join(locks_dir, "file_locks.json")
        self.username = username
        
        # Carrega os locks existentes
        self._load_locks()
        
        # Inicia o monitoramento de atividade se não estiver rodando
        if not self.monitoring:
            self._start_activity_monitoring()
    
    def _load_locks(self):
        """Loads locks from JSON file"""
        try:
            if os.path.exists(self.lock_file_path):
                with open(self.lock_file_path, 'r') as f:
                    self.locks = json.load(f)
        except Exception as e:
            print(f"Error loading locks file: {e}")
            self.locks = {}
    
    def _save_locks(self):
        """Saves locks to JSON file"""
        try:
            with open(self.lock_file_path, 'w') as f:
                json.dump(self.locks, f, indent=2)
        except Exception as e:
            print(f"Error saving locks file: {e}")
    
    def lock_file(self, file_path, note=""):
        """Locks a file for the current user"""
        if not file_path or not self.username:
            return False
            
        file_path = os.path.normpath(file_path)
        
        # Check if file is already locked by another user
        if file_path in self.locks and self.locks[file_path]["user"] != self.username:
            return False
            
        # Create lock info
        self.locks[file_path] = {
            "user": self.username,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": note
        }
        
        # Save locks to file
        self._save_locks()
        
        # Update current file
        self.current_file = file_path
        
        # Registra atividade
        self._register_activity()
        
        # Notify that file was locked
        notification_manager.notify_file_locked(file_path)
        
        # Start timer save if not already running
        if not self.timer_save_handle:
            self._start_timer_save()
        
        return True
    
    def unlock_file(self, file_path):
        """Desbloqueia um arquivo"""
        if not file_path:
            return False
            
        file_path = os.path.normpath(file_path)
        
        # Verifica se o arquivo está bloqueado pelo usuário atual
        if file_path not in self.locks or self.locks[file_path]["user"] != self.username:
            return False
            
        # Remove o lock
        if file_path in self.locks:
            del self.locks[file_path]
            
        # Salva os locks
        self._save_locks()
        
        # Limpa o arquivo atual se for o mesmo
        if self.current_file == file_path:
            self.current_file = ""
            
            # Para o timer de auto-save
            if self.timer_save_handle:
                bpy.app.timers.unregister(self.timer_save_handle)
                self.timer_save_handle = None
        
        # Notifica que o arquivo foi desbloqueado
        notification_manager.notify_file_unlocked(file_path)
        
        return True
    
    def is_file_locked(self, file_path):
        """Verifica se um arquivo está bloqueado"""
        if not file_path:
            return False
            
        file_path = os.path.normpath(file_path)
        return file_path in self.locks
    
    def is_locked_by_me(self, file_path):
        """Verifica se um arquivo está bloqueado pelo usuário atual"""
        if not file_path:
            return False
            
        file_path = os.path.normpath(file_path)
        return file_path in self.locks and self.locks[file_path]["user"] == self.username
    
    def get_lock_info(self, file_path):
        """Retorna informações sobre o lock de um arquivo"""
        if not file_path or file_path not in self.locks:
            return None
            
        file_path = os.path.normpath(file_path)
        return self.locks[file_path]
    
    def update_note(self, file_path, note):
        """Atualiza a nota de um arquivo"""
        if not file_path or not self.is_locked_by_me(file_path):
            return False
            
        file_path = os.path.normpath(file_path)
        
        # Atualiza a nota
        self.locks[file_path]["note"] = note
        
        # Salva os locks
        self._save_locks()
        
        # Registra atividade
        self._register_activity()
        
        # Notifica que uma nota foi adicionada
        notification_manager.notify_note_added(file_path, note)
        
        return True
    
    def get_note(self, file_path):
        """Retorna a nota de um arquivo"""
        if not file_path or file_path not in self.locks:
            return ""
            
        file_path = os.path.normpath(file_path)
        return self.locks[file_path].get("note", "")
    
    def _register_activity(self):
        """Registra atividade do usuário"""
        self.last_activity_time = datetime.now()
    
    def _check_inactivity(self):
        """Verifica se o usuário está inativo e desbloqueia o arquivo se necessário"""
        current_time = datetime.now()
        time_diff = (current_time - self.last_activity_time).total_seconds()
        
        # Se o usuário está inativo por mais tempo que o timeout e tem um arquivo bloqueado
        if time_diff > self.inactivity_timeout and self.current_file:
            # Tenta salvar o arquivo antes de desbloquear
            self._save_current_file()
            
            # Desbloqueia o arquivo
            self.unlock_file(self.current_file)
            
            print(f"Arquivo desbloqueado automaticamente após {self.inactivity_timeout} segundos de inatividade: {self.current_file}")
    
    def _save_current_file(self):
        """Salva o arquivo atual se estiver aberto e tiver alterações"""
        try:
            if bpy.data.is_dirty and self.current_file == bpy.data.filepath:
                bpy.ops.wm.save_mainfile()
                print(f"Arquivo salvo automaticamente: {self.current_file}")
                
                # Notifica que o arquivo foi salvo
                notification_manager.notify_file_saved(self.current_file)
        except Exception as e:
            print(f"Erro ao salvar arquivo: {e}")
    
    def _start_activity_monitoring(self):
        """Inicia o monitoramento de atividade em uma thread separada"""
        def monitor_activity():
            while self.monitoring:
                self._check_inactivity()
                time.sleep(ACTIVITY_CHECK_INTERVAL)
        
        self.monitoring = True
        self.activity_monitor_thread = threading.Thread(target=monitor_activity)
        self.activity_monitor_thread.daemon = True
        self.activity_monitor_thread.start()
    
    def _start_timer_save(self):
        """Inicia o timer para auto-save"""
        def timer_save():
            # Se não há arquivo atual, não continua o timer
            if not self.current_file:
                self.timer_save_handle = None
                return None
                
            # Verifica se o arquivo está bloqueado por nós e se tem alterações
            if self.is_locked_by_me(self.current_file) and bpy.data.is_dirty:
                self._save_current_file()
                
            # Continua o timer
            return SAVE_INTERVAL
        
        # Registra o timer
        self.timer_save_handle = bpy.app.timers.register(timer_save)
    
    def stop_monitoring(self):
        """Para o monitoramento de atividade"""
        self.monitoring = False
        
        # Para o timer de auto-save
        if self.timer_save_handle and self.timer_save_handle in bpy.app.timers.registered:
            bpy.app.timers.unregister(self.timer_save_handle)
            self.timer_save_handle = None
    
    def handle_file_open(self, file_path):
        """Manipula a abertura de um arquivo"""
        if not file_path:
            return
            
        file_path = os.path.normpath(file_path)
        
        # Desbloqueia o arquivo atual se for diferente
        if self.current_file and self.current_file != file_path:
            self.unlock_file(self.current_file)
            
        # Registra atividade
        self._register_activity()
        
        # Notifica que o arquivo foi aberto
        notification_manager.notify_file_opened(file_path)
        
        # Se o arquivo já está bloqueado por nós, atualiza o timestamp
        if self.is_locked_by_me(file_path):
            self.locks[file_path]["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._save_locks()
            return
            
        # Se o arquivo não está bloqueado, bloqueia automaticamente
        if not self.is_file_locked(file_path):
            self.lock_file(file_path)
    
    def handle_file_save(self, file_path):
        """Manipula o salvamento de um arquivo"""
        if not file_path:
            return
            
        file_path = os.path.normpath(file_path)
        
        # Registra atividade
        self._register_activity()
        
        # Notifica que o arquivo foi salvo
        notification_manager.notify_file_saved(file_path)
        
        # Se o arquivo já está bloqueado por nós, atualiza o timestamp
        if self.is_locked_by_me(file_path):
            self.locks[file_path]["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._save_locks()
            return
            
        # Se o arquivo não está bloqueado, bloqueia automaticamente
        if not self.is_file_locked(file_path):
            self.lock_file(file_path)

# Singleton para acessar de qualquer lugar
file_lock_manager = FileLockManager() 