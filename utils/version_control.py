import logging
import os
import shutil

import bpy

from .addon import get_addon_preferences
from .core import get_project_info, get_publish_path
from .pipeline_rules import build_publish_filename, build_wip_filename, build_wip_prefix, select_latest_wip

logger = logging.getLogger(__name__)


def get_wip_path(context, role_name, create=False):
    """Get the WIP path for the current role/shot."""
    try:
        if not (context.scene.current_project and context.scene.current_shot):
            return None

        project_path = context.scene.current_project
        prefs = get_addon_preferences(context)
        _, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot

        wip_path = os.path.join(workspace_path, "SHOTS", shot_name, role_name, "WIP")
        if create:
            os.makedirs(wip_path, exist_ok=True)
        elif not os.path.exists(wip_path):
            return None
        return wip_path

    except Exception as exc:
        logger.error("Error getting WIP path for role %s: %s", role_name, exc)
        return None


def get_latest_wip(context, role_name):
    """Get the latest WIP version for the current role."""
    try:
        wip_path = get_wip_path(context, role_name, create=False)
        if not wip_path:
            return None, 0

        project_path = context.scene.current_project
        prefs = get_addon_preferences(context)
        _, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot

        wip_prefix = build_wip_prefix(project_prefix, shot_name, role_name)
        latest_name, latest_version = select_latest_wip(os.listdir(wip_path), wip_prefix)
        if not latest_name:
            return None, 0

        return os.path.join(wip_path, latest_name), latest_version

    except Exception as exc:
        logger.error("Error getting latest WIP for role %s: %s", role_name, exc)
        return None, 0


def create_first_wip(context, role_name):
    """Create the first WIP version and publish file."""
    try:
        if not (context.scene.current_project and context.scene.current_shot):
            return None

        project_path = context.scene.current_project
        prefs = get_addon_preferences(context)
        project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot

        wip_path = get_wip_path(context, role_name, create=True)
        if not wip_path:
            return None

        wip_file = os.path.join(wip_path, build_wip_filename(project_prefix, shot_name, role_name, 1))
        bpy.ops.wm.save_as_mainfile(filepath=wip_file)

        role_settings = next((rm for rm in prefs.role_mappings if rm.role_name == role_name), None)
        if not role_settings:
            return None

        publish_path = get_publish_path(
            role_settings.publish_path_preset,
            role_settings,
            context,
            project_path,
            project_name,
            shot_name,
            asset_name=role_name,
        )

        os.makedirs(publish_path, exist_ok=True)
        publish_file = os.path.join(publish_path, build_publish_filename(project_prefix, shot_name, role_name))
        shutil.copy2(wip_file, publish_file)
        return wip_file

    except Exception as exc:
        logger.error("Error creating first WIP for role %s: %s", role_name, exc)
        return None

