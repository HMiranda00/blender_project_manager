import logging
import os

import bpy
from bpy.app.handlers import (
    persistent,
    load_post,
    load_factory_preferences_post,
    load_factory_startup_post,
    redo_post,
    undo_post,
)
from bpy.types import Operator

from ..utils import get_addon_preferences, get_project_info

logger = logging.getLogger(__name__)


def cleanup_project_libraries(scene=None):
    """Remove temporary project asset libraries from preferences."""
    try:
        ctx = bpy.context

        has_project_context = (
            hasattr(ctx.scene, "current_project")
            and ctx.scene.current_project
            and os.path.exists(ctx.scene.current_project)
        )

        current_project_name = None
        if has_project_context:
            prefs = get_addon_preferences(ctx)
            project_path = ctx.scene.current_project
            project_name, _, _ = get_project_info(project_path, prefs.use_fixed_root)
            current_project_name = project_name

        asset_libs = ctx.preferences.filepaths.asset_libraries
        to_remove = []

        for i, lib in enumerate(asset_libs):
            lib_path = bpy.path.abspath(lib.path)
            if "ASSETS 3D" in lib_path:
                if not has_project_context or lib.name != current_project_name:
                    to_remove.append(i)

        for i in reversed(to_remove):
            try:
                bpy.ops.preferences.asset_library_remove(index=i)
            except Exception as exc:
                logger.warning("Error removing library at index %s: %s", i, exc)

    except Exception as exc:
        logger.error("Error cleaning up libraries: %s", exc)


@persistent
def on_file_change(dummy):
    """Handler for file changes."""
    cleanup_project_libraries()
    return None


@persistent
def on_undo_redo(dummy):
    """Handler for undo/redo."""
    cleanup_project_libraries()
    return None


class ASSETBROWSER_OT_setup(Operator):
    """Setup Asset Browser for the current project."""

    bl_idname = "project.setup_asset_browser"
    bl_label = "Setup Asset Browser"
    bl_description = "Configure Asset Browser paths for this project"

    link_type: bpy.props.EnumProperty(
        name="Link Type",
        items=[
            ("LINK", "Link", "Assets will be linked"),
            ("APPEND", "Append", "Assets will be appended"),
        ],
        default="LINK",
    )

    @classmethod
    def poll(cls, context):
        return context.scene.current_project is not None

    def setup_catalogs(self, library_path):
        """Create default catalogs."""
        catalog_path = os.path.join(library_path, "blender_assets.cats.txt")

        catalogs_data = """# This is an Asset Catalog Definition file for Blender.
#
# Empty lines and lines starting with `#` will be ignored.
# The first non-ignored line should be the version indicator.
# Other lines are of the format "UUID:catalog/path/for/assets:simple catalog name"
VERSION 1
d1f81597-d27d-42fd-8386-3a3def6c9200:PROPS:PROPS
8bfeff41-7692-4f58-8238-a5c4d9dad2d0:CHR:CHR
b741e8a3-5da8-4f5a-8f4c-e05dd1e4766c:ENV:ENV
f5780a5c-74a4-4dd9-9e3d-c3654cf91f5c:MATERIALS:MATERIALS"""

        with open(catalog_path, "w", encoding="utf-8") as file_obj:
            file_obj.write(catalogs_data)

    def execute(self, context):
        try:
            cleanup_project_libraries(context.scene)

            prefs = get_addon_preferences(context)
            project_path = context.scene.current_project
            project_name, workspace_path, _ = get_project_info(project_path, prefs.use_fixed_root)

            assets_path = os.path.join(workspace_path, "ASSETS 3D")
            os.makedirs(assets_path, exist_ok=True)

            self.setup_catalogs(assets_path)

            asset_libs = context.preferences.filepaths.asset_libraries
            for i, lib in enumerate(asset_libs):
                if lib.name == project_name:
                    bpy.ops.preferences.asset_library_remove(index=i)
                    break

            bpy.ops.preferences.asset_library_add()
            new_lib = context.preferences.filepaths.asset_libraries[-1]
            new_lib.name = project_name
            new_lib.path = assets_path

            for asset_library in context.preferences.filepaths.asset_libraries:
                if asset_library.name == project_name:
                    asset_library.import_method = "APPEND" if self.link_type == "APPEND" else "LINK"

            self.report({"INFO"}, f"Asset Library '{project_name}' configured with catalogs")
            return {"FINISHED"}

        except Exception as exc:
            logger.error("Error configuring Asset Browser: %s", exc)
            self.report({"ERROR"}, f"Error configuring Asset Browser: {exc}")
            return {"CANCELLED"}


class ASSETBROWSER_OT_toggle(Operator):
    """Toggle Asset Browser visibility."""

    bl_idname = "project.toggle_asset_browser"
    bl_label = "Toggle Asset Browser"
    bl_description = "Show/Hide Asset Browser"

    def execute(self, context):
        try:
            asset_areas = [
                area
                for area in context.screen.areas
                if area.type == "FILE_BROWSER" and area.ui_type == "ASSETS"
            ]

            if asset_areas:
                for area in asset_areas:
                    with context.temp_override(area=area):
                        bpy.ops.screen.area_close()

                context.scene.show_asset_manager = False
            else:
                view3d_area = next((area for area in context.screen.areas if area.type == "VIEW_3D"), None)

                if view3d_area:
                    areas_before = context.screen.areas[:]

                    with context.temp_override(area=view3d_area, region=view3d_area.regions[0]):
                        bpy.ops.screen.area_split(direction="HORIZONTAL", factor=0.15)

                    new_area = next((area for area in context.screen.areas if area not in areas_before), None)

                    if new_area is None:
                        self.report({"ERROR"}, "Could not find newly created area")
                        return {"CANCELLED"}

                    new_area.type = "FILE_BROWSER"
                    new_area.ui_type = "ASSETS"

                    prefs = get_addon_preferences(context)
                    project_path = context.scene.current_project
                    project_name, _, _ = get_project_info(project_path, prefs.use_fixed_root)

                    def set_library():
                        for library in context.preferences.filepaths.asset_libraries:
                            if library.name == project_name:
                                space = new_area.spaces.active
                                if hasattr(space, "params"):
                                    space.params.asset_library_reference = library.name
                                return None
                        return None

                    bpy.app.timers.register(set_library, first_interval=0.1)
                    context.scene.show_asset_manager = True

            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()

            return {"FINISHED"}

        except Exception as exc:
            logger.error("Error toggling asset browser: %s", exc)
            self.report({"ERROR"}, f"Error toggling asset browser: {exc}")
            return {"CANCELLED"}


classes = (ASSETBROWSER_OT_setup, ASSETBROWSER_OT_toggle)

handlers = (
    (load_post, on_file_change),
    (load_factory_preferences_post, on_file_change),
    (load_factory_startup_post, on_file_change),
    (undo_post, on_undo_redo),
    (redo_post, on_undo_redo),
)


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as exc:
            logger.debug("Skipping class registration for %s: %s", cls.__name__, exc)

    for handler_list, func in handlers:
        try:
            if func not in handler_list:
                handler_list.append(func)
        except Exception as exc:
            logger.warning("Error adding handler %s: %s", func.__name__, exc)


def unregister():
    for handler_list, func in handlers:
        try:
            if func in handler_list:
                handler_list.remove(func)
        except Exception as exc:
            logger.warning("Error removing handler %s: %s", func.__name__, exc)

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as exc:
            logger.debug("Skipping class unregistration for %s: %s", cls.__name__, exc)

    try:
        cleanup_project_libraries()
    except Exception as exc:
        logger.warning("Error cleaning up libraries on unregister: %s", exc)

