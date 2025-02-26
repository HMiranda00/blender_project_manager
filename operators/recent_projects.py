import bpy
import os
from bpy.types import Operator
import re

class OpenRecentProjectOperator(Operator):
    bl_idname = "project.open_recent"
    bl_label = "Open Recent Project"
    
    project_path: bpy.props.StringProperty()
    is_fixed_root: bpy.props.BoolProperty()
    
    def execute(self, context):
        prefs = context.preferences.addons['blender_project_manager'].preferences
        
        if prefs.use_fixed_root != self.is_fixed_root:
            self.report({'ERROR'}, 
                "Current root mode does not match the mode used when the project was saved. "
                "Please adjust the mode in addon preferences first.")
            return {'CANCELLED'}
        
        # Close all open dialogs
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'INFO':  # Area where dialogs are shown
                    override = context.copy()
                    override['window'] = window
                    override['screen'] = window.screen
                    override['area'] = area
                    bpy.ops.screen.area_close(override)
        
        # Load project
        if prefs.use_fixed_root:
            bpy.ops.project.load_project(selected_project=self.project_path)
        else:
            bpy.ops.project.load_project(project_path=self.project_path)
            
        return {'FINISHED'}

class ClearRecentListOperator(Operator):
    bl_idname = "project.clear_recent_list"
    bl_label = "Clear List"
    bl_description = "Clear recent projects list"
    
    def execute(self, context):
        prefs = context.preferences.addons['blender_project_manager'].preferences
        prefs.recent_projects.clear()
        self.report({'INFO'}, "Recent projects list cleared")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

class RemoveRecentProjectOperator(Operator):
    bl_idname = "project.remove_recent"
    bl_label = "Remove Project"
    bl_description = "Remove project from recent list"
    
    project_path: bpy.props.StringProperty()
    
    def execute(self, context):
        prefs = context.preferences.addons['blender_project_manager'].preferences
        for i, proj in enumerate(prefs.recent_projects):
            if proj.path == self.project_path:
                prefs.recent_projects.remove(i)
                break
                
        # Force UI update
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()
                
        return {'FINISHED'}

def add_recent_project(context, project_path, project_name):
    """Add a project to recent list"""
    MAX_RECENT = 5
    prefs = context.preferences.addons['blender_project_manager'].preferences
    
    print(f"\n[DEBUG] Adding recent project:")
    print(f"Path: {project_path}")
    print(f"Name: {project_name}")
    
    # Remove if already exists
    recent_projects = prefs.recent_projects
    for i, proj in enumerate(recent_projects):
        if proj.path == project_path:
            print(f"[DEBUG] Removing existing project at position {i}")
            recent_projects.remove(i)
            break
    
    # Add new project at the beginning
    new_project = recent_projects.add()
    new_project.path = project_path
    new_project.name = project_name
    new_project.is_fixed_root = prefs.use_fixed_root
    
    print(f"[DEBUG] Project added:")
    print(f"Path: {new_project.path}")
    print(f"Name: {new_project.name}")
    print(f"Fixed Root: {new_project.is_fixed_root}")
    
    # Keep only the last MAX_RECENT projects
    while len(recent_projects) > MAX_RECENT:
        recent_projects.remove(len(recent_projects) - 1)
    
    print(f"[DEBUG] Total recent projects: {len(recent_projects)}")
    
    # Force UI update
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()

class PROJECT_MT_recent_menu(bpy.types.Menu):
    bl_label = "Recent Projects"
    bl_idname = "PROJECT_MT_recent_menu"
    
    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons['blender_project_manager'].preferences
        
        print("\n[DEBUG] Drawing recent projects menu")
        print(f"Total projects: {len(prefs.recent_projects)}")
        
        for recent in prefs.recent_projects:
            # Determine display name
            if recent.name and recent.name.strip():
                project_name = recent.name
                print(f"[DEBUG] Using stored name: {project_name}")
            else:
                project_name = os.path.basename(recent.path.rstrip(os.path.sep))
                if recent.is_fixed_root:
                    match = re.match(r'^(\d+)\s*-\s*(.+)$', project_name)
                    if match:
                        project_name = match.group(2).strip()
                print(f"[DEBUG] Using folder name: {project_name}")
            
            # Ensure we have a name to display
            if not project_name or not project_name.strip():
                project_name = os.path.basename(recent.path.rstrip(os.path.sep))
                print(f"[DEBUG] Using folder name as fallback: {project_name}")
            
            print(f"[DEBUG] Project in menu:")
            print(f"Path: {recent.path}")
            print(f"Stored name: {recent.name}")
            print(f"Display name: {project_name}")
            
            props = layout.operator(
                "project.open_recent",
                text=project_name,
                icon='FILE_FOLDER'
            )
            props.project_path = recent.path
            props.is_fixed_root = recent.is_fixed_root
        
        if len(prefs.recent_projects) > 0:
            layout.separator()
            layout.operator("project.clear_recent_list", text="Clear List", icon='TRASH')

def register():
    bpy.utils.register_class(OpenRecentProjectOperator)
    bpy.utils.register_class(ClearRecentListOperator)
    bpy.utils.register_class(RemoveRecentProjectOperator)
    bpy.utils.register_class(PROJECT_MT_recent_menu)
    print("[DEBUG] Recent projects operators registered")

def unregister():
    bpy.utils.unregister_class(RemoveRecentProjectOperator)
    bpy.utils.unregister_class(ClearRecentListOperator)
    bpy.utils.unregister_class(OpenRecentProjectOperator)
    bpy.utils.unregister_class(PROJECT_MT_recent_menu)
    print("[DEBUG] Recent projects operators unregistered")