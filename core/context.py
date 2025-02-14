import bpy
import os
import json
from pathlib import Path
from .. import i18n

# Constants
CONTEXT_FILENAME = ".project_context.json"

class ProjectContext:
    """Class to manage project context in a file"""
    
    def __init__(self):
        self.project_path = ""
        self.shot_name = ""
        self.role_name = ""
        self.is_team_mode = False
        self.last_file = ""
        self.version = 1
        
    @property
    def context_file(self):
        """Get the path to the context file"""
        if not self.project_path:
            return None
        return os.path.join(self.project_path, CONTEXT_FILENAME)
        
    def to_dict(self):
        """Convert context to dictionary"""
        return {
            "project_path": self.project_path,
            "shot_name": self.shot_name,
            "role_name": self.role_name,
            "is_team_mode": self.is_team_mode,
            "last_file": self.last_file,
            "version": self.version
        }
        
    def from_dict(self, data):
        """Load context from dictionary"""
        self.project_path = data.get("project_path", "")
        self.shot_name = data.get("shot_name", "")
        self.role_name = data.get("role_name", "")
        self.is_team_mode = data.get("is_team_mode", False)
        self.last_file = data.get("last_file", "")
        self.version = data.get("version", 1)
        
    def save(self):
        """Save context to file"""
        if not self.context_file:
            return False
            
        try:
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving context: {str(e)}")
            return False
            
    def load(self):
        """Load context from file"""
        if not self.context_file or not os.path.exists(self.context_file):
            return False
            
        try:
            with open(self.context_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.from_dict(data)
            return True
        except Exception as e:
            print(f"Error loading context: {str(e)}")
            return False
            
    def clear(self):
        """Clear context data"""
        self.__init__()
        
    def update_from_scene(self):
        """Update context from scene properties"""
        scene = bpy.context.scene
        prefs = bpy.context.preferences.addons[__package__.split('.')[0]].preferences
        
        # Get current values
        self.project_path = getattr(scene, "current_project", "")
        self.shot_name = getattr(scene, "current_shot", "")
        self.role_name = getattr(scene, "current_role", "")
        self.is_team_mode = getattr(prefs, "is_team_mode", False)
        self.last_file = bpy.data.filepath
        
        # Save to file
        self.save()
        
    def update_to_scene(self):
        """Update scene properties from context"""
        scene = bpy.context.scene
        prefs = bpy.context.preferences.addons[__package__.split('.')[0]].preferences
        
        # Set values
        scene.current_project = self.project_path
        scene.current_shot = self.shot_name
        scene.current_role = self.role_name
        prefs.is_team_mode = self.is_team_mode
        
    def validate(self):
        """Validate context data"""
        if not self.project_path:
            return False, i18n.translate("No project selected")
            
        if not os.path.exists(self.project_path):
            return False, i18n.translate("Project not found")
            
        if self.shot_name and not os.path.exists(os.path.join(self.project_path, "shots", self.shot_name)):
            return False, i18n.translate("Shot not found")
            
        if self.role_name and not os.path.exists(os.path.join(self.project_path, "shots", self.shot_name, self.role_name)):
            return False, i18n.translate("Role not found")
            
        return True, ""

# Global context instance
_context = None

def get_context():
    """Get the global context instance"""
    global _context
    if _context is None:
        _context = ProjectContext()
    return _context

def save_context():
    """Save the current context"""
    ctx = get_context()
    ctx.update_from_scene()
    return ctx.save()
    
def load_context():
    """Load the saved context"""
    ctx = get_context()
    if ctx.load():
        ctx.update_to_scene()
        return True
    return False
    
def clear_context():
    """Clear the current context"""
    ctx = get_context()
    ctx.clear()
    ctx.update_to_scene()
    
def validate_context():
    """Validate the current context"""
    ctx = get_context()
    return ctx.validate() 
