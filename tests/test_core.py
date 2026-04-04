import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "utils" / "core.py"


def load_core_module():
    bpy_stub = types.ModuleType("bpy")
    bpy_stub.app = types.SimpleNamespace(version=(5, 1, 0))
    bpy_stub.data = types.SimpleNamespace(is_saved=False)
    bpy_stub.ops = types.SimpleNamespace()
    bpy_stub.types = types.SimpleNamespace(Scene=object)
    bpy_stub.context = types.SimpleNamespace(
        view_layer=types.SimpleNamespace(layer_collection=types.SimpleNamespace(children={})),
        window_manager=types.SimpleNamespace(windows=[]),
        scene=types.SimpleNamespace(),
    )

    sys.modules["bpy"] = bpy_stub

    addon_stub = types.ModuleType("blender_project_manager.utils.addon")
    addon_stub.get_addon_preferences = lambda context: None
    sys.modules["blender_project_manager.utils.addon"] = addon_stub

    pipeline_stub = types.ModuleType("blender_project_manager.utils.pipeline_rules")
    pipeline_stub.resolve_publish_template = lambda preset, custom_path, placeholders: ""
    sys.modules["blender_project_manager.utils.pipeline_rules"] = pipeline_stub

    package_stub = types.ModuleType("blender_project_manager")
    package_stub.__path__ = [str(REPO_ROOT)]
    sys.modules["blender_project_manager"] = package_stub

    utils_package_stub = types.ModuleType("blender_project_manager.utils")
    utils_package_stub.__path__ = [str(REPO_ROOT / "utils")]
    sys.modules["blender_project_manager.utils"] = utils_package_stub

    spec = importlib.util.spec_from_file_location("blender_project_manager.utils.core", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


core = load_core_module()


class CoreProjectInfoTests(unittest.TestCase):
    def test_fixed_root_uses_existing_legacy_workspace_when_prefix_is_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "Projeto Solto"
            workspace = project_root / "3D"
            workspace.mkdir(parents=True)

            project_name, workspace_path, project_prefix = core.get_project_info(
                str(project_root),
                is_fixed_root=True,
            )

            self.assertEqual(project_name, "Projeto Solto")
            self.assertEqual(workspace_path, str(workspace))
            self.assertEqual(project_prefix, "")

    def test_fixed_root_accepts_workspace_folder_as_current_project(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "007 - Demo Project" / "03 - 3D"
            workspace.mkdir(parents=True)

            project_name, workspace_path, project_prefix = core.get_project_info(
                str(workspace),
                is_fixed_root=True,
            )

            self.assertEqual(project_name, "007 - Demo Project")
            self.assertEqual(workspace_path, str(workspace))
            self.assertEqual(project_prefix, "007")

    def test_flexible_root_defaults_to_3d_workspace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "PRJ001_MyProject"
            project_root.mkdir()

            project_name, workspace_path, project_prefix = core.get_project_info(
                str(project_root),
                is_fixed_root=False,
            )

            self.assertEqual(project_name, "PRJ001_MyProject")
            self.assertEqual(workspace_path, str(project_root / "3D"))
            self.assertEqual(project_prefix, "PRJ001")


if __name__ == "__main__":
    unittest.main()
