# Prompt Template For New Chats (Release)

Use this prompt in a new chat when you want Codex to publish a new version:

```text
Publish version X.Y.Z using this repo release flow.

Requirements:
1) Update version metadata for X.Y.Z.
2) Update CHANGELOG.md with concrete Added/Changed/Fixed notes.
3) Prepare the repo so merging/pushing to master will publish production automatically.
4) Show me the expected GitHub Actions impact on CI and release.
5) If anything fails, fix it and re-run.
```

## Optional additions

- Add `-BlenderExe` if Blender is not in default path.
- Add `-SkipTests` only for emergency hotfixes.
