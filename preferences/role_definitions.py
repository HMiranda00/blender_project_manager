"""
Role definitions for Blender Project Manager.
Contains classes for role configuration and management.
"""

import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import StringProperty, EnumProperty, IntProperty, BoolProperty

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
        description="If the role's panel is expanded in the preferences",
        default=False
    )

class PROJECTMANAGER_OT_add_role_mapping(Operator):
    """Adds a new role to settings"""
    bl_idname = "project.add_role_mapping"
    bl_label = "Add Role"
    
    def execute(self, context):
        from .preference_utils import get_addon_preferences
        
        prefs = get_addon_preferences(context)
        role = prefs.role_mappings.add()
        role.role_name = f"ROLE_{len(prefs.role_mappings)}"
        return {'FINISHED'}

class PROJECTMANAGER_OT_remove_role_mapping(Operator):
    """Removes a role from settings"""
    bl_idname = "project.remove_role_mapping"
    bl_label = "Remove Role"
    
    index: IntProperty()
    
    def execute(self, context):
        from .preference_utils import get_addon_preferences
        
        prefs = get_addon_preferences(context)
        prefs.role_mappings.remove(self.index)
        return {'FINISHED'} 