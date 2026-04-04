# Release Process and Versioning Policy

## Versioning

- Patch (`x.y.Z`): bug fixes, no intentional workflow changes.
- Minor (`x.Y.z`): new operators/workflows, backward-compatible defaults.
- Major (`X.y.z`): folder/naming contract changes or breaking behavior.

## Release Checklist

1. Run pure unit tests:
   - `powershell -ExecutionPolicy Bypass -File scripts/run_unit_tests.ps1`
2. Run automated version bump + extension packaging:
   - `powershell -ExecutionPolicy Bypass -File scripts/release_new_version.ps1 -Version X.Y.Z`
3. Sync generated extension artifacts to the external publication repo when applicable:
   - push this repo with updated `extension_repo/` so GitHub Actions publishes to `https://github.com/HMiranda00/h_blender_addons.git`
4. Execute Blender validation checklist in:
   - Blender 4.4 LTS
   - Blender 5.0.1
5. Update changelog using behavior-focused entries:
   - fixed
   - changed
   - added
6. Package add-on zip and verify installation in clean Blender profile.

## Changelog Template

### Added
- ...

### Changed
- ...

### Fixed
- ...

### Known Limitations
- ...

## Operational Docs

- `docs/PUBLISH_NEW_VERSION.md`
- `docs/DEPLOY_EXTENSION_REPO.md`
- `docs/RELEASE_CHAT_PROMPT.md`
