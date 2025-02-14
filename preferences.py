import bpy
import os
import json
from bpy.types import AddonPreferences, PropertyGroup, Operator, UIList
from bpy.props import StringProperty, CollectionProperty, EnumProperty, IntProperty, BoolProperty
from .i18n.translations import translate as i18n_translate

# Definições estáticas para os itens de enum
ICON_ITEMS = [
    ('NONE', "None", "", 'NONE', 0),
    ('OUTLINER_OB_ARMATURE', "Animation", "", 'OUTLINER_OB_ARMATURE', 1),
    ('LIGHT', "Light", "", 'LIGHT', 2),
    ('VIEW3D', "Layout", "", 'VIEW3D', 3),
    ('COMMUNITY', "Assembly", "", 'COMMUNITY', 4),
    ('MATERIAL', "Material", "", 'MATERIAL', 5),
    ('MOD_CLOTH', "Cloth", "", 'MOD_CLOTH', 6),
    ('OBJECT_DATAMODE', "Object", "", 'OBJECT_DATAMODE', 7),
    ('PARTICLES', "Particles", "", 'PARTICLES', 8),
    ('PHYSICS', "Physics", "", 'PHYSICS', 9),
    ('RENDER_RESULT', "Render", "", 'RENDER_RESULT', 10),
    ('SCENE_DATA', "Scene", "", 'SCENE_DATA', 11),
    ('SHADING_RENDERED', "Shading", "", 'SHADING_RENDERED', 12),
    ('TEXTURE', "Texture", "", 'TEXTURE', 13),
    ('WORLD', "World", "", 'WORLD', 14)
]

COLOR_ITEMS = [
    ('NONE', "None", "", 'OUTLINER_COLLECTION', 0),
    ('COLOR_01', "Red", "", 'COLLECTION_COLOR_01', 1),
    ('COLOR_02', "Orange", "", 'COLLECTION_COLOR_02', 2),
    ('COLOR_03', "Yellow", "", 'COLLECTION_COLOR_03', 3),
    ('COLOR_04', "Green", "", 'COLLECTION_COLOR_04', 4),
    ('COLOR_05', "Blue", "", 'COLLECTION_COLOR_05', 5),
    ('COLOR_06', "Purple", "", 'COLLECTION_COLOR_06', 6),
    ('COLOR_07', "Pink", "", 'COLLECTION_COLOR_07', 7),
    ('COLOR_08', "Brown", "", 'COLLECTION_COLOR_08', 8)
]

LANGUAGE_ITEMS = [
    ('en_US', "English", "", 0),
    ('pt_BR', "Português (Brasil)", "", 1)
]

def load_default_roles(prefs):
    """Load default role mappings"""
    # Clear existing roles
    prefs.role_mappings.clear()
    
    # Animation role
    anim = prefs.role_mappings.add()
    anim.role_name = "ANIMATION"
    anim.description = i18n_translate("Character and object animation")
    anim.icon = 'OUTLINER_OB_ARMATURE'
    anim.collection_color = 'COLOR_02'
    anim.link_type = 'LINK'
    anim.publish_path_preset = 'SHOTS'
    anim.show_status = True
    
    # Lightning role
    light = prefs.role_mappings.add()
    light.role_name = "LIGHTNING"
    light.description = i18n_translate("Scene lighting and rendering")
    light.icon = 'LIGHT'
    light.collection_color = 'COLOR_03'
    light.link_type = 'LINK'
    light.publish_path_preset = 'SHOTS'
    light.owns_world = True
    light.show_status = True
    
    # Layout role
    layout = prefs.role_mappings.add()
    layout.role_name = "LAYOUT"
    layout.description = i18n_translate("Scene layout and camera")
    layout.icon = 'VIEW3D'
    layout.collection_color = 'COLOR_04'
    layout.link_type = 'LINK'
    layout.publish_path_preset = 'SHOTS'
    layout.show_status = True

def get_language_items(self, context):
    """Get available languages for enum property"""
    return LANGUAGE_ITEMS

class RecentProject(PropertyGroup):
    """Armazena informações de projetos recentes"""
    path: StringProperty(
        name="Project Path",
        description="Caminho completo do projeto",
        default=""
    )
    name: StringProperty(
        name="Project Name",
        description="Nome do projeto",
        default=""
    )

