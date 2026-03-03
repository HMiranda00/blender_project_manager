import os
import bpy
import re
from .addon import get_addon_preferences
from .pipeline_rules import resolve_publish_template

def get_project_info(path, is_fixed_root=False):
    """Extract project info from a path"""
    project_folder = os.path.basename(path.rstrip(os.path.sep))
    
    # Extrair o número do projeto (ex: 001, 002, etc)
    project_prefix = ""
    if is_fixed_root:
        prefix_match = re.match(r'^(\d+)\s*-\s*', project_folder)
        if prefix_match:
            project_prefix = prefix_match.group(1)
            # No modo raiz fixa, sempre usar "03 - 3D"
            workspace_folder = "03 - 3D"
            workspace_path = os.path.join(path, workspace_folder)
    else:
        prefix_match = re.match(r'^([A-Z]+\d+)', project_folder)
        project_prefix = prefix_match.group(1) if prefix_match else ""
        workspace_path = os.path.join(path, "3D")
    
    return project_folder, workspace_path, project_prefix

def get_next_project_number(root_path):
    """Get the next available project number in fixed root mode"""
    try:
        project_numbers = []
        for folder in os.listdir(root_path):
            if os.path.isdir(os.path.join(root_path, folder)):
                match = re.match(r'^(\d+)\s*-\s*', folder)
                if match:
                    project_numbers.append(int(match.group(1)))
        return max(project_numbers, default=0) + 1
    except Exception:
        return 1

def get_publish_path(preset, role_settings, context, project_path, project_name, shot_name, asset_name):
    """Get the publish path based on settings"""
    prefs = get_addon_preferences(context)
    _, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
    
    placeholders = {
        'root': workspace_path,
        'projectCode': project_name,
        'shot': shot_name,
        'role': role_settings.role_name,
        'assetName': asset_name
    }
    
    return resolve_publish_template(
        preset,
        role_settings.custom_publish_path,
        placeholders
    )

def save_current_file():
    """Save current file if it exists"""
    if bpy.data.is_saved:
        bpy.ops.wm.save_mainfile()

def create_project_structure(workspace_path):
    """Create standard project folder structure"""
    os.makedirs(os.path.join(workspace_path, 'SHOTS'), exist_ok=True)
    os.makedirs(os.path.join(workspace_path, 'ASSETS 3D', 'PROPS'), exist_ok=True)
    os.makedirs(os.path.join(workspace_path, 'ASSETS 3D', 'CHR'), exist_ok=True)
    os.makedirs(os.path.join(workspace_path, 'ASSETS 3D', 'ENV'), exist_ok=True)

def setup_collection_settings(collection, role_settings):
    """Setup collection color and other settings"""
    if collection:
        # Definir cor da collection
        if role_settings.collection_color != 'NONE':
            collection.color_tag = role_settings.collection_color
            
        # Configurar visibilidade
        viewlayer = bpy.context.view_layer
        layer_collection = viewlayer.layer_collection.children.get(collection.name)
        if layer_collection:
            layer_collection.hide_viewport = role_settings.hide_viewport_default
            layer_collection.exclude = role_settings.exclude_from_view_layer

def setup_role_world(role_settings):
    """Setup world if role owns it"""
    if role_settings.owns_world:
        for scene in bpy.data.scenes:
            if not scene.world:
                scene.world = bpy.data.worlds.new(name=f"{role_settings.role_name}_World")

def is_compositor_control_supported():
    """Compositor role ownership is supported from Blender 5.0+."""
    return bpy.app.version >= (5, 0, 0) and hasattr(bpy.types.Scene, "compositing_node_group")

def setup_role_compositor(role_settings):
    """Create/assign role compositor group for current scene when supported."""
    if not role_settings.owns_compositor or not is_compositor_control_supported():
        return None

    scene = bpy.context.scene
    group_name = f"{role_settings.role_name}_COMPOSITOR"
    node_group = bpy.data.node_groups.get(group_name)
    if node_group is None or node_group.bl_idname != "CompositorNodeTree":
        node_group = bpy.data.node_groups.new(group_name, "CompositorNodeTree")

    scene.compositing_node_group = node_group
    # Backward-compat flag still present in 5.x.
    if hasattr(scene, "use_nodes"):
        scene.use_nodes = True

    return node_group

def apply_role_compositor_from_publish(scene, blend_path, role_settings, link=True):
    """Load and assign compositor node group from a role publish file."""
    if not role_settings.owns_compositor or not is_compositor_control_supported():
        return False

    if not os.path.exists(blend_path):
        return False

    target_group_name = f"{role_settings.role_name}_COMPOSITOR"
    loaded_groups = []
    with bpy.data.libraries.load(blend_path, link=link) as (data_from, data_to):
        candidate = None
        if target_group_name in data_from.node_groups:
            candidate = target_group_name
        elif data_from.node_groups:
            # Fallback for legacy files that have unnamed/default compositor group.
            candidate = data_from.node_groups[0]

        if candidate:
            data_to.node_groups = [candidate]
            loaded_groups = data_to.node_groups

    if not loaded_groups or loaded_groups[0] is None:
        return False

    scene.compositing_node_group = loaded_groups[0]
    if hasattr(scene, "use_nodes"):
        scene.use_nodes = True
    return True

def force_ui_update():
    """Force UI update in all areas"""
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw() 

