import logging
import os
import shutil

import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator

from ..utils import get_addon_preferences, get_project_info, get_publish_path, save_current_file
from ..utils.cache import DirectoryCache
from ..utils.pipeline_rules import (
    build_publish_filename,
    build_wip_filename,
    build_wip_prefix,
    extract_wip_version,
)
from ..utils.version_control import get_latest_wip as util_get_latest_wip
from ..utils.version_control import get_wip_path as util_get_wip_path

logger = logging.getLogger(__name__)


def get_wip_path(context, role_name, create=False):
    """Compatibility wrapper: canonical implementation lives in utils.version_control."""
    return util_get_wip_path(context, role_name, create=create)


def get_latest_wip(context, role_name):
    """Compatibility wrapper: canonical implementation lives in utils.version_control."""
    return util_get_latest_wip(context, role_name)


def create_or_update_publish(context, role_name):
    """Create or update publish by copying latest WIP."""
    try:
        if not (context.scene.current_project and context.scene.current_shot):
            logger.warning("Cannot publish without current project and shot")
            return None

        latest_wip, _ = get_latest_wip(context, role_name)
        if not latest_wip:
            logger.warning("No WIP file found for role %s", role_name)
            return None

        project_path = context.scene.current_project
        prefs = get_addon_preferences(context)
        project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot

        role_settings = next((rm for rm in prefs.role_mappings if rm.role_name == role_name), None)
        if not role_settings:
            logger.warning("Role settings not found for role %s", role_name)
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
        shutil.copy2(latest_wip, publish_file)
        return publish_file

    except Exception as exc:
        logger.error("Error creating/updating publish for role %s: %s", role_name, exc)
        return None


class VERSION_OT_new_wip_version(Operator):
    """Create a new WIP version."""

    bl_idname = "project.new_wip_version"
    bl_label = "New WIP Version"
    bl_description = "Create a new WIP version of the current file"

    role_name: StringProperty()
    update_publish: BoolProperty(
        name="Update Publish",
        description="Update the publish file with this version",
        default=True,
    )

    def execute(self, context):
        try:
            if not (context.scene.current_project and context.scene.current_shot and context.scene.current_role):
                self.report({"ERROR"}, "No project, shot or role selected")
                return {"CANCELLED"}

            role_name = context.scene.current_role
            wip_path = get_wip_path(context, role_name, create=True)
            if not wip_path:
                self.report({"ERROR"}, "Could not get WIP path")
                return {"CANCELLED"}

            project_path = context.scene.current_project
            prefs = get_addon_preferences(context)
            _, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            shot_name = context.scene.current_shot

            _, latest_version = get_latest_wip(context, role_name)
            new_version = latest_version + 1
            new_file = os.path.join(
                wip_path,
                build_wip_filename(project_prefix, shot_name, role_name, new_version),
            )

            bpy.ops.wm.save_as_mainfile(filepath=new_file)

            publish_file = create_or_update_publish(context, role_name)
            if self.update_publish and not publish_file:
                self.report({"WARNING"}, "Could not update publish file")

            self.report({"INFO"}, f"Created WIP version {new_version}")
            return {"FINISHED"}

        except Exception as exc:
            self.report({"ERROR"}, f"Error creating new version: {exc}")
            return {"CANCELLED"}


