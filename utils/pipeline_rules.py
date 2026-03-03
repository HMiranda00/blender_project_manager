import re
from typing import Iterable, Optional, Tuple


def build_wip_prefix(project_prefix: str, shot_name: str, role_name: str) -> str:
    return f"{project_prefix}_{shot_name}_{role_name}_v"


def build_wip_filename(project_prefix: str, shot_name: str, role_name: str, version: int) -> str:
    return f"{build_wip_prefix(project_prefix, shot_name, role_name)}{version:03d}.blend"


def build_publish_filename(project_prefix: str, shot_name: str, role_name: str) -> str:
    return f"{project_prefix}_{shot_name}_{role_name}.blend"


def build_assembly_filename(project_prefix: str, shot_name: str) -> str:
    return f"{project_prefix}_{shot_name}_ASSEMBLY.blend"


def extract_wip_version(filename: str, prefix: str) -> Optional[int]:
    if not filename.startswith(prefix) or not filename.endswith(".blend"):
        return None

    match = re.search(r"_v(\d+)\.blend$", filename)
    if not match:
        return None

    try:
        return int(match.group(1))
    except ValueError:
        return None


def select_latest_wip(filenames: Iterable[str], prefix: str) -> Tuple[Optional[str], int]:
    latest_name = None
    latest_version = 0

    for filename in filenames:
        version = extract_wip_version(filename, prefix)
        if version is None:
            continue
        if version > latest_version:
            latest_version = version
            latest_name = filename

    return latest_name, latest_version


def resolve_publish_template(
    preset: str,
    custom_publish_path: str,
    placeholders: dict,
) -> str:
    if preset == "SHOTS":
        path_template = "{root}/SHOTS/{shot}/{role}/PUBLISH"
    elif preset == "CHARACTERS":
        path_template = "{root}/ASSETS 3D/CHR/{assetName}/PUBLISH"
    elif preset == "PROPS":
        path_template = "{root}/ASSETS 3D/PROPS/{assetName}/PUBLISH"
    elif preset == "CUSTOM":
        path_template = custom_publish_path or "{root}/SHOTS/{shot}/{role}/PUBLISH"
    else:
        path_template = "{root}/SHOTS/{shot}/{role}/PUBLISH"

    return path_template.format(**placeholders)
