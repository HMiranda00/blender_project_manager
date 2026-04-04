# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed
- `get_project_info()` now resolves workspace paths defensively for fixed-root, flexible-root, legacy, and manually selected workspace folders.
- Architecture and troubleshooting docs updated to describe the centralized project/workspace path contract.
- Extension release docs now cover sync to an external publication repository.
- Production publishing is now driven from `master` via GitHub Actions release automation instead of requiring committed `extension_repo/` updates.

### Fixed
- Intermittent `UnboundLocalError` on `workspace_path` when the current project path did not match the fixed-root naming pattern.
- Added regression coverage for project/workspace path resolution outside Blender runtime.

### Added
- `scripts/deploy_extension_repo.ps1` to sync `index.json` and extension zip artifacts to an external publication repository, with optional commit and push.
- `docs/DEPLOY_EXTENSION_REPO.md` documenting the external publication repo workflow.
- GitHub Actions workflow [ci.yml](/Users/henrique/github/blender_project_manager/.github/workflows/ci.yml) for branch and PR validation.
- GitHub Actions workflow [release-extension.yml](/Users/henrique/github/blender_project_manager/.github/workflows/release-extension.yml) to build and publish production artifacts from `master`.

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
