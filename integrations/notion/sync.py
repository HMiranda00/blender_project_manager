import argparse
import json
import sys
from pathlib import Path


def _load_json(path):
    with open(path, "r", encoding="utf-8") as fobj:
        return json.load(fobj)


def _validate_profile(profile):
    required_top = ["profile_name", "schema_version", "notion", "identity", "mapping"]
    for key in required_top:
        if key not in profile:
            raise ValueError(f"Missing key in profile: {key}")

    if "databases" not in profile["notion"]:
        raise ValueError("Missing notion.databases in profile")


def _build_identity_value(entity_name, record, identity_fields):
    values = []
    for field in identity_fields:
        values.append(str(record.get(field, "")))
    return "::".join(values)


def _map_record(entity_name, record, mapping):
    properties = {}
    for source_key, notion_field in mapping.items():
        prefix = f"{entity_name}."
        if not source_key.startswith(prefix):
            continue
        field_name = source_key[len(prefix) :]
        if field_name in record:
            properties[notion_field] = record[field_name]
    return properties


def build_sync_plan(snapshot, profile):
    schema_version = snapshot.get("schema_version")
    if schema_version != profile.get("schema_version"):
        raise ValueError(
            f"Schema version mismatch: snapshot={schema_version}, profile={profile.get('schema_version')}"
        )

    entities = snapshot.get("entities", {})
    databases = profile["notion"]["databases"]
    identity = profile["identity"]
    mapping = profile["mapping"]

    plan = []
    for entity_name, records in entities.items():
        db_id = databases.get(entity_name)
        if not db_id:
            continue

        id_fields = identity.get(entity_name, [])
        for record in records:
            identity_value = _build_identity_value(entity_name, record, id_fields)
            properties = _map_record(entity_name, record, mapping)
            plan.append(
                {
                    "entity": entity_name,
                    "database_id": db_id,
                    "identity": identity_value,
                    "properties": properties,
                }
            )

    return plan


def main():
    parser = argparse.ArgumentParser(description="Build Notion sync payload (dry-run).")
    parser.add_argument("--profile", required=True, help="Path to profile JSON")
    parser.add_argument("--input", required=True, help="Path to pipeline snapshot JSON")
    parser.add_argument("--output", help="Optional output file for generated payload")
    parser.add_argument("--dry-run", action="store_true", help="Print payload only")
    args = parser.parse_args()

    profile_path = Path(args.profile)
    input_path = Path(args.input)
    if not profile_path.exists():
        raise SystemExit(f"Profile not found: {profile_path}")
    if not input_path.exists():
        raise SystemExit(f"Snapshot not found: {input_path}")

    profile = _load_json(profile_path)
    snapshot = _load_json(input_path)
    _validate_profile(profile)
    plan = build_sync_plan(snapshot, profile)

    output = {
        "profile_name": profile["profile_name"],
        "schema_version": profile["schema_version"],
        "dry_run": True if args.dry_run else False,
        "items": plan,
    }

    payload = json.dumps(output, indent=2, ensure_ascii=True)
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload + "\n", encoding="utf-8")
    else:
        sys.stdout.write(payload + "\n")


if __name__ == "__main__":
    main()
