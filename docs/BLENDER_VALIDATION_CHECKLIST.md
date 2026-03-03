# Blender Validation Checklist (4.4 LTS + 5.0.1)

Use this same checklist in both versions.

## Execution Metadata

- Date:
- Blender version:
- OS:
- Add-on commit/tag:
- Tester:

## Flow A - Project

1. Create project with fixed root.
Expected: project folder + `03 - 3D` + standard tree created.
Observed:
Result: PASS/FAIL

2. Create project with flexible root.
Expected: project folder + `3D` + standard tree created.
Observed:
Result: PASS/FAIL

3. Load project and verify recent list update.
Expected: loaded project appears in recent list top position.
Observed:
Result: PASS/FAIL

## Flow B - Shot/Role

1. Create shot with role set to `LINK`.
Expected: role structure with `WIP`/`PUBLISH`, first WIP and publish created.
Observed:
Result: PASS/FAIL

2. Create shot with role set to `APPEND`.
Expected: same as above, no registration/runtime errors.
Observed:
Result: PASS/FAIL

3. Open shot without prior WIP.
Expected: `v001` auto-created and opened.
Observed:
Result: PASS/FAIL

## Flow C - Versioning

1. New WIP from `v001` to `v002`.
Expected: new file saved with incremented version.
Observed:
Result: PASS/FAIL

2. Publish current role.
Expected: publish file updated from latest WIP.
Observed:
Result: PASS/FAIL

3. Open version list and open:
- latest WIP
- published
- explicit historical version
Expected: each selection opens correct file and keeps scene context.
Observed:
Result: PASS/FAIL

## Flow D - Assembly

1. Open assembly when file does not exist.
Expected: assembly created and opened.
Observed:
Result: PASS/FAIL

2. Rebuild assembly with one role flagged `skip_assembly=True`.
Expected: skipped role not linked, others linked.
Observed:
Result: PASS/FAIL

3. Prepare assembly render.
Expected: render copy created under `SHOTS/!local/<date>`.
Observed:
Result: PASS/FAIL

## Flow E - Assets

1. Create asset from shot file.
Expected: asset file created and linked back to shot.
Observed:
Result: PASS/FAIL

2. Create asset from normal file in modes:
- `NEW_FILE`
- `SAVE_AS`
- `MARK_ONLY`
Expected: each mode performs its corresponding behavior without errors.
Observed:
Result: PASS/FAIL

3. Toggle asset browser repeatedly.
Expected: opens/closes without duplicate operator errors.
Observed:
Result: PASS/FAIL

## Regression

1. Disable/enable add-on repeatedly.
Expected: no register/unregister errors.
Observed:
Result: PASS/FAIL

2. Open a new Blender file.
Expected: handlers remain active and stable.
Observed:
Result: PASS/FAIL

## Failures Log

- Include traceback/log excerpts and reproduction steps for each FAIL.
