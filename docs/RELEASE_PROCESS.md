# Release Process and Versioning Policy

## Versioning

- Patch (`x.y.Z`): bug fixes, no intentional workflow changes.
- Minor (`x.Y.z`): new operators/workflows, backward-compatible defaults.
- Major (`X.y.z`): folder/naming contract changes or breaking behavior.

## Release Checklist

1. Work in feature branches and validate with CI.
2. Before release, bump version metadata if needed:
   - `powershell -ExecutionPolicy Bypass -File scripts/release_new_version.ps1 -Version X.Y.Z`
3. Merge to `master` only what should go to production.
4. Let the `Release Extension` workflow:
   - run unit tests
   - validate extension manifest
   - build extension zip
   - generate repository `index.json`
   - publish to `https://github.com/HMiranda00/h_blender_addons.git`
5. Execute Blender validation checklist in:
   - Blender 4.4 LTS
   - Blender 5.0.1
6. Update changelog using behavior-focused entries:
   - fixed
   - changed
   - added
7. Verify the published extension in a clean Blender profile when needed.

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