class RoleMapping(PropertyGroup):
    """Classe para armazenar as configurações de cada cargo"""
    role_name: StringProperty(
        name=i18n_translate("Name"),
        description=i18n_translate("Role name"),
        default=""
    )
    description: StringProperty(
        name=i18n_translate("Description"),
        description=i18n_translate("Role description"),
        default=""
    )
    link_type: EnumProperty(
        name=i18n_translate("Link Type"),
        description=i18n_translate("How to link this role"),
        items=[
            ('LINK', i18n_translate("Link"), ""),
            ('APPEND', i18n_translate("Append"), "")
        ],
        default='LINK'
    )
    icon: EnumProperty(
        name=i18n_translate("Icon"),
        description=i18n_translate("Role icon"),
        items=ICON_ITEMS,
        default='NONE'
    )
    collection_color: EnumProperty(
        name=i18n_translate("Color"),
        description=i18n_translate("Collection color"),
        items=COLOR_ITEMS,
        default='NONE'
    )
    hide_viewport_default: BoolProperty(
        name=i18n_translate("Hide Viewport"),
        description=i18n_translate("Hide in viewport by default"),
        default=False
    )
    exclude_from_view_layer: BoolProperty(
        name=i18n_translate("Exclude from View Layer"),
        description=i18n_translate("Exclude from view layer"),
        default=False
    )
    show_status: BoolProperty(
        name=i18n_translate("Show Status"),
        description=i18n_translate("Show role status"),
        default=True
    )
    owns_world: BoolProperty(
        name=i18n_translate("Owns World"),
        description=i18n_translate("Role owns world data"),
        default=False
    )
    skip_assembly: BoolProperty(
        name=i18n_translate("Skip Assembly"),
        description=i18n_translate("Skip role in assembly"),
        default=False
    )
    publish_path_preset: EnumProperty(
        name=i18n_translate("Publish Path"),
        description=i18n_translate("Publish path preset"),
        items=[
            ('SHOTS', i18n_translate("Shots"), ""),
            ('ASSETS', i18n_translate("Assets"), "")
        ],
        default='SHOTS'
    )
    custom_publish_path: StringProperty(
        name="Caminho Personalizado",
        description="Caminho personalizado para a pasta de publicação deste cargo (use placeholders como {root}, {projectCode}, {shot}, {role}, {assetName})",
        default=""
    )
    expanded: BoolProperty(
        name="Expandido",
        default=False,
        description="Expande ou colapsa as configurações deste cargo"
    )

class PROJECTMANAGER_UL_roles(UIList):
    """Role list UI"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.role_name == "ASSEMBLY":
                layout.label(text=item.role_name, icon=item.icon if item.icon != 'NONE' else 'COMMUNITY')
            else:
                layout.prop(item, "role_name", text="", emboss=False, icon=item.icon if item.icon != 'NONE' else 'NONE')

class PROJECTMANAGER_UL_recent_projects(UIList):
    """Recent projects list UI"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Mostrar nome do projeto se disponível, senão mostrar o nome da pasta
            project_name = item.name if item.name else os.path.basename(os.path.dirname(item.path))
            layout.label(text=project_name, icon='FILE_BLEND')
            op = layout.operator("project.open_recent", text="", icon='FILEBROWSER', emboss=False)
            op.selected_project = item.path

class PROJECTMANAGER_OT_add_role_mapping(Operator):
    """Adiciona um novo cargo"""
    bl_idname = "project.add_role_mapping"
    bl_label = "Adicionar Cargo"
    
    def execute(self, context):
        prefs = context.preferences.addons['blender_project_manager'].preferences
        new_role = prefs.role_mappings.add()
        
        # Se não houver cargo Assembly, criar como primeiro
        has_assembly = False
        for role in prefs.role_mappings:
            if role.role_name.upper() == "ASSEMBLY":
                has_assembly = True
                break
                
        if not has_assembly and len(prefs.role_mappings) == 1:
            new_role.role_name = "ASSEMBLY"
            new_role.description = "Montagem final do projeto"
            new_role.icon = 'COMMUNITY'
        
        return {'FINISHED'}

class PROJECTMANAGER_OT_remove_role_mapping(Operator):
    """Remove um cargo das configurações"""
    bl_idname = "project.remove_role_mapping"
    bl_label = "Remover Cargo"
    
    index: IntProperty()
    
    def execute(self, context):
        prefs = context.preferences.addons['blender_project_manager'].preferences
        prefs.role_mappings.remove(self.index)
        return {'FINISHED'}

