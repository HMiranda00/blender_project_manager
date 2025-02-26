import bpy
import os
import json
from bpy.types import AddonPreferences, PropertyGroup, Operator
from bpy.props import StringProperty, CollectionProperty, EnumProperty, IntProperty, BoolProperty

class RecentProject(PropertyGroup):
    path: StringProperty(name="Project Path")
    name: StringProperty(name="Project Name")
    is_fixed_root: BoolProperty(name="Is Fixed Root")

class RoleMapping(PropertyGroup):
    """Class to store role configurations"""
    role_name: StringProperty(
        name="Role Name",
        description="Role name (e.g., ANIMATION, LOOKDEV)",
    )
    description: StringProperty(
        name="Description",
        description="Brief description of what this role does",
        default="Role description"
    )
    link_type: EnumProperty(
        name="Reference Type",
        description="Defines if the collection will be linked or appended",
        items=[
            ('LINK', "Link", "Collection will be linked (reference)"),
            ('APPEND', "Append", "Collection will be appended (copy)")
        ],
        default='LINK'
    )
    icon: EnumProperty(
        name="Icon",
        description="Icon to represent this role",
        items=[
            ('OUTLINER_OB_ARMATURE', "Animation", "Responsible for character and object animation", 'OUTLINER_OB_ARMATURE', 0),
            ('MATERIAL', "Materials", "Material and texture development", 'MATERIAL', 1),
            ('OUTLINER_OB_MESH', "Models", "Object and character modeling", 'OUTLINER_OB_MESH', 2),
            ('WORLD', "Environment", "Environment setup and global illumination", 'WORLD', 3),
            ('CAMERA_DATA', "Camera", "Camera setup and animation", 'CAMERA_DATA', 4),
            ('LIGHT', "Lights", "Scene lighting", 'LIGHT', 5),
            ('PARTICLE_DATA', "Effects", "Special effects and particles", 'PARTICLE_DATA', 6),
            ('RENDER_RESULT', "Composition", "Final composition and post-production", 'RENDER_RESULT', 7),
            ('TOOL_SETTINGS', "Technical", "Technical settings and optimizations", 'TOOL_SETTINGS', 8),
            ('MODIFIER', "Rigging", "Rig and control development", 'MODIFIER', 9),
            ('UV', "UV/Texture", "UV unwrap and texturing", 'UV', 10),
            ('VIEW3D', "Layout", "Scene layout and blocking", 'VIEW3D', 11),
        ],
        default='TOOL_SETTINGS'
    )
    collection_color: EnumProperty(
        name="Collection Color",
        description="Color to visually identify the collection in the outliner",
        items=[
            ('NONE', "None", "No color", 'OUTLINER_COLLECTION', 0),
            ('COLOR_01', "Red", "Red color", 'COLLECTION_COLOR_01', 1),
            ('COLOR_02', "Orange", "Orange color", 'COLLECTION_COLOR_02', 2),
            ('COLOR_03', "Yellow", "Yellow color", 'COLLECTION_COLOR_03', 3),
            ('COLOR_04', "Green", "Green color", 'COLLECTION_COLOR_04', 4),
            ('COLOR_05', "Blue", "Blue color", 'COLLECTION_COLOR_05', 5),
            ('COLOR_06', "Purple", "Purple color", 'COLLECTION_COLOR_06', 6),
            ('COLOR_07', "Pink", "Pink color", 'COLLECTION_COLOR_07', 7),
            ('COLOR_08', "Brown", "Brown color", 'COLLECTION_COLOR_08', 8),
        ],
        default='NONE'
    )
    hide_viewport_default: BoolProperty(
        name="Hidden by Default",
        description="Defines if the collection should start hidden in viewport",
        default=False
    )
    exclude_from_view_layer: BoolProperty(
        name="Exclude from View Layer",
        description="Defines if the collection should be excluded from view layer by default",
        default=False
    )
    show_status: BoolProperty(
        name="Show Status",
        description="Shows this role's status in the main panel",
        default=True
    )
    owns_world: BoolProperty(
        name="Controls World",
        description="Defines if this role is responsible for the scene's World",
        default=False
    )
    skip_assembly: BoolProperty(
        name="Skip Assembly",
        description="If checked, this role will not be included in the shot's assembly file",
        default=False
    )
    publish_path_preset: EnumProperty(
        name="Publish Folder",
        description="Select the publish path for this role",
        items=[
            ('SHOTS', "SHOTS", "Publish in shots"),
            ('CHARACTERS', "CHARACTERS", "Publish in characters"),
            ('PROPS', "PROPS", "Publish in props"),
            ('CUSTOM', "Custom", "Set custom path"),
        ],
        default='SHOTS'
    )
    custom_publish_path: StringProperty(
        name="Custom Path",
        description="Custom path for this role's publish folder (use placeholders like {root}, {projectCode}, {shot}, {role}, {assetName})",
        default=""
    )
    expanded: BoolProperty(
        name="Expanded",
        default=False,
        description="Expands or collapses this role's settings"
    )

