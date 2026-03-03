"""Deprecated module.

Asset Browser toggle operator is now canonically implemented in
`operators.asset_browser_setup` to avoid duplicate bl_idname registration.
"""


def register():
    return None


def unregister():
    return None
