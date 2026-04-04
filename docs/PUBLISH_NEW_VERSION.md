# Publish New Version (One Flow)

This project is configured to publish Blender Extensions artifacts from this same repository.

## What this flow does

Running `scripts/release_new_version.ps1`:

1. Updates version in:
   - `__init__.py` (`bl_info["version"]`)
   - `blender_manifest.toml` (`version`)
   - `README.md` version badge
2. Ensures `CHANGELOG.md` has a section for the new version.
3. Runs unit tests.
4. Validates extension manifest.
5. Builds extension zip.
6. Generates `extension_repo/index.json`.
7. Leaves artifacts ready for sync to your external publication repository.

## Command

```powershell
powershell -ExecutionPolicy Bypass -File scripts/release_new_version.ps1 -Version 1.7.0
```

Optional flags:

- `-SkipTests`
- `-SkipBuild`
- `-BlenderExe "C:\Path\to\blender.exe"`

## Output artifacts

Generated in `extension_repo/`:

- `blender_project_manager-<version>.zip`
- `index.json`

These are the files needed for Blender remote repository updates.

## Sync to external publication repo

If Blender consumes another repository as the remote extension source, sync the generated artifacts with:

```powershell
git add extension_repo __init__.py blender_manifest.toml README.md CHANGELOG.md
git commit -m "Release X.Y.Z"
git push origin master
```

Full guide:

- `docs/DEPLOY_EXTENSION_REPO.md`

After the push, the `Publish Extension Repo` GitHub Actions workflow syncs the artifacts to `https://github.com/HMiranda00/h_blender_addons.git`.

## Register local extension repository in Blender (optional)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/register_local_extension_repo.ps1
```

Optional sync (requires Blender online access enabled):

```powershell
powershell -ExecutionPolicy Bypass -File scripts/register_local_extension_repo.ps1 -Sync
```

## Before creating a GitHub release

1. Fill `CHANGELOG.md` entries for the version.
2. Commit version bump and changelog.
3. Create Git tag (example: `v1.7.0`).
4. Upload `extension_repo/*.zip` and `extension_repo/index.json` to your hosting target.