class PROJECTMANAGER_OT_add_role_mapping(Operator):
    """Adds a new role to settings"""
    bl_idname = "project.add_role_mapping"
    bl_label = "Add Role"
    
    def execute(self, context):
        prefs = context.preferences.addons['blender_project_manager'].preferences
        new_role = prefs.role_mappings.add()
        new_role.role_name = "NEW_ROLE"
        new_role.description = "New role description"
        new_role.icon = 'TOOL_SETTINGS'
        return {'FINISHED'}

class PROJECTMANAGER_OT_remove_role_mapping(Operator):
    """Removes a role from settings"""
    bl_idname = "project.remove_role_mapping"
    bl_label = "Remove Role"
    
    index: IntProperty()
    
    def execute(self, context):
        prefs = context.preferences.addons['blender_project_manager'].preferences
        prefs.role_mappings.remove(self.index)
        return {'FINISHED'}

class PROJECTMANAGER_OT_export_config(Operator):
    """Exports settings to a JSON file"""
    bl_idname = "project.export_config"
    bl_label = "Export Settings"
    
    filepath: StringProperty(
        subtype='FILE_PATH',
        default="project_config.json"
    )
    
    filter_glob: StringProperty(
        default='*.json',
        options={'HIDDEN'}
    )
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        prefs = context.preferences.addons['blender_project_manager'].preferences
        
        config = {
            'use_fixed_root': prefs.use_fixed_root,
            'fixed_root_path': prefs.fixed_root_path,
            'roles': []
        }
        
        for role_mapping in prefs.role_mappings:
            role_config = {
                'role_name': role_mapping.role_name,
                'description': role_mapping.description,
                'icon': role_mapping.icon,
                'collection_color': role_mapping.collection_color,
                'hide_viewport_default': role_mapping.hide_viewport_default,
                'exclude_from_view_layer': role_mapping.exclude_from_view_layer,
                'show_status': role_mapping.show_status,
                'owns_world': role_mapping.owns_world,
                'skip_assembly': role_mapping.skip_assembly,
                'publish_path_preset': role_mapping.publish_path_preset,
                'custom_publish_path': role_mapping.custom_publish_path,
                'link_type': role_mapping.link_type,
            }
            config['roles'].append(role_config)
        
        filepath = self.filepath
        if not filepath.lower().endswith('.json'):
            filepath += '.json'
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            self.report({'INFO'}, f"Settings exported to: {filepath}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error exporting settings: {str(e)}")
            return {'CANCELLED'}

class PROJECTMANAGER_OT_import_config(Operator):
    """Imports settings from a JSON file"""
    bl_idname = "project.import_config"
    bl_label = "Import Settings"
    
    filepath: StringProperty(
        subtype='FILE_PATH'
    )
    
    filter_glob: StringProperty(
        default='*.json',
        options={'HIDDEN'}
    )
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        if not os.path.exists(self.filepath):
            self.report({'ERROR'}, "File not found")
            return {'CANCELLED'}
            
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            prefs = context.preferences.addons['blender_project_manager'].preferences
            
            prefs.use_fixed_root = config.get('use_fixed_root', True)
            prefs.fixed_root_path = config.get('fixed_root_path', '')
            
            prefs.role_mappings.clear()
            
            for role_config in config.get('roles', []):
                role_mapping = prefs.role_mappings.add()
                role_mapping.role_name = role_config.get('role_name', '')
                role_mapping.description = role_config.get('description', '')
                role_mapping.icon = role_config.get('icon', 'TOOL_SETTINGS')
                role_mapping.collection_color = role_config.get('collection_color', 'NONE')
                role_mapping.hide_viewport_default = role_config.get('hide_viewport_default', False)
                role_mapping.exclude_from_view_layer = role_config.get('exclude_from_view_layer', False)
                role_mapping.show_status = role_config.get('show_status', True)
                role_mapping.owns_world = role_config.get('owns_world', False)
                role_mapping.skip_assembly = role_config.get('skip_assembly', False)
                role_mapping.publish_path_preset = role_config.get('publish_path_preset', 'SHOTS')
                role_mapping.custom_publish_path = role_config.get('custom_publish_path', '')
                role_mapping.link_type = role_config.get('link_type', 'LINK')
            
            self.report({'INFO'}, "Settings imported successfully!")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error importing settings: {str(e)}")
            return {'CANCELLED'}

