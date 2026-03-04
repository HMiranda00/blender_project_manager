# Notion Integration (Template-Swappable)

This folder contains the add-on side integration contract for Notion.

## Goal

Keep Blender pipeline logic independent from any specific Notion template.
Only profile files should change when you switch templates.

## Files

- `schema.json`: canonical entities/fields used internally by the add-on.
- `profiles/studio_template_v1.json`: mapping profile example for one Notion template.
- `sync.py`: dry-run sync adapter that converts snapshot data into mapped Notion payloads.

## Snapshot Input Format

`sync.py` expects a JSON with this shape:

```json
{
  "schema_version": 1,
  "entities": {
    "Project": [
      {
        "id": "PRJ001",
        "project_code": "PRJ001",
        "status": "active",
        "updated_at": "2026-03-03T20:00:00Z"
      }
    ],
    "Shot": [],
    "Role": [],
    "Version": [],
    "Asset": [],
    "Assembly": [],
    "PublishEvent": []
  }
}
```

## Usage

Dry-run only (safe):

```powershell
python integrations/notion/sync.py `
  --profile integrations/notion/profiles/studio_template_v1.json `
  --input path/to/pipeline_snapshot.json `
  --dry-run `
  --output integrations/notion/out_dry_run.json
```

`--output` is optional. If omitted, output is printed to stdout.

## Next step

When ready to write to Notion for real, extend `sync.py` with Notion API calls:
- authenticate with integration token
- upsert page by identity keys
- write mapped property payloads

