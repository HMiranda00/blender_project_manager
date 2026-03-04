# Add-on Mapping + Notion Integration Blueprint

Date: 2026-03-03
Addon: Blender Project Manager (`1.6.3`)
Baseline: Blender `4.4 LTS + 5.0.1`

## 1) Entry Points and Runtime State

### Core entry point
- File: `__init__.py`
- Registers:
  - `preferences.register()`
  - `operators.register()`
  - `panels.register()`
- Scene runtime properties:
  - `scene.current_project` (String)
  - `scene.current_shot` (String)
  - `scene.current_role` (String)
  - `scene.previous_file` (String)
  - `scene.show_asset_manager` (Bool)
  - `scene.show_role_status` (Bool)

### Add-on preferences identity
- File: `preferences.py`
- `ProjectPreferences.bl_idname = __package__ or "blender_project_manager"`
- This supports both:
  - classic add-on module (`blender_project_manager`)
  - Blender Extensions namespaced module (`bl_ext.user_default.blender_project_manager`)

## 2) Module Map (Complete)

### `operators/`
- `create_project.py`
  - `project.create_project`
  - Creates project root/workspace and initial structure.
- `load_project.py`
  - `project.load_project`
  - Loads an existing project and syncs recents.
- `create_shot.py`
  - `project.create_shot`, `project.duplicate_shot`
  - Creates shot/role structure and first files.
- `open_shot.py`
  - `project.open_shot`
  - Opens shot role file; auto-creates first WIP if needed.
- `link_role.py`
  - `project.link_role`
  - Links/Appends publish from another role.
- `open_role_file.py`
  - `project.open_role_file`
  - Opens role publish/WIP file by context.
- `asset_operators.py`
  - `project.reload_links`, `project.create_asset`
  - Asset creation and library link refresh.
- `asset_browser_setup.py`
  - `project.setup_asset_browser`, `project.toggle_asset_browser`
  - Configures and toggles Asset Browser.
  - Persistent handlers: `on_file_change`, `on_undo_redo`.
- `recent_projects.py`
  - `project.open_recent`, `project.clear_recent_list`
  - Manages recent projects collection.
- `ui_operators.py`
  - `project.dummy_operator`
  - UI fallback helper.
- `version_control.py`
  - `project.new_wip_version`, `project.open_latest_wip`, `project.publish_version`, `project.open_version_list`, `project.open_published`
  - WIP increment, publish, open latest/specific/published.
- `assembly_control.py`
  - `project.rebuild_assembly`, `project.prepare_assembly_render`, `project.open_assembly`, `project.open_current_directory`
  - Assembly open/rebuild/render-prep and folder open.
- `asset_browser_view.py`
  - Legacy/deactivated module (kept in repo, not canonical toggle implementation).

### `panels/`
- `project_panel.py`
  - Panel: `VIEW3D_PT_project_management`
  - Main N-panel UI for project/shot/role/version/assets/assembly actions.

### `utils/`
- `addon.py`
  - `get_addon_entry`, `get_addon_preferences`
  - Namespaced add-on key compatibility helper.
- `core.py`
  - Project info parsing, structure creation, publish path resolve, collection/world/compositor setup.
- `version_control.py`
  - WIP path resolution, latest WIP lookup, first WIP bootstrap + publish.
- `pipeline_rules.py`
  - Pure rules for naming/version parsing and publish templates.
- `cache.py`
  - Directory cache helper.

### Root/config/test/release files
- `preferences.py`: role model, add/remove role, import/export config.
- `tests/test_pipeline_rules.py`: pure unit tests (naming/path/version rules).
- `scripts/run_unit_tests.ps1`: test runner.
- `scripts/blender_smoke_runner.py`: headless smoke tests with `bpy`.
- `scripts/release_new_version.ps1`: bump version + validate + build + generate `index.json`.
- `extension_repo/`: published extension artifacts (`zip`, `index.json`).

## 3) Data Model (Current)

### Scene (runtime context)
- Current selection state used by almost all operators.
- Acts as session context, not persistent pipeline database.

### AddonPreferences
- Root settings:
  - `use_fixed_root`, `fixed_root_path`
- `role_mappings` (`RoleMapping`):
  - `role_name`, `description`, `icon`, `collection_color`
  - `hide_viewport_default`, `exclude_from_view_layer`, `show_status`
  - `owns_world`, `owns_compositor` (5.0+ behavior), `skip_assembly`
  - `publish_path_preset`, `custom_publish_path`
- `recent_projects` list:
  - `path`, `name`, `is_fixed_root`

## 4) File/Folder and Naming Contracts

### Workspace root
- Flexible root: `<project>/3D`
- Fixed root: `<project>/03 - 3D`

