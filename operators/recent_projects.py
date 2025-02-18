import bpy
import os
from bpy.types import Operator

class OpenRecentProjectOperator(Operator):
    bl_idname = "project.open_recent"
    bl_label = "Abrir Projeto Recente"
    
    project_path: bpy.props.StringProperty()
    is_fixed_root: bpy.props.BoolProperty()
    
    def execute(self, context):
        prefs = context.preferences.addons['project_manager'].preferences
        
        if prefs.use_fixed_root != self.is_fixed_root:
            self.report({'ERROR'}, 
                "O modo de raiz atual não corresponde ao modo usado quando o projeto foi salvo. "
                "Ajuste o modo nas preferências do addon primeiro.")
            return {'CANCELLED'}
            
        if prefs.use_fixed_root:
            bpy.ops.project.load_project(selected_project=self.project_path)
        else:
            bpy.ops.project.load_project(project_path=self.project_path)
            
        return {'FINISHED'}

class ClearRecentListOperator(Operator):
    bl_idname = "project.clear_recent_list"
    bl_label = "Limpar Lista"
    bl_description = "Limpar lista de projetos recentes"
    
    def execute(self, context):
        prefs = context.preferences.addons['project_manager'].preferences
        prefs.recent_projects.clear()
        self.report({'INFO'}, "Lista de projetos recentes limpa")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

class RemoveRecentProjectOperator(Operator):
    bl_idname = "project.remove_recent"
    bl_label = "Remover Projeto"
    bl_description = "Remover projeto da lista de recentes"
    
    project_path: bpy.props.StringProperty()
    
    def execute(self, context):
        prefs = context.preferences.addons['project_manager'].preferences
        for i, proj in enumerate(prefs.recent_projects):
            if proj.path == self.project_path:
                prefs.recent_projects.remove(i)
                break
        return {'FINISHED'}

def add_recent_project(context, project_path, project_name):
    MAX_RECENT = 5
    prefs = context.preferences.addons['project_manager'].preferences
    
    # Remover se já existe
    recent_projects = prefs.recent_projects
    for i, proj in enumerate(recent_projects):
        if proj.path == project_path:
            recent_projects.remove(i)
            break
    
    # Adicionar novo projeto no início
    new_project = recent_projects.add()
    new_project.path = project_path
    new_project.name = project_name
    new_project.is_fixed_root = prefs.use_fixed_root
    
    # Manter apenas os últimos MAX_RECENT projetos
    while len(recent_projects) > MAX_RECENT:
        recent_projects.remove(len(recent_projects) - 1)
    
    # Forçar atualização da UI
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()

def register():
    bpy.utils.register_class(OpenRecentProjectOperator)
    bpy.utils.register_class(ClearRecentListOperator)
    bpy.utils.register_class(RemoveRecentProjectOperator)

def unregister():
    bpy.utils.unregister_class(RemoveRecentProjectOperator)
    bpy.utils.unregister_class(ClearRecentListOperator)
    bpy.utils.unregister_class(OpenRecentProjectOperator)