class VERSION_OT_open_latest_wip(Operator):
    """Open the latest WIP version."""

    bl_idname = "project.open_latest_wip"
    bl_label = "Open Latest WIP"
    bl_description = "Open the latest WIP version of the current role"

    role_name: StringProperty(
        name="Role Name",
        description="Name of the role to open latest WIP for (internal use only)",
        options={"HIDDEN"},
    )

    def execute(self, context):
        try:
            if not (context.scene.current_project and context.scene.current_shot):
                self.report({"ERROR"}, "No project or shot selected")
                return {"CANCELLED"}

            role_name = self.role_name if self.role_name else context.scene.current_role
            if not role_name:
                self.report({"ERROR"}, "No role selected")
                return {"CANCELLED"}

            current_project = context.scene.current_project
            current_shot = context.scene.current_shot
            context.scene.current_role = role_name

            latest_wip, version = get_latest_wip(context, role_name)
            if not latest_wip:
                wip_path = get_wip_path(context, role_name, create=True)
                if not wip_path:
                    self.report({"ERROR"}, "Could not get WIP path")
                    return {"CANCELLED"}

                project_path = context.scene.current_project
                prefs = get_addon_preferences(context)
                _, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
                shot_name = context.scene.current_shot

                latest_wip = os.path.join(
                    wip_path,
                    build_wip_filename(project_prefix, shot_name, role_name, 1),
                )

                save_current_file()
                bpy.ops.wm.save_as_mainfile(filepath=latest_wip)

                publish_file = create_or_update_publish(context, role_name)
                if not publish_file:
                    self.report({"WARNING"}, "Could not create publish file")

                self.report({"INFO"}, "Created first WIP version")
            else:
                save_current_file()
                bpy.ops.wm.open_mainfile(filepath=latest_wip)
                self.report({"INFO"}, f"Opened WIP version {version}")

            context.scene.current_project = current_project
            context.scene.current_shot = current_shot
            context.scene.current_role = role_name

            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()

            return {"FINISHED"}

        except Exception as exc:
            self.report({"ERROR"}, f"Error opening latest WIP: {exc}")
            return {"CANCELLED"}


class VERSION_OT_publish(Operator):
    bl_idname = "project.publish_version"
    bl_label = "Publish Version"
    bl_description = "Create a publish version from the current WIP"

    def execute(self, context):
        try:
            if not (context.scene.current_project and context.scene.current_shot and context.scene.current_role):
                self.report({"ERROR"}, "No project, shot or role selected")
                return {"CANCELLED"}

            role_name = context.scene.current_role
            project_path = context.scene.current_project
            prefs = get_addon_preferences(context)
            _, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
            shot_name = context.scene.current_shot

            if bpy.data.is_saved:
                current_file = os.path.basename(bpy.data.filepath)
                expected_prefix = f"{project_prefix}_{shot_name}_{role_name}"
                if not current_file.startswith(expected_prefix):
                    self.report({"WARNING"}, f"Current file does not match role {role_name}. Publishing anyway.")

            save_current_file()
            publish_file = create_or_update_publish(context, role_name)
            if not publish_file:
                self.report({"ERROR"}, "Could not create publish file")
                return {"CANCELLED"}

            self.report({"INFO"}, f"Published file created: {os.path.basename(publish_file)}")
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()

            return {"FINISHED"}

        except Exception as exc:
            self.report({"ERROR"}, f"Error publishing version: {exc}")
            return {"CANCELLED"}


