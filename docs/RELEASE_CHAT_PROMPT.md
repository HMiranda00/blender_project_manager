# Prompt Template For New Chats (Release)

Use this prompt in a new chat when you want Codex to publish a new version:

```text
Publish version X.Y.Z using this repo release flow.

Requirements:
1) Run scripts/release_new_version.ps1 with -Version X.Y.Z.
2) Update CHANGELOG.md with concrete Added/Changed/Fixed notes.
3) Regenerate extension_repo/index.json and package zip.
4) Commit and push the release changes so the publication workflow updates h_blender_addons automatically.
5) Show me the exact files generated, workflow impact, and final git diff summary.
6) If anything fails, fix it and re-run.
```

## Optional additions

- Add `-BlenderExe` if Blender is not in default path.
- Add `-SkipTests` only for emergency hotfixes.
