"""
Project Context module for managing project state.
This module handles saving and loading project state to/from files.
"""

import os
import json
import time
import bpy
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
from ..utils import get_project_info

CONTEXT_FILE_NAME = "project_context.json"

@dataclass
class ProjectSettings:
    """Project settings data class"""
    project_type: str = "TEAM"  # TEAM or SOLO
    asset_linking: str = "LINK"  # LINK or APPEND
    use_versioning: bool = True

@dataclass
class RecentFile:
    """Recent file data class"""
    path: str
    name: str
    timestamp: float

@dataclass
class ProjectContext:
    """Project context data"""
    current_project: str = ""
    current_shot: str = ""
    current_role: str = ""
    current_version: int = 1
    is_team_project: bool = False
    project_name: str = ""
    project_prefix: str = ""
    project_path: str = ""
    settings: ProjectSettings = field(default_factory=ProjectSettings)
    recent_files: List[RecentFile] = field(default_factory=list)
    last_publish_time: Optional[str] = None
    version_status: Optional[str] = None
    assembly_status: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "current_project": self.current_project,
            "project_path": self.project_path,
            "current_shot": self.current_shot,
            "current_role": self.current_role,
            "settings": asdict(self.settings),
            "recent_files": [asdict(rf) for rf in self.recent_files],
            "last_publish_time": self.last_publish_time,
            "version_status": self.version_status,
            "assembly_status": self.assembly_status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectContext':
        """Create from dictionary"""
        settings = ProjectSettings(**data.get("settings", {}))
        recent_files = [
            RecentFile(**rf) for rf in data.get("recent_files", [])
        ]
        return cls(
            current_project=data.get("current_project", ""),
            project_path=data.get("project_path", ""),
            current_shot=data.get("current_shot", ""),
            current_role=data.get("current_role", ""),
            settings=settings,
            recent_files=recent_files,
            last_publish_time=data.get("last_publish_time"),
            version_status=data.get("version_status"),
            assembly_status=data.get("assembly_status")
        )
    
    def add_recent_file(self, path: str, name: str):
        """Add a file to recent files"""
        # Remove if already exists
        self.recent_files = [rf for rf in self.recent_files if rf.path != path]
        
        # Add to start of list
        self.recent_files.insert(0, RecentFile(
            path=path,
            name=name,
            timestamp=time.time()
        ))
        
        # Keep only last 10
        self.recent_files = self.recent_files[:10]
    
    def update_publish_time(self):
        """Update the last publish time"""
        self.last_publish_time = datetime.now().strftime("%d/%m/%Y %H:%M")

    @property
    def context_file_path(self):
        """Retorna o caminho do arquivo de contexto"""
        if not bpy.data.filepath:
            return None
        
        project_dir = os.path.dirname(os.path.dirname(bpy.data.filepath))
        return os.path.join(project_dir, CONTEXT_FILE_NAME)
    
    def save_context(self):
        """Salva o contexto atual em um arquivo JSON"""
        if not self.context_file_path:
            return False
            
        context_data = {
            'current_project': self.current_project,
            'project_path': self.project_path,
            'current_shot': self.current_shot,
            'current_role': self.current_role,
            'project_type': self.settings.project_type,
            'last_publish_time': self.last_publish_time,
            'version_status': self.version_status,
            'assembly_status': self.assembly_status
        }
        
        try:
            with open(self.context_file_path, 'w') as f:
                json.dump(context_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar contexto: {str(e)}")
            return False
    
    def load_context(self):
        """Carrega o contexto do arquivo JSON"""
        if not self.context_file_path or not os.path.exists(self.context_file_path):
            return False
            
        try:
            with open(self.context_file_path, 'r') as f:
                context_data = json.load(f)
                
            self.current_project = context_data.get('current_project', '')
            self.project_path = context_data.get('project_path', '')
            self.current_shot = context_data.get('current_shot', '')
            self.current_role = context_data.get('current_role', '')
            self.settings.project_type = context_data.get('project_type', 'TEAM')
            self.last_publish_time = context_data.get('last_publish_time')
            self.version_status = context_data.get('version_status')
            self.assembly_status = context_data.get('assembly_status')
            
            # Atualiza o contexto do Blender
            self.update_blender_context()
            return True
        except Exception as e:
            print(f"Erro ao carregar contexto: {str(e)}")
            return False
    
    def update_blender_context(self):
        """Atualiza o contexto do Blender com as informaÃ§Ãµes carregadas"""
        scene = bpy.context.scene
        
        if not hasattr(scene, "project_settings"):
            return
            
        scene.current_project = self.current_project or ""
        scene.current_shot = self.current_shot or ""
        scene.current_role = self.current_role or ""
        scene.project_settings.project_type = self.settings.project_type
        
        if self.last_publish_time:
            scene.last_publish_time = self.last_publish_time
        if self.version_status:
            scene.version_status = self.version_status
        if self.assembly_status:
            scene.assembly_status = self.assembly_status
    
    def update_from_blender(self):
        """Atualiza o contexto a partir do Blender"""
        scene = bpy.context.scene
        
        if not hasattr(scene, "project_settings"):
            return
            
        self.current_project = scene.current_project
        self.project_path = scene.current_project
        self.current_shot = scene.current_shot
        self.current_role = scene.current_role
        self.settings.project_type = scene.project_settings.project_type
        
        if hasattr(scene, "last_publish_time"):
            self.last_publish_time = scene.last_publish_time
        if hasattr(scene, "version_status"):
            self.version_status = scene.version_status
        if hasattr(scene, "assembly_status"):
            self.assembly_status = scene.assembly_status
        
        # Salva o contexto atualizado
        self.save_context()

# InstÃ¢ncia global do contexto
project_context = ProjectContext()

def get_project_context():
    """Retorna a instÃ¢ncia global do contexto"""
    return project_context

def load_project_context():
    """Carrega o contexto do projeto"""
    return project_context.load_context()

def save_project_context():
    """Salva o contexto do projeto"""
    project_context.update_from_blender()
    return project_context.save_context()

class ProjectContextManager:
    """Manages project context persistence"""
    
    def __init__(self):
        self.context_filename = ".project_context.json"
    
    def get_context_path(self, project_path: str) -> str:
        """Get the path to the context file for a project"""
        return os.path.join(project_path, self.context_filename)
    
    def load(self, project_path: str) -> ProjectContext:
        """Load project context from file"""
        try:
            context_path = self.get_context_path(project_path)
            if os.path.exists(context_path):
                with open(context_path, 'r') as f:
                    data = json.load(f)
                    return ProjectContext.from_dict(data)
            return ProjectContext()
        except Exception as e:
            print(f"Error loading project context: {str(e)}")
            return ProjectContext()
    
    def save(self, context: ProjectContext) -> bool:
        """Save project context to file"""
        try:
            context_path = self.get_context_path(context.project_path)
            with open(context_path, 'w') as f:
                json.dump(context.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving project context: {str(e)}")
            return False
    
    @classmethod
    def update_context(cls, project_path: str, **kwargs):
        """Update specific fields in the context"""
        manager = cls()
        context = manager.load(project_path)
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(context, key):
                setattr(context, key, value)
        
        # Save updated context
        manager.save(context)
        
        return context 
