import bpy
import os
from bpy.types import Operator, UIList, PropertyGroup
from bpy.props import StringProperty, IntProperty, CollectionProperty

class RecentProjectItem(PropertyGroup):
    name: StringProperty(name="Name")
    path: StringProperty(name="Path", subtype='DIR_PATH')

class PROJECTMANAGER_UL_recent_projects(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon='FILE_FOLDER')

class OpenRecentProjectOperator(Operator):
    bl_idname = "project.open_recent"
    bl_label = "Open Recent Project"
    
    project_path: bpy.props.StringProperty()
    
    def execute(self, context):
        if not self.project_path:
            return {'CANCELLED'}
            
        bpy.ops.project.load_project(project_path=self.project_path)
        return {'FINISHED'}

class ClearRecentListOperator(Operator):
    bl_idname = "project.clear_recent_list"
    bl_label = "Clear Recent Projects"
    bl_description = "Clear the recent projects list"
    
    def execute(self, context):
        prefs = context.preferences.addons['blender_project_manager'].preferences
        prefs.recent_projects.clear()
        return {'FINISHED'}

def add_recent_project(context, project_path, project_name):
    """Add a project to the recent projects list"""
    MAX_RECENT = 10
    prefs = context.preferences.addons['blender_project_manager'].preferences
    
    # Remove trailing slashes
    project_path = project_path.rstrip("\\/")
    
    # If project_name is empty, use folder name
    if not project_name:
        project_name = os.path.basename(project_path)
    
    # Remove if already exists
    recent_projects = prefs.recent_projects
    for i, proj in enumerate(recent_projects):
        if proj.path.rstrip("\\/") == project_path:
            recent_projects.remove(i)
            break
    
    # Add new project at the beginning
    new_project = recent_projects.add()
    new_project.path = project_path
    new_project.name = project_name
    
    # Move to first position
    recent_projects.move(len(recent_projects)-1, 0)
    
    # Keep only the last MAX_RECENT projects
    while len(recent_projects) > MAX_RECENT:
        recent_projects.remove(len(recent_projects) - 1)

def register():
    bpy.utils.register_class(RecentProjectItem)
    bpy.utils.register_class(PROJECTMANAGER_UL_recent_projects)
    bpy.utils.register_class(ClearRecentListOperator)
    
    # Adicionar propriedades para a UIList
    bpy.types.Scene.recent_project_list_index = IntProperty()
    bpy.types.Scene.recent_projects = CollectionProperty(type=RecentProjectItem)

def unregister():
    del bpy.types.Scene.recent_projects
    del bpy.types.Scene.recent_project_list_index
    
    bpy.utils.unregister_class(ClearRecentListOperator)
    bpy.utils.unregister_class(PROJECTMANAGER_UL_recent_projects)
    bpy.utils.unregister_class(RecentProjectItem)