class PROJECTMANAGER_OT_export_config(Operator):
    """Exporta as configurações para um arquivo JSON"""
    bl_idname = "project.export_config"
    bl_label = "Exportar Configurações"
    
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
            self.report({'INFO'}, f"Configurações exportadas para: {filepath}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao exportar configurações: {str(e)}")
            return {'CANCELLED'}

class PROJECTMANAGER_OT_import_config(Operator):
    """Importa as configurações de um arquivo JSON"""
    bl_idname = "project.import_config"
    bl_label = "Importar Configurações"
    
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
            self.report({'ERROR'}, "Arquivo não encontrado")
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
                role_mapping.icon = role_config.get('icon', 'NONE')
                role_mapping.collection_color = role_config.get('collection_color', 'NONE')
                role_mapping.hide_viewport_default = role_config.get('hide_viewport_default', False)
                role_mapping.exclude_from_view_layer = role_config.get('exclude_from_view_layer', False)
                role_mapping.show_status = role_config.get('show_status', True)
                role_mapping.owns_world = role_config.get('owns_world', False)
                role_mapping.skip_assembly = role_config.get('skip_assembly', False)
                role_mapping.publish_path_preset = role_config.get('publish_path_preset', 'SHOTS')
                role_mapping.custom_publish_path = role_config.get('custom_publish_path', '')
                role_mapping.link_type = role_config.get('link_type', 'LINK')
            
            self.report({'INFO'}, "Configurações importadas com sucesso!")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Erro ao importar configurações: {str(e)}")
            return {'CANCELLED'}

