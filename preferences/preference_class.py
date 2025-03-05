"""
Main preference class definition for Blender Project Manager.
"""

import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import StringProperty, CollectionProperty, BoolProperty, IntProperty

class RecentProject(PropertyGroup):
    """
    Class to store information about a recent project
    
    Attributes:
        path: Path to the project
        name: Display name of the project
        is_fixed_root: Whether this project uses a fixed root
    """
    path: StringProperty(name="Project Path")
    name: StringProperty(name="Project Name")
    is_fixed_root: BoolProperty(name="Is Fixed Root")

class ProjectPreferences(AddonPreferences):
    """
    Main preferences class for Blender Project Manager addon
    
    This class stores all the user preferences for the addon, including
    project paths, role settings, and integration settings.
    """
    # bl_idname will be set dynamically during initialization
    # For Blender 4.0+, we need to be careful with how this is set
    # See initialize() function in __init__.py
    
    use_fixed_root: BoolProperty(
        name="Use Fixed Root",
        description="If checked, will use a fixed root folder for all projects",
        default=False
    )

    fixed_root_path: StringProperty(
        name="Fixed Root Path",
        subtype='DIR_PATH',
        default="",
        description="Path to the fixed root folder"
    )

    # Integration settings
    username: StringProperty(
        name="Username",
        description="Your username for notifications",
        default="",
    )

    discord_webhook_url: StringProperty(
        name="Discord Webhook URL",
        description="Discord webhook URL for notifications",
        default="",
        subtype='PASSWORD'
    )

    slack_webhook_url: StringProperty(
        name="Slack Webhook URL",
        description="Slack webhook URL for notifications",
        default="",
        subtype='PASSWORD'
    )

    inactivity_timeout: IntProperty(
        name="Inactivity Timeout (seconds)",
        description="Inactivity time in seconds before automatically unlocking files",
        default=300,
        min=60,
        max=3600
    )

    role_mappings: CollectionProperty(
        type=None,  # Will be set in register
        name="Role Settings",
        description="Define roles and their settings",
    )

    recent_projects: CollectionProperty(
        type=None,  # Will be set in register
        name="Recent Projects",
        description="List of recent projects"
    )

    show_all_recent: BoolProperty(
        name="Show All Projects",
        default=False,
        description="Show all recent projects or just the 3 most recent ones"
    )
    
    recent_search: StringProperty(
        name="Search",
        default="",
        description="Search in recent projects"
    )
    
    # UI settings
    ui_expanded_project: BoolProperty(
        name="Expanded Project Settings",
        default=True
    )
    
    ui_expanded_roles: BoolProperty(
        name="Expanded Role Settings",
        default=True
    )
    
    ui_expanded_notification: BoolProperty(
        name="Expanded Notification Settings",
        default=False
    )
    
    ui_expanded_recent: BoolProperty(
        name="Expanded Recent Projects",
        default=True
    )
    
    def draw(self, context):
        """
        Draw the preferences UI
        
        Args:
            context: Blender context
        """
        from .role_definitions import RoleMapping
        
        layout = self.layout
        
        # Project settings
        box = layout.box()
        row = box.row()
        row.prop(self, "ui_expanded_project", text="", icon='TRIA_DOWN' if self.ui_expanded_project else 'TRIA_RIGHT', emboss=False)
        row.label(text="Project Settings")
        
        if self.ui_expanded_project:
            box.prop(self, "use_fixed_root")
            if self.use_fixed_root:
                box.prop(self, "fixed_root_path")
        
        # Role settings
        box = layout.box()
        row = box.row()
        row.prop(self, "ui_expanded_roles", text="", icon='TRIA_DOWN' if self.ui_expanded_roles else 'TRIA_RIGHT', emboss=False)
        row.label(text="Role Settings")
        
        if self.ui_expanded_roles:
            if not self.role_mappings:
                box.label(text="No roles defined")
            else:
                for idx, role in enumerate(self.role_mappings):
                    draw_role_item(self, box, idx, role)
                    
            row = box.row()
            row.operator("project.add_role_mapping", icon='ADD')
            row.operator("project.export_config", icon='EXPORT')
            row.operator("project.import_config", icon='IMPORT')
        
        # Notification settings
        box = layout.box()
        row = box.row()
        row.prop(self, "ui_expanded_notification", text="", icon='TRIA_DOWN' if self.ui_expanded_notification else 'TRIA_RIGHT', emboss=False)
        row.label(text="Notification Settings")
        
        if self.ui_expanded_notification:
            box.prop(self, "username")
            box.prop(self, "discord_webhook_url")
            box.prop(self, "slack_webhook_url")
            box.prop(self, "inactivity_timeout")
            
            webhook_types = []
            if self.discord_webhook_url:
                webhook_types.append(('DISCORD', "Discord", ""))
            if self.slack_webhook_url:
                webhook_types.append(('SLACK', "Slack", ""))
                
            if webhook_types:
                row = box.row()
                row.label(text="Test Webhook:")
                for webhook_type, name, _ in webhook_types:
                    props = row.operator("project.test_webhook", text=name)
                    props.webhook_type = webhook_type
        
        # Recent projects
        box = layout.box()
        row = box.row()
        row.prop(self, "ui_expanded_recent", text="", icon='TRIA_DOWN' if self.ui_expanded_recent else 'TRIA_RIGHT', emboss=False)
        row.label(text="Recent Projects")
        
        if self.ui_expanded_recent:
            box.prop(self, "recent_search", icon='VIEWZOOM')
            box.prop(self, "show_all_recent")
            
            projects_to_show = self.get_filtered_recent_projects()
            
            if not projects_to_show:
                box.label(text="No recent projects")
            else:
                for i, project in enumerate(projects_to_show):
                    if not self.show_all_recent and i >= 3:
                        break
                        
                    row = box.row()
                    row.label(text=project.name)
                    row.label(text=project.path)
                    
                    # Remove project button
                    op = row.operator("project.remove_recent", text="", icon='X')
                    op.index = i
    
    def get_filtered_recent_projects(self):
        """
        Get a filtered list of recent projects based on the search string
        
        Returns:
            list: Filtered list of RecentProject objects
        """
        if not self.recent_search:
            return self.recent_projects
            
        search_lower = self.recent_search.lower()
        return [p for p in self.recent_projects if 
                search_lower in p.name.lower() or 
                search_lower in p.path.lower()]

def draw_role_item(prefs, layout, idx, role):
    """
    Draw UI for a single role item
    
    Args:
        prefs: ProjectPreferences instance
        layout: Layout to draw UI in
        idx: Index of the role
        role: RoleMapping instance
    """
    box = layout.box()
    row = box.row()
    row.prop(role, "expanded", text="", icon='TRIA_DOWN' if role.expanded else 'TRIA_RIGHT', emboss=False)
    row.prop(role, "role_name", text="")
    row.prop(role, "icon", text="")
    
    # Remove button
    op = row.operator("project.remove_role_mapping", text="", icon='X')
    op.index = idx
    
    if role.expanded:
        box.prop(role, "description")
        box.prop(role, "link_type")
        box.prop(role, "collection_color")
        box.prop(role, "show_status")
        box.prop(role, "hide_viewport_default")
        box.prop(role, "exclude_from_view_layer")
        box.prop(role, "owns_world")
        box.prop(role, "skip_assembly")
        
        box.label(text="Publish Settings:")
        box.prop(role, "publish_path_preset")
        if role.publish_path_preset == 'CUSTOM':
            box.prop(role, "custom_publish_path") 