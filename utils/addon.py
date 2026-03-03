import bpy

ADDON_ID = "blender_project_manager"


def get_addon_entry(context=None):
    if context is None:
        context = bpy.context

    addons = context.preferences.addons
    if ADDON_ID in addons:
        return addons[ADDON_ID]

    suffix = f".{ADDON_ID}"
    for key in addons.keys():
        if key.endswith(suffix):
            return addons[key]
    return None


def get_addon_preferences(context=None):
    addon = get_addon_entry(context)
    if addon is None:
        raise KeyError(f"Addon preferences not found for {ADDON_ID}")
    return addon.preferences
