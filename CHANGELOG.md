# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.6.3] - 2026-03-03

### Added
- Smoke evidence report for Blender 5.0.1 in `docs/reports/smoke_5_0_1.md`.

### Changed
- Alignment report updated with Extension install status and namespace compatibility notes.

### Fixed
- Blender 5 Extensions namespace compatibility for add-on preferences lookup.
- `AddonPreferences` initialization in Extension mode (`bl_idname` derived from package).
- Asset Browser cleanup lookup still referencing non-namespaced add-on key.

## [1.6.2] - 2026-03-03

### Added
- Blender Extensions release pipeline in-repo (`blender_manifest.toml`, package build and `index.json` generation).
- Release automation scripts:
  - `scripts/release_new_version.ps1`
  - `scripts/register_local_extension_repo.ps1`
- Operational release docs:
  - `docs/PUBLISH_NEW_VERSION.md`
  - `docs/RELEASE_CHAT_PROMPT.md`
  - extension repository docs under `extension_repo/`.
- Automated smoke/validation support docs and reports structure.

### Changed
- Baseline metadata and docs aligned to Blender 4.4 LTS + 5.0.1.
- Versioning/test/release workflow consolidated for repeatable new-chat publishing.
- Add-on role settings now include `Controls Compositor` (Blender 5.0+).

### Fixed
- Duplicate operator registration (`project.toggle_asset_browser`) removed.
- Utility duplication reduced (`get_project_info`, canonical WIP path behavior).
- Unnecessary folder creation reduced (WIP/paths now created when truly needed).
- Add-on initialization robustness in headless contexts (`preferences` default role setup timing).
- Context restoration issues after file-open operations in critical version/shot flows.