class ProjectPreferences(AddonPreferences):
    bl_idname = 'blender_project_manager'

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

    role_mappings: CollectionProperty(
        type=RoleMapping,
        name="Role Settings",
        description="Define roles and their settings",
    )

    recent_projects: CollectionProperty(
        type=RecentProject,
        name="Recent Projects",
        description="List of recent projects"
    )

    show_all_recent: BoolProperty(
        name="Show All Projects",
        default=False,
        description="Show all recent projects or just the 3 most recent ones"
    )
    
    recent_search: StringProperty(
        name="Search Projects",
        default="",
        description="Filter recent projects"
    )

    def draw(self, context):
        layout = self.layout
        
        # Documentation/Help
        help_box = layout.box()
        help_box.label(text="Documentation", icon='HELP')
        help_box.label(text="How the addon works:", icon='INFO')
        col = help_box.column()
        col.label(text="1. Each role defines a main collection with the same name")
        col.label(text="2. Collections are created with the settings defined below")
        col.label(text="3. When creating a new shot, the role's collection is created automatically")
        col.label(text="4. When linking a role, its collection is linked and an override is created")
        
        # Project Root Configuration
        box = layout.box()
        box.label(text="Project Root Configuration", icon='FILE_FOLDER')
        box.prop(self, "use_fixed_root")
        if self.use_fixed_root:
            box.prop(self, "fixed_root_path")
        
        # Import/Export Buttons
        box = layout.box()
        box.label(text="Settings Management", icon='SETTINGS')
        row = box.row()
        row.operator("project.export_config", icon='EXPORT')
        row.operator("project.import_config", icon='IMPORT')
        
        # Role Settings
        box = layout.box()
        box.label(text="Role Settings", icon='COMMUNITY')
        
        # Add new role button
        row = box.row()
        row.operator("project.add_role_mapping", icon='ADD')
        
        # List of existing roles
        for i, role_mapping in enumerate(self.role_mappings):
            role_box = box.box()
            
            # Header with name and remove button
            header = role_box.row()
            header.prop(role_mapping, "expanded", icon='TRIA_DOWN' if role_mapping.expanded else 'TRIA_RIGHT', icon_only=True, emboss=False)
            header.prop(role_mapping, "role_name", text="")
            remove = header.operator("project.remove_role_mapping", icon='X', text="")
            remove.index = i
            
            if role_mapping.expanded:
                # Basic settings
                col = role_box.column()
                col.prop(role_mapping, "description")
                
                # Publish settings
                col.prop(role_mapping, "publish_path_preset")
                if role_mapping.publish_path_preset == 'CUSTOM':
                    col.prop(role_mapping, "custom_publish_path")
                
                # Icon with preview
                icon_row = col.row()
                icon_row.prop(role_mapping, "icon")
                icon_row.label(icon=role_mapping.icon)
                
                # Collection settings
                col_settings = role_box.box()
                col_settings.label(text="Collection Settings:", icon='OUTLINER')
                col_settings.prop(role_mapping, "collection_color")
                col_settings.prop(role_mapping, "hide_viewport_default")
                col_settings.prop(role_mapping, "exclude_from_view_layer")

                # Link settings
                link_settings = role_box.box()
                link_settings.label(text="Link Settings:", icon='LINKED')
                link_settings.prop(role_mapping, "link_type")

                # Special settings
                special_settings = role_box.box()
                special_settings.label(text="Special Settings:", icon='SETTINGS')
                special_settings.prop(role_mapping, "show_status")
                special_settings.prop(role_mapping, "owns_world")
                special_settings.prop(role_mapping, "skip_assembly")

# Lista de classes para registro
classes = (
    RoleMapping,
    PROJECTMANAGER_OT_add_role_mapping,
    PROJECTMANAGER_OT_remove_role_mapping,
    PROJECTMANAGER_OT_export_config,
    PROJECTMANAGER_OT_import_config,
    ProjectPreferences,
)

def register():
    # Registrar RecentProject primeiro
    if not hasattr(bpy.types, 'RecentProject'):
        bpy.utils.register_class(RecentProject)
    
    # Registrar outras classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add default roles
    prefs = bpy.context.preferences.addons['blender_project_manager'].preferences
    
    # Only add if there are no roles yet
    if len(prefs.role_mappings) == 0:
        # Animation Role
        role = prefs.role_mappings.add()
        role.role_name = "ANIMATION"
        role.description = "Animation and character performance"
        role.icon = "OUTLINER_OB_ARMATURE"
        role.collection_color = "COLOR_02"
        role.hide_viewport_default = False
        role.exclude_from_view_layer = False
        role.show_status = True
        role.owns_world = False
        role.skip_assembly = False
        role.publish_path_preset = "SHOTS"
        role.custom_publish_path = ""
        role.link_type = "LINK"
        
        # Lookdev Role
        role = prefs.role_mappings.add()
        role.role_name = "LOOKDEV"
        role.description = "Materials, lighting and rendering"
        role.icon = "LIGHT"
        role.collection_color = "COLOR_03"
        role.hide_viewport_default = False
        role.exclude_from_view_layer = False
        role.show_status = True
        role.owns_world = True
        role.skip_assembly = False
        role.publish_path_preset = "SHOTS"
        role.custom_publish_path = ""
        role.link_type = "LINK"
        
        # Layout Role
        role = prefs.role_mappings.add()
        role.role_name = "LAYOUT"
        role.description = "Scene layout and camera"
        role.icon = "TOOL_SETTINGS"
        role.collection_color = "NONE"
        role.hide_viewport_default = False
        role.exclude_from_view_layer = False
        role.show_status = True
        role.owns_world = False
        role.skip_assembly = True
        role.publish_path_preset = "SHOTS"
        role.custom_publish_path = ""
        role.link_type = "APPEND"

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)