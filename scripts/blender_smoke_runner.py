import argparse
import os
import shutil
import sys
import tempfile
import time
import traceback
from datetime import datetime

import addon_utils
import bpy


def _status(ok):
    return "PASS" if ok else "FAIL"


class SmokeSuite:
    def __init__(self):
        self.results = []
        self.errors = []

    def run_case(self, name, fn):
        try:
            fn()
            self.results.append((name, True, ""))
        except Exception as exc:
            self.results.append((name, False, str(exc)))
            self.errors.append((name, traceback.format_exc()))

    def has_failures(self):
        return any(not ok for _, ok, _ in self.results)


def ensure_addon_enabled():
    for _ in range(10):
        addon = bpy.context.preferences.addons.get("blender_project_manager")
        if addon is not None:
            return addon.preferences

        addon_utils.enable("blender_project_manager", default_set=False, persistent=False)
        try:
            bpy.ops.preferences.addon_enable(module="blender_project_manager")
        except Exception:
            pass
        time.sleep(0.1)

    raise RuntimeError("Failed to enable blender_project_manager add-on in headless session")


def ensure_roles(prefs):
    if len(prefs.role_mappings) > 0:
        return

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


def assert_finished(result, op_name):
    if "FINISHED" not in result:
        raise RuntimeError(f"{op_name} did not finish successfully: {result}")


def run_smoke_suite():
    suite = SmokeSuite()
    temp_root = tempfile.mkdtemp(prefix="bpm_smoke_")
    project_path = os.path.join(temp_root, "PRJ001_SMOKE")
    created_paths = {"temp_root": temp_root, "project_path": project_path}

    prefs = ensure_addon_enabled()
    prefs.use_fixed_root = False
    prefs.fixed_root_path = ""
    ensure_roles(prefs)

    def case_register_cycle():
        addon_utils.disable("blender_project_manager", default_set=False)
        addon_utils.enable("blender_project_manager", default_set=False, persistent=False)
        _, loaded = addon_utils.check("blender_project_manager")
        if not loaded:
            raise RuntimeError("Add-on not loaded after disable/enable cycle")

    def case_create_project():
        result = bpy.ops.project.create_project(project_path=project_path)
        assert_finished(result, "project.create_project")

        workspace = os.path.join(project_path, "3D")
        expected_dirs = [
            os.path.join(workspace, "SHOTS"),
            os.path.join(workspace, "ASSETS 3D", "PROPS"),
            os.path.join(workspace, "ASSETS 3D", "CHR"),
            os.path.join(workspace, "ASSETS 3D", "ENV"),
        ]
        missing = [path for path in expected_dirs if not os.path.isdir(path)]
        if missing:
            raise RuntimeError(f"Missing project structure directories: {missing}")

    def case_create_shot_role():
        result = bpy.ops.project.create_shot(shot_name="SHOT_010", role_name="ANIMATION")
        assert_finished(result, "project.create_shot")

        scene = bpy.context.scene
        current_project = scene.current_project
        if not current_project:
            raise RuntimeError("Scene current_project is empty after create_shot")

        prefix = "PRJ001"
        shot = "SHOT_010"
        role = "ANIMATION"
        workspace = os.path.join(current_project, "3D")
        wip_dir = os.path.join(workspace, "SHOTS", shot, role, "WIP")
        publish_dir = os.path.join(workspace, "SHOTS", shot, role, "PUBLISH")
        assembly_dir = os.path.join(workspace, "SHOTS", shot, "ASSEMBLY")

        expected_files = [
            os.path.join(wip_dir, f"{prefix}_{shot}_{role}_v001.blend"),
            os.path.join(publish_dir, f"{prefix}_{shot}_{role}.blend"),
            os.path.join(assembly_dir, f"{prefix}_{shot}_ASSEMBLY.blend"),
        ]
        missing = [path for path in expected_files if not os.path.isfile(path)]
        if missing:
            raise RuntimeError(f"Missing shot files: {missing}")

    def case_new_wip_and_publish():
        scene = bpy.context.scene
        current_project = scene.current_project
        prefix = "PRJ001"
        shot = scene.current_shot or "SHOT_010"
        role = scene.current_role or "ANIMATION"
        workspace = os.path.join(current_project, "3D")
        wip_v2 = os.path.join(workspace, "SHOTS", shot, role, "WIP", f"{prefix}_{shot}_{role}_v002.blend")
        publish_file = os.path.join(workspace, "SHOTS", shot, role, "PUBLISH", f"{prefix}_{shot}_{role}.blend")

        result = bpy.ops.project.new_wip_version()
        assert_finished(result, "project.new_wip_version")
        if not os.path.isfile(wip_v2):
            raise RuntimeError(f"Expected WIP v002 not found: {wip_v2}")

        result = bpy.ops.project.publish_version()
        assert_finished(result, "project.publish_version")
        if not os.path.isfile(publish_file):
            raise RuntimeError(f"Expected publish file not found: {publish_file}")

    def case_open_and_rebuild_assembly():
        result = bpy.ops.project.open_assembly()
        assert_finished(result, "project.open_assembly")

        result = bpy.ops.project.rebuild_assembly()
        assert_finished(result, "project.rebuild_assembly")

    def case_create_asset_mark_only():
        # Ensure current scene has an active collection to mark as asset
        scene = bpy.context.scene
        collection_name = "SMOKE_ASSET_COLLECTION"
        if collection_name not in bpy.data.collections:
            coll = bpy.data.collections.new(collection_name)
            scene.collection.children.link(coll)
        else:
            coll = bpy.data.collections[collection_name]

        layer_collection = bpy.context.view_layer.layer_collection.children.get(coll.name)
        if layer_collection is not None:
            bpy.context.view_layer.active_layer_collection = layer_collection

        result = bpy.ops.project.create_asset(
            asset_type="PROPS",
            name="SMOKE_ASSET",
            save_mode="MARK_ONLY",
        )
        assert_finished(result, "project.create_asset")

    suite.run_case("Addon register/unregister cycle", case_register_cycle)
    suite.run_case("Create project (flexible root)", case_create_project)
    suite.run_case("Create shot + role initial files", case_create_shot_role)
    suite.run_case("New WIP and publish update", case_new_wip_and_publish)
    suite.run_case("Open and rebuild assembly", case_open_and_rebuild_assembly)
    suite.run_case("Create asset (mark only)", case_create_asset_mark_only)

    return suite, created_paths


def write_report(report_path, suite, created_paths):
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    lines = []
    lines.append(f"# Blender Smoke Report - {bpy.app.version_string}")
    lines.append("")
    lines.append(f"- Date: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"- Blender: {bpy.app.version_string}")
    lines.append(f"- Build hash: {bpy.app.build_hash.decode() if isinstance(bpy.app.build_hash, bytes) else bpy.app.build_hash}")
    lines.append(f"- Temp root: `{created_paths['temp_root']}`")
    lines.append(f"- Project path: `{created_paths['project_path']}`")
    lines.append("")
    lines.append("## Results")
    lines.append("")

    for name, ok, msg in suite.results:
        lines.append(f"- {_status(ok)}: {name}")
        if msg:
            lines.append(f"  - {msg}")

    lines.append("")
    lines.append("## Detailed Errors")
    lines.append("")
    if suite.errors:
        for name, tb in suite.errors:
            lines.append(f"### {name}")
            lines.append("```text")
            lines.append(tb.rstrip())
            lines.append("```")
            lines.append("")
    else:
        lines.append("- None")

    with open(report_path, "w", encoding="utf-8") as file_obj:
        file_obj.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True, help="Path to markdown report output")
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary project directory")
    if "--" in sys.argv:
        args = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :])
    else:
        args = parser.parse_args()

    suite = SmokeSuite()
    created_paths = {}
    try:
        suite, created_paths = run_smoke_suite()
    except Exception as exc:
        suite.results.append(("Smoke bootstrap", False, str(exc)))
        suite.errors.append(("Smoke bootstrap", traceback.format_exc()))
    finally:
        write_report(args.report, suite, created_paths)
        if (not args.keep_temp) and created_paths.get("temp_root"):
            shutil.rmtree(created_paths["temp_root"], ignore_errors=True)

    if suite.has_failures():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
