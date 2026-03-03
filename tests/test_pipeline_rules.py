import unittest
import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "utils" / "pipeline_rules.py"
spec = importlib.util.spec_from_file_location("pipeline_rules", MODULE_PATH)
pipeline_rules = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(pipeline_rules)

build_assembly_filename = pipeline_rules.build_assembly_filename
build_publish_filename = pipeline_rules.build_publish_filename
build_wip_filename = pipeline_rules.build_wip_filename
build_wip_prefix = pipeline_rules.build_wip_prefix
extract_wip_version = pipeline_rules.extract_wip_version
resolve_publish_template = pipeline_rules.resolve_publish_template
select_latest_wip = pipeline_rules.select_latest_wip


class PipelineRulesTests(unittest.TestCase):
    def test_build_wip_filename(self):
        self.assertEqual(
            build_wip_filename("PRJ001", "SHOT_010", "ANIMATION", 12),
            "PRJ001_SHOT_010_ANIMATION_v012.blend",
        )

    def test_build_publish_filename(self):
        self.assertEqual(
            build_publish_filename("PRJ001", "SHOT_010", "ANIMATION"),
            "PRJ001_SHOT_010_ANIMATION.blend",
        )

    def test_build_assembly_filename(self):
        self.assertEqual(
            build_assembly_filename("PRJ001", "SHOT_010"),
            "PRJ001_SHOT_010_ASSEMBLY.blend",
        )

    def test_extract_wip_version(self):
        prefix = build_wip_prefix("PRJ001", "SHOT_010", "ANIMATION")
        self.assertEqual(extract_wip_version("PRJ001_SHOT_010_ANIMATION_v021.blend", prefix), 21)
        self.assertIsNone(extract_wip_version("PRJ001_SHOT_010_ANIMATION.blend", prefix))

    def test_select_latest_wip(self):
        prefix = build_wip_prefix("PRJ001", "SHOT_010", "ANIMATION")
        latest_name, latest_version = select_latest_wip(
            [
                "PRJ001_SHOT_010_ANIMATION_v002.blend",
                "PRJ001_SHOT_010_ANIMATION_v010.blend",
                "PRJ001_SHOT_010_ANIMATION_v007.blend",
                "random_file.blend",
            ],
            prefix,
        )
        self.assertEqual(latest_name, "PRJ001_SHOT_010_ANIMATION_v010.blend")
        self.assertEqual(latest_version, 10)

    def test_resolve_publish_template_default_and_custom(self):
        placeholders = {
            "root": "X:/PROJECT/3D",
            "projectCode": "PRJ001",
            "shot": "SHOT_010",
            "role": "ANIMATION",
            "assetName": "CHAIR_A",
        }

        self.assertEqual(
            resolve_publish_template("SHOTS", "", placeholders),
            "X:/PROJECT/3D/SHOTS/SHOT_010/ANIMATION/PUBLISH",
        )
        self.assertEqual(
            resolve_publish_template("PROPS", "", placeholders),
            "X:/PROJECT/3D/ASSETS 3D/PROPS/CHAIR_A/PUBLISH",
        )
        self.assertEqual(
            resolve_publish_template("CUSTOM", "{root}/LIB/{assetName}/PUB", placeholders),
            "X:/PROJECT/3D/LIB/CHAIR_A/PUB",
        )


if __name__ == "__main__":
    unittest.main()
