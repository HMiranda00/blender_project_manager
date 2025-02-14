"""
Project context management
"""
import bpy
import os
import json
from . import get_project_info
from .project_utils import get_addon_prefs

def save_project_context():
    """Save project context to file"""
    try:
        context = bpy.context
        if not context.scene.current_project:
            return False
            
        prefs = get_addon_prefs()
        if not prefs:
            return False
            
        project_name, workspace_path, _ = get_project_info(
            context.scene.current_project,
            prefs.use_fixed_root
        )
        
        # Create context data
        context_data = {
            "project_path": context.scene.current_project,
            "current_shot": context.scene.current_shot if hasattr(context.scene, "current_shot") else "",
            "current_role": context.scene.current_role if hasattr(context.scene, "current_role") else "",
            "project_settings": {
                "project_type": context.scene.project_settings.project_type,
                "asset_linking": context.scene.project_settings.asset_linking,
                "use_versioning": context.scene.project_settings.use_versioning
            }
        }
        
        # Save to file
        context_file = os.path.join(workspace_path, ".project_context")
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(context_data, f, indent=4)
            
        return True
        
    except Exception as e:
        print(f"Erro salvando contexto: {str(e)}")
        return False

def load_project_context(project_path):
    """Load project context from file"""
    try:
        if not project_path or not os.path.exists(project_path):
            return False
            
        prefs = get_addon_prefs()
        if not prefs:
            return False
            
        project_name, workspace_path, _ = get_project_info(
            project_path,
            prefs.use_fixed_root
        )
        
        # Load from file
        context_file = os.path.join(workspace_path, ".project_context")
        if not os.path.exists(context_file):
            return False
            
        with open(context_file, 'r', encoding='utf-8') as f:
            context_data = json.load(f)
            
        # Apply context
        context = bpy.context
        context.scene.current_project = context_data["project_path"]
        
        if "current_shot" in context_data:
            context.scene.current_shot = context_data["current_shot"]
            
        if "current_role" in context_data:
            context.scene.current_role = context_data["current_role"]
            
        if "project_settings" in context_data:
            settings = context_data["project_settings"]
            context.scene.project_settings.project_type = settings["project_type"]
            context.scene.project_settings.asset_linking = settings["asset_linking"]
            context.scene.project_settings.use_versioning = settings["use_versioning"]
            
        return True
        
    except Exception as e:
        print(f"Erro carregando contexto: {str(e)}")
        return False 