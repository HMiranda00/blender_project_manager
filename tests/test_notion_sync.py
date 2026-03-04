import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "integrations" / "notion" / "sync.py"
spec = importlib.util.spec_from_file_location("notion_sync", MODULE_PATH)
notion_sync = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(notion_sync)

build_sync_plan = notion_sync.build_sync_plan


class NotionSyncTests(unittest.TestCase):
    def test_build_sync_plan_maps_fields_and_identity(self):
        snapshot = {
            "schema_version": 1,
            "entities": {
                "Project": [
                    {
                        "id": "PRJ001",
                        "project_code": "PRJ001",
                        "status": "active",
                        "updated_at": "2026-03-03T20:00:00Z",
                    }
                ]
            },
        }
        profile = {
            "profile_name": "test_profile",
            "schema_version": 1,
            "notion": {"databases": {"Project": "db_projects"}},
            "identity": {"Project": ["project_code"]},
            "mapping": {
                "Project.project_code": "Code",
                "Project.status": "Status",
                "Project.updated_at": "Updated At",
            },
        }

        plan = build_sync_plan(snapshot, profile)
        self.assertEqual(len(plan), 1)
        item = plan[0]
        self.assertEqual(item["entity"], "Project")
        self.assertEqual(item["database_id"], "db_projects")
        self.assertEqual(item["identity"], "PRJ001")
        self.assertEqual(item["properties"]["Code"], "PRJ001")
        self.assertEqual(item["properties"]["Status"], "active")


if __name__ == "__main__":
    unittest.main()