### Canonical folders
- `SHOTS/<SHOT>/<ROLE>/WIP`
- `SHOTS/<SHOT>/<ROLE>/PUBLISH`
- `SHOTS/<SHOT>/ASSEMBLY`
- `ASSETS 3D/PROPS|CHR|ENV`

### Canonical names (`utils/pipeline_rules.py`)
- WIP: `{project_prefix}_{shot}_{role}_v###.blend`
- Publish: `{project_prefix}_{shot}_{role}.blend`
- Assembly: `{project_prefix}_{shot}_ASSEMBLY.blend`

## 5) Operational Flows (What the Add-on Actually Does)

1. Project lifecycle:
- Create/load project.
- Store active context in Scene.
- Configure project asset library.

2. Shot/role lifecycle:
- Create shot + role structure.
- Bootstrap first WIP (`v001`) and publish copy.
- Open/create role file on demand.

3. Version lifecycle:
- Increment WIP (`new_wip_version`).
- Publish from latest WIP.
- Open latest/specific/published versions.

4. Assembly lifecycle:
- Open/create assembly file.
- Rebuild linked role publishes.
- Prepare render copy.

5. Asset lifecycle:
- Create/mark assets.
- Toggle browser and reload libraries.

## 6) Notion Integration Blueprint (Template-Swappable)

Goal: integrate this add-on with an existing Notion template, while keeping template replacement cheap.

### Key rule
Use a stable internal schema in the add-on side, and map to Notion via a template profile file. Never hardcode Notion property names in core logic.

### 6.1 Canonical internal schema (source of truth)
Use these entities:
- `Project`
- `Shot`
- `Role`
- `Version`
- `Asset`
- `Assembly`
- `PublishEvent`

Minimal canonical fields:
- `id` (stable slug/id)
- `project_code`
- `shot_name`
- `role_name`
- `status`
- `version_number`
- `wip_path`
- `publish_path`
- `assembly_path`
- `updated_at`
- `blender_version`

### 6.2 Template profile (swap layer)
Create one JSON profile per Notion template, example:

```json
{
  "profile_name": "studio_template_v1",
  "notion": {
    "databases": {
      "projects": "<db_id>",
      "shots": "<db_id>",
      "roles": "<db_id>",
      "versions": "<db_id>",
      "assets": "<db_id>"
    }
  },
  "mapping": {
    "Project.project_code": "Code",
    "Project.status": "Status",
    "Shot.shot_name": "Shot",
    "Shot.project_code": "Project Code",
    "Role.role_name": "Role",
    "Version.version_number": "Version",
    "Version.wip_path": "WIP Path",
    "Version.publish_path": "Publish Path",
    "Asset.id": "Asset ID",
    "Asset.status": "Status"
  }
}
```

When you change Notion template, only this profile changes.

### 6.3 Sync architecture
- Step A: Export pipeline snapshot from add-on (JSON).
- Step B: Notion adapter reads snapshot + selected profile.
- Step C: Adapter upserts pages by stable IDs.

Recommended files:
- `integrations/notion/schema.json` (canonical entity schema)
- `integrations/notion/profiles/<name>.json` (template mappings)
- `integrations/notion/sync.py` (or `sync.ts`) adapter implementation

### 6.4 Upsert identity strategy
- `Project`: `project_code`
- `Shot`: `project_code + shot_name`
- `Role`: `project_code + shot_name + role_name`
- `Version`: `project_code + shot_name + role_name + version_number`
- `Asset`: `project_code + asset_name`

This prevents duplicates when syncing repeatedly.

## 7) MCP Usage (Practical)

If using Notion MCP in future chats:
1. Create/select target template (or databases).
2. Fill a new profile JSON with real database/property names.
3. Run sync with profile name.
4. Validate a small sample (`1 project, 1 shot, 2 roles`) before bulk sync.

Suggested command contract for future automation:
- `sync_notion --profile studio_template_v1 --input exports/pipeline_snapshot.json --dry-run`

## 8) Implementation Roadmap (Low Risk)

1. Add JSON snapshot exporter from current Blender state + filesystem.
2. Add profile loader + validator.
3. Add dry-run sync (log only).
4. Add real upsert sync.
5. Add UI action: `Export Notion Snapshot` (first), then `Sync to Notion`.

## 9) What to Keep Stable for Integration

- Keep operator `bl_idname` stable.
- Keep naming/path contracts stable.
- Keep Scene context keys (`current_project`, `current_shot`, `current_role`).
- Keep canonical schema versioned (e.g. `schema_version: 1`).

---

This file is the baseline map for building Notion integration without coupling the add-on to a single Notion template.