class ProjectPreferences(AddonPreferences):
    bl_idname = __package__

    use_fixed_root: BoolProperty(
        name=i18n_translate("Use Fixed Root"),
        description=i18n_translate("If checked, will use a fixed root folder for all projects"),
        default=False
    )

    fixed_root_path: StringProperty(
        name=i18n_translate("Fixed Root Path"),
        subtype='DIR_PATH',
        default="",
        description=i18n_translate("Path to fixed root folder")
    )

    role_mappings: CollectionProperty(
        type=RoleMapping,
        name=i18n_translate("Role Settings"),
        description=i18n_translate("Define roles and their settings"),
    )

    active_role_index: IntProperty(
        name="Active Role Index",
        default=0
    )

    recent_projects: CollectionProperty(
        type=RecentProject,
        name=i18n_translate("Recent Projects"),
        description=i18n_translate("List of recent projects")
    )

    show_all_recent: BoolProperty(
        name=i18n_translate("Show All"),
        default=False,
        description=i18n_translate("Show all recent projects")
    )
    
    recent_search: StringProperty(
        name=i18n_translate("Search Projects"),
        default="",
        description=i18n_translate("Filter recent projects")
    )

    # Language selection
    language: EnumProperty(
        name=i18n_translate("Language"),
        description=i18n_translate("Interface language"),
        items=get_language_items,
        default=0  # Index for 'en_US'
    )

    active_recent_index: IntProperty(
        name="Active Recent Project Index",
        default=0
    )

    def draw(self, context):
        layout = self.layout
        
        # Documentation/Help
        help_box = layout.box()
        help_box.label(text=i18n_translate("Documentation"), icon='HELP')
        help_box.label(text=i18n_translate("How the addon works:"), icon='INFO')
        col = help_box.column()
        col.label(text=i18n_translate("1. Each role defines a main collection with the same name"))
        col.label(text=i18n_translate("2. Collections are created with settings defined below"))
        col.label(text=i18n_translate("3. When creating a new shot, the role collection is created automatically"))
        col.label(text=i18n_translate("4. When linking a role, its collection is linked and an override is created"))
        
        # Project Root Configuration
        box = layout.box()
        box.label(text=i18n_translate("Project Root Configuration"), icon='FILE_FOLDER')
        box.prop(self, "use_fixed_root")
        if self.use_fixed_root:
            box.prop(self, "fixed_root_path")
        
        # Recent Projects
        box = layout.box()
        box.label(text=i18n_translate("Recent Projects"), icon='RECOVER_LAST')
        
        # Recent projects list and management
        row = box.row()
        
        # Left side: Recent projects list
        col = row.column()
        col.template_list(
            "PROJECTMANAGER_UL_recent_projects", "recent_projects_list",
            self, "recent_projects",
            self, "active_recent_index",
            rows=3
        )
        
        # Right side: List management buttons
        col = row.column(align=True)
        col.operator("project.clear_recent", icon='TRASH', text="")
        
        # Search field
        box.prop(self, "recent_search", icon='VIEWZOOM', text="")
        
        # Import/Export Buttons
        box = layout.box()
        box.label(text=i18n_translate("Settings Management"), icon='SETTINGS')
        row = box.row()
        row.operator("project.export_config", icon='EXPORT')
        row.operator("project.import_config", icon='IMPORT')
        
        # Role Settings
        box = layout.box()
        box.label(text=i18n_translate("Role Settings"), icon='COMMUNITY')
        
        # Role list and management
        row = box.row()
        
        # Left side: Role list
        col = row.column()
        col.template_list(
            "PROJECTMANAGER_UL_roles", "role_list",
            self, "role_mappings",
            self, "active_role_index",
            rows=4
        )
        
        # Right side: List management buttons
        col = row.column(align=True)
        col.operator("project.add_role_mapping", icon='ADD', text="")
        col.operator("project.remove_role_mapping", icon='REMOVE', text="").index = self.active_role_index
        col.separator()
        col.operator("project.move_default_role", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("project.move_default_role", icon='TRIA_DOWN', text="").direction = 'DOWN'
        
        # Role settings (only show if a role is selected and it's not ASSEMBLY)
        if len(self.role_mappings) > self.active_role_index >= 0:
            role = self.role_mappings[self.active_role_index]
            if role.role_name != "ASSEMBLY":
                settings_box = box.box()
                settings_box.label(text=i18n_translate("Role Settings:"), icon='PREFERENCES')
                
                # Basic settings
                col = settings_box.column()
                col.prop(role, "description")
                
                # Publish settings
                col.prop(role, "publish_path_preset")
                if role.publish_path_preset == 'CUSTOM':
                    col.prop(role, "custom_publish_path")
                
                # Icon with preview
                icon_row = col.row()
                icon_row.prop(role, "icon")
                icon_row.label(icon=role.icon)
                
                # Collection settings
                col_settings = settings_box.box()
                col_settings.label(text=i18n_translate("Collection Settings:"), icon='OUTLINER')
                col_settings.prop(role, "collection_color")
                col_settings.prop(role, "hide_viewport_default")
                col_settings.prop(role, "exclude_from_view_layer")

                # Link settings
                link_settings = settings_box.box()
                link_settings.label(text=i18n_translate("Link Settings:"), icon='LINKED')
                link_settings.prop(role, "link_type")

                # Special settings
                special_settings = settings_box.box()
                special_settings.label(text=i18n_translate("Special Settings:"), icon='SETTINGS')
                row = special_settings.row()
                row.prop(role, "owns_world", icon='WORLD')
                row.prop(role, "show_status", icon='INFO')
                row.prop(role, "skip_assembly", icon='FILE_BLEND')

        # Language selection
        box = layout.box()
        box.label(text=i18n_translate("Interface Settings"))
        box.prop(self, "language")

# Lista de classes para registro
classes = (
    RecentProject,
    RoleMapping,
    PROJECTMANAGER_UL_roles,
    PROJECTMANAGER_UL_recent_projects,
    PROJECTMANAGER_OT_add_role_mapping,
    PROJECTMANAGER_OT_remove_role_mapping,
    PROJECTMANAGER_OT_export_config,
    PROJECTMANAGER_OT_import_config,
    ProjectPreferences,
)

def register():
    """Register preferences"""
    try:
        # Register classes
        for cls in classes:
            bpy.utils.register_class(cls)
            
        # Load default roles if none exist
        prefs = bpy.context.preferences.addons[__package__].preferences
        if len(prefs.role_mappings) == 0:
            load_default_roles(prefs)
            
    except Exception as e:
        print(f"Error registering preferences: {str(e)}")
        raise

def unregister():
    """Unregister preferences"""
    try:
        # Unregister classes
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)
            
    except Exception as e:
        print(f"Error unregistering preferences: {str(e)}")
        raise

def get_prefs(context):
    """Retorna as preferências do addon"""
    return context.preferences.addons['blender_project_manager'].preferences

def update_role_mapping(self, context):
    """Atualiza o mapeamento de cargos"""
    prefs = context.preferences.addons['blender_project_manager'].preferences
    
    # ... existing code ...

def update_role_mapping_list(self, context):
    """Atualiza a lista de mapeamentos de cargos"""
    prefs = context.preferences.addons['blender_project_manager'].preferences
    
    # ... existing code ...

def update_recent_projects(self, context):
    """Atualiza a lista de projetos recentes"""
    prefs = context.preferences.addons['blender_project_manager'].preferences