class VERSION_OT_open_version_list(Operator):
    """Select and open a version from list."""

    bl_idname = "project.open_version_list"
    bl_label = "Select Version"
    bl_description = "Open a specific version from the list"
    bl_property = "version_enum"

    file_paths = {}

    def get_version_list(self, context):
        VERSION_OT_open_version_list.file_paths.clear()
        items = []

        if not (context.scene.current_project and context.scene.current_shot and context.scene.current_role):
            return [("NONE", "No versions available", "")]

        role_name = context.scene.current_role
        project_path = context.scene.current_project
        prefs = get_addon_preferences(context)
        project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)
        shot_name = context.scene.current_shot

        wip_path = get_wip_path(context, role_name, create=False)
        if not wip_path or not os.path.exists(wip_path):
            return [("NONE", "No versions available", "")]

        items.append(("LATEST", "Latest WIP", "Open the latest WIP version"))

        role_mapping = next((rm for rm in prefs.role_mappings if rm.role_name == role_name), None)
        if role_mapping:
            publish_path = get_publish_path(
                role_mapping.publish_path_preset,
                role_mapping,
                context,
                project_path,
                project_name,
                shot_name,
                asset_name=role_name,
            )
            publish_file = os.path.join(publish_path, build_publish_filename(project_prefix, shot_name, role_name))
            if os.path.exists(publish_file):
                VERSION_OT_open_version_list.file_paths["PUBLISHED"] = publish_file
                items.append(("PUBLISHED", "Published Version", "Open the published version"))

        try:
            wip_prefix = build_wip_prefix(project_prefix, shot_name, role_name)
            wip_files = []
            for filename in os.listdir(wip_path):
                version_num = extract_wip_version(filename, wip_prefix)
                if version_num is None:
                    continue
                filepath = os.path.join(wip_path, filename)
                wip_files.append((version_num, filepath, filename))

            wip_files.sort(reverse=True)
            for version_num, filepath, filename in wip_files:
                item_id = f"V{version_num:03d}"
                VERSION_OT_open_version_list.file_paths[item_id] = filepath
                items.append((item_id, f"Version {version_num:03d}", f"Open {filename}"))

        except Exception as exc:
            logger.error("Error listing WIP files: %s", exc)

        if len(items) <= 1:
            return [("NONE", "No versions available", "")]

        return items

    version_enum: bpy.props.EnumProperty(
        name="Version",
        description="Select a version to open",
        items=get_version_list,
    )

    def invoke(self, context, event):
        if not (context.scene.current_project and context.scene.current_shot and context.scene.current_role):
            self.report({"ERROR"}, "No project, shot or role selected")
            return {"CANCELLED"}

        self.get_version_list(context)
        context.window_manager.invoke_search_popup(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if self.version_enum == "NONE":
            self.report({"INFO"}, "No versions available")
            return {"CANCELLED"}

        if self.version_enum == "LATEST":
            bpy.ops.project.open_latest_wip()
            return {"FINISHED"}

        if self.version_enum == "PUBLISHED":
            bpy.ops.project.open_published()
            return {"FINISHED"}

        filepath = VERSION_OT_open_version_list.file_paths.get(self.version_enum)
        if not filepath or not os.path.exists(filepath):
            self.report({"ERROR"}, f"File not found: {self.version_enum}")
            return {"CANCELLED"}

        project_path = context.scene.current_project
        shot_name = context.scene.current_shot
        role_name = context.scene.current_role

        save_current_file()
        bpy.ops.wm.open_mainfile(filepath=filepath)

        context.scene.current_project = project_path
        context.scene.current_shot = shot_name
        context.scene.current_role = role_name

        self.report({"INFO"}, f"Opened: {os.path.basename(filepath)}")
        DirectoryCache.invalidate(os.path.dirname(project_path))
        return {"FINISHED"}


class VERSION_OT_open_published(Operator):
    """Open the published version for the current role."""

    bl_idname = "project.open_published"
    bl_label = "Open Published Version"
    bl_description = "Open the published version of the current role"

    def execute(self, context):
        try:
            if not (context.scene.current_project and context.scene.current_shot and context.scene.current_role):
                self.report({"ERROR"}, "No project, shot or role selected")
                return {"CANCELLED"}

            role_name = context.scene.current_role
            project_path = context.scene.current_project
            shot_name = context.scene.current_shot

            prefs = get_addon_preferences(context)
            project_name, _, project_prefix = get_project_info(project_path, prefs.use_fixed_root)

            for role_mapping in prefs.role_mappings:
                if role_mapping.role_name != role_name:
                    continue

                publish_path = get_publish_path(
                    role_mapping.publish_path_preset,
                    role_mapping,
                    context,
                    project_path,
                    project_name,
                    shot_name,
                    asset_name=role_name,
                )

                if not publish_path:
                    self.report({"ERROR"}, "Could not determine publish path")
                    return {"CANCELLED"}

                publish_file = os.path.join(publish_path, build_publish_filename(project_prefix, shot_name, role_name))
                if not os.path.exists(publish_file):
                    self.report({"ERROR"}, "Published file does not exist")
                    return {"CANCELLED"}

                save_current_file()
                bpy.ops.wm.open_mainfile(filepath=publish_file)

                context.scene.current_project = project_path
                context.scene.current_shot = shot_name
                context.scene.current_role = role_name

                self.report({"INFO"}, f"Opened published file: {os.path.basename(publish_file)}")
                DirectoryCache.invalidate(os.path.dirname(project_path))
                return {"FINISHED"}

            self.report({"ERROR"}, f"Role '{role_name}' not found in settings")
            return {"CANCELLED"}

        except Exception as exc:
            self.report({"ERROR"}, f"Error opening published version: {exc}")
            return {"CANCELLED"}


classes = (
    VERSION_OT_new_wip_version,
    VERSION_OT_open_latest_wip,
    VERSION_OT_publish,
    VERSION_OT_open_version_list,
    VERSION_OT_open_published,
)


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as exc:
            logger.debug("Skipping class registration for %s: %s", cls.__name__, exc)


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as exc:
            logger.debug("Skipping class unregistration for %s: %s", cls.__name__, exc